#!/usr/bin/env python3
"""Reversibly hide/lock ISIM on sysmocom SJA5 cards for USIM IMS fallback.

SPDX-License-Identifier: GPL-2.0-or-later
"""

import argparse
import getpass
import json
import os
from pathlib import Path
import secrets
import sys
import time

from osmocom.utils import b2h, h2b
from pySim.app import init_card
from pySim.exceptions import SwMatchError
from pySim.global_platform import GpCardKeyset, GpRegistryRelatedData
from pySim.global_platform.scp import SCP02
from pySim.log import PySimLogger
from pySim.sysmocom_sja2 import EF_0348_KEY, SysmocomSJA5
from pySim.transport.pcsc import PcscSimLink
from pySim.ts_102_221 import CardProfileUICC, EF_DIR
from pySim.utils import dec_iccid


# Clear IMS/ePDG capabilities for fallback, preserving unrelated services such as
# ACDC, PS Data Off, 5GS, and the ordinary USIM SMS storage capability.
IMS_SERVICES = (93, 95, 104, 105, 106, 107, 109, 110, 111, 112, 114, 115, 120, 134)
IMS_FILES = {
    '6fe7': 'UICCIARI',
    '6ff3': 'ePDGId',
    '6ff4': 'ePDGSelection',
    '6ff5': 'ePDGIdEm',
    '6ff6': 'ePDGSelectionEm',
    '6ff7': 'FromPreferred',
    '6ff8': 'IMSConfigData',
    '6ffc': 'XCAPConfigData',
    '6ffe': 'MuDMiDConfigData',
}
ACTIVE = 'operational_activated'
INACTIVE = 'operational_deactivated'
ISD = 'a000000003000000'


class ToggleError(ValueError):
    """An actionable, credential-free diagnostic safe to show to the operator."""


def fallback_ust(raw):
    """Clear only the IMS-related UST bits represented in this file."""
    data = bytearray.fromhex(raw)
    for service in IMS_SERVICES:
        byte, bit = divmod(service - 1, 8)
        if byte < len(data):
            data[byte] &= ~(1 << bit)
    return data.hex()


def application_aid(record):
    """Decode the advertised application AID, ignoring unused records."""
    if not record or set(record.lower()) == {'f'}:
        return None
    template = EF_DIR().decode_record_hex(record)['application_template']
    aids = [b2h(item['application_id']) for item in template if 'application_id' in item]
    if len(aids) != 1:
        raise ToggleError('Ambiguous EF.DIR application record')
    return aids[0].lower()


def hidden_directory(records, aid):
    """Blank only the records advertising this exact ISIM application."""
    return ['ff' * (len(record) // 2) if application_aid(record) == aid else record
            for record in records]


def save_backup(path, state):
    """Exclusively create and flush a private backup before any configuration write."""
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'w') as stream:
        json.dump(state, stream, indent=2)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())


def default_backup(action, iccid):
    """Reuse the latest per-card snapshot so interrupted operations can resume."""
    root = Path(os.environ.get('XDG_STATE_HOME', Path.home() / '.local' / 'state'))
    if not root.is_absolute():
        raise ToggleError('XDG_STATE_HOME must be an absolute path')
    directory = root / 'pysim' / 'isim' / iccid
    candidates = list(directory.glob('before-disable-*.json'))
    if candidates:
        return max(candidates, key=lambda path: (path.stat().st_mtime_ns, path.name))
    if action == 'disable':
        return directory / f'before-disable-{time.time_ns()}.json'
    raise ToggleError('No saved backup for this card; supply --backup with its original disable backup')


def load_backup(path):
    """Read an existing backup without replacing it, including after partial failure."""
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        raise ToggleError('Cannot read a valid state backup; the existing file was left untouched') from None


def validate_backup(state, iccid):
    """Reject another card's backup and changes outside the restoration allowlist."""
    if state.get('version') != 1 or state.get('iccid') != iccid:
        raise ToggleError('Backup format or ICCID does not match this card')
    if not state.get('isim_aid', '').startswith('a0000000871004'):
        raise ToggleError('Backup has no ISIM AID')
    if not state.get('usim_aid', '').startswith('a0000000871002'):
        raise ToggleError('Backup has no USIM AID')
    if state.get('gp_state') not in ('selectable', 'personalized'):
        raise ToggleError('Backup does not describe an enabled ISIM application')
    records = state.get('dir_records', [])
    if not records or not any(application_aid(r) == state['isim_aid'] for r in records):
        raise ToggleError('Backup does not advertise its ISIM AID')
    bytes.fromhex(state['ust'])
    if set(state.get('files', {})) != set(IMS_FILES):
        raise ToggleError('Backup file list does not match the restoration allowlist')
    if any(value not in (ACTIVE, INACTIVE, 'absent') for value in state['files'].values()):
        raise ToggleError('Backup contains an unsupported file lifecycle')


class Card:
    """Strict pySIM operations: every selection/write must succeed before continuing."""

    def __init__(self, reader, iccid=None):
        self.link = PcscSimLink(argparse.Namespace(pcsc_dev=reader, pcsc_shared=False))
        try:
            self.rs, self.card = init_card(self.link)
            if self.rs is None or self.rs.identity['ATR'].lower() not in SysmocomSJA5._atrs:
                raise ToggleError('Only detected sysmocom SJA5 cards are supported')
            self.scc = self.rs.lchan[0].scc
            self.scc.select_file('3f00')
            self.iccid = dec_iccid(self.scc.read_binary('2fe2')[0])
            if not self.iccid or not self.iccid.isascii() or not self.iccid.isdecimal():
                raise ToggleError('Cannot read a valid ICCID from this card')
            if iccid is not None and self.iccid != iccid:
                raise ToggleError('ICCID mismatch; no authentication or write attempted')
        except BaseException:
            self.link.disconnect()
            raise

    def close(self):
        """Release the reader, including on failure."""
        self._adm_pin = None
        self.link.disconnect()

    def directory(self):
        """Read every EF.DIR record without touching other applications."""
        self.scc.select_file('3f00')
        raw, _ = self.scc.select_file('2f00')
        fcp = CardProfileUICC.decode_select_response(raw)
        count = fcp['file_descriptor']['num_of_rec']
        return [self.scc.read_record('2f00', n)[0] for n in range(1, count + 1)]

    def usim(self, aid):
        """Select the full, verified USIM AID."""
        self.scc.select_adf(aid)

    def file_state(self, aid, fid):
        """Read a USIM EF lifecycle, distinguishing absence from access failures."""
        self.usim(aid)
        try:
            raw, _ = self.scc.select_file(fid)
        except SwMatchError as error:
            if error.sw_actual == '6a82':
                return 'absent'
            raise
        fcp = CardProfileUICC.decode_select_response(raw)
        if fcp['file_descriptor']['file_descriptor_byte']['file_type'] != 'working_ef':
            raise ToggleError('Refusing to toggle a directory or unexpected file type')
        state = fcp['life_cycle_status_integer']
        if state not in (ACTIVE, INACTIVE):
            raise ToggleError('Unsupported lifecycle for USIM file ' + fid)
        return state

    def read_ust(self, aid):
        """Read the USIM service table."""
        self.usim(aid)
        return self.scc.read_binary('6f38')[0]

    def authenticate(self):
        """Verify ADM1 and establish SCP02 using on-card ISD keys only."""
        pin = os.environ.pop('PYSIM_ADM1', None)
        if pin is None:
            pin = getpass.getpass('ADM1: ')
        if not pin.isascii() or not pin.isdecimal() or not 1 <= len(pin) <= 8:
            raise ToggleError('ADM1 must contain 1 to 8 ASCII decimal digits')
        self._adm_pin = pin.encode().ljust(8, b'\xff')
        self.scc.select_file('3f00')
        self.verify_adm()
        self.scc.select_path(['3f00', 'a515'])
        raw, _ = self.scc.select_file('6f22')
        count = CardProfileUICC.decode_select_response(raw)['file_descriptor']['num_of_rec']
        keys = {}
        for index in range(1, count + 1):
            record = EF_0348_KEY().decode_record_hex(self.scc.read_record('6f22', index)[0], index)
            # On SJA5, security domain 0 / KVN 0x70 is the issuer SCP02 keyset.
            if record['security_domain'] == 0 and record['key_set_version'] == 0x70:
                info = record['key_len_and_type']
                if info['algorithm'] != 'des' or info['key_length'] != 16:
                    raise ToggleError('Unexpected ISD SCP02 key format')
                kind = info['key_type']
                if kind in keys:
                    raise ToggleError('Duplicate ISD SCP02 key type')
                keys[kind] = record['key']
        if set(keys) != {'kic', 'kid', 'kik'}:
            raise ToggleError('Cannot read a complete ISD SCP02 keyset; no writes attempted')
        self.scc.select_adf(ISD)
        scp = SCP02(card_keys=GpCardKeyset(0x70, keys['kic'], keys['kid'], keys['kik']))
        try:
            raw, _ = self.scc.send_apdu_checksw(b2h(scp.gen_init_update_apdu(secrets.token_bytes(8))))
            scp.parse_init_update_resp(h2b(raw))
            self.scc.send_apdu_checksw(b2h(scp.gen_ext_auth_apdu(0x01)))
        except Exception:
            raise ToggleError('SCP02 authentication failed; no retry or configuration write attempted') from None
        self.scc.scp = scp

    def verify_adm(self):
        """Verify the supplied PIN once per session without echoing it on failure."""
        try:
            self.scc.verify_chv(self.card._adm_chv_num, self._adm_pin)
        except Exception:
            raise ToggleError('ADM1 verification failed; no retry was attempted') from None

    def gp_state(self, aid):
        """Read the exact application's GlobalPlatform lifecycle with GET STATUS."""
        # authenticate() left ISD selected. SELECTing it again would invalidate
        # the card-side secure channel while retaining the host-side SCP state.
        data = '4f' + f'{len(aid) // 2:02x}' + aid
        raw, _ = self.scc.send_apdu_checksw('80f24002' + f'{len(data) // 2:02x}' + data + '00')
        entry = GpRegistryRelatedData()
        _, remainder = entry.from_tlv(h2b(raw))
        values = {key: value for item in entry.to_dict()['gp_registry_related_data'] for key, value in item.items()}
        if remainder or b2h(values['application_aid']).lower() != aid:
            raise ToggleError('Unexpected GlobalPlatform registry response')
        state = values['life_cycle_state']
        # LOCKED is a flag: SJA5 returns 0x87 for a locked SELECTABLE app.
        if isinstance(state, int) and state & 0x80:
            return 'locked'
        return state

    def set_gp_state(self, aid, state):
        """Lock or restore only this application, then verify the registry state."""
        value = {'locked': '83', 'selectable': '07', 'personalized': '0f'}[state]
        if self.gp_state(aid) == state:
            return
        self.scc.send_apdu_checksw('80f040' + value + f'{len(aid) // 2:02x}' + aid)
        if self.gp_state(aid) != state:
            raise ToggleError('Application lifecycle readback mismatch')

    def release_scp(self):
        """Reset out of the ISD context and reestablish ADM rights for UICC files."""
        self.scc.scp = None
        self.rs.reset()
        self.scc = self.rs.lchan[0].scc
        self.verify_adm()

    def write_directory(self, records):
        """Update and verify only changed EF.DIR records."""
        current = self.directory()
        if len(current) != len(records):
            raise ToggleError('EF.DIR record count mismatch')
        for n, (old, new) in enumerate(zip(current, records), 1):
            if old != new:
                self.scc.update_record('2f00', n, new, verify=True)

    def write_ust(self, aid, raw):
        """Write and read back the complete backed-up or masked service table."""
        self.usim(aid)
        self.scc.update_binary('6f38', raw, verify=True)

    def set_file_state(self, aid, fid, target):
        """Toggle a confirmed EF, never the last file left selected after a failure."""
        actual = self.file_state(aid, fid)
        if actual == target:
            return
        if actual == 'absent' or target == 'absent':
            raise ToggleError('File presence changed for ' + fid)
        if target == INACTIVE:
            self.scc.deactivate_file()
        else:
            self.usim(aid)
            self.scc.activate_file(fid)
        if self.file_state(aid, fid) != target:
            raise ToggleError('File lifecycle readback mismatch for ' + fid)


def snapshot(card):
    """Capture the exact state that disable is allowed to modify."""
    records = card.directory()
    aids = [application_aid(record) for record in records]
    usims = {aid for aid in aids if aid and aid.startswith('a0000000871002')}
    isims = {aid for aid in aids if aid and aid.startswith('a0000000871004')}
    if len(usims) != 1 or len(isims) != 1:
        raise ToggleError('Expected exactly one advertised USIM and ISIM; use the original backup to restore')
    usim = usims.pop()
    return {'version': 1, 'iccid': card.iccid, 'usim_aid': usim,
            'isim_aid': isims.pop(), 'dir_records': records, 'ust': card.read_ust(usim),
            'files': {fid: card.file_state(usim, fid) for fid in IMS_FILES}}


def restore_preflight(card, state):
    """Reject a stale backup if unrelated directory records or service bits changed."""
    validate_backup(state, card.iccid)
    current = card.directory()
    hidden = hidden_directory(state['dir_records'], state['isim_aid'])
    if len(current) != len(hidden) or any(now not in (old, off) for now, old, off in
                                        zip(current, state['dir_records'], hidden)):
        raise ToggleError('EF.DIR changed outside this toggle; refusing to overwrite it')
    now = bytes.fromhex(card.read_ust(state['usim_aid']))
    old = bytes.fromhex(state['ust'])
    masked = bytes.fromhex(fallback_ust(state['ust']))
    if len(now) != len(old) or any((a ^ b) & ~(b ^ c) for a, b, c in zip(now, old, masked)):
        raise ToggleError('Unrelated UST bits changed; refusing to overwrite them')
    for fid, lifecycle in state['files'].items():
        if (card.file_state(state['usim_aid'], fid) == 'absent') != (lifecycle == 'absent'):
            raise ToggleError('File presence changed for ' + fid)


def disable(card, backup, dry_run=False):
    """Back up, lock/hide ISIM and select USIM IMS fallback, failing closed."""
    resuming = backup.exists()
    if resuming:
        state = load_backup(backup)
        restore_preflight(card, state)
        print('Using the original backup; resuming or repeating the disable operation.')
    else:
        state = snapshot(card)
    print('ISIM:', state['isim_aid'])
    print('UST:', state['ust'], '->', fallback_ust(state['ust']))
    print('Plan: lock ISIM, hide its EF.DIR record(s), clear IMS UST bits, deactivate present IMS EFs.')
    for fid, lifecycle in state['files'].items():
        action = 'deactivate' if lifecycle == ACTIVE else 'preserve'
        print(f'  {fid} ({IMS_FILES[fid]}): {lifecycle}; {action}')
    if dry_run:
        print('Dry run: no authentication, backup creation or card writes.')
        return
    card.authenticate()
    current_gp = card.gp_state(state['isim_aid'])
    if resuming:
        if current_gp not in (state['gp_state'], 'locked'):
            raise ToggleError('ISIM lifecycle does not match the saved enabled or locked state')
    else:
        state['gp_state'] = current_gp
        validate_backup(state, card.iccid)
        save_backup(backup, state)
        print('Backup saved:', backup)
    print('Locking ISIM and verifying the application lifecycle...')
    card.set_gp_state(state['isim_aid'], 'locked')
    print('Resetting to UICC file access and verifying ADM1 for the new session...')
    card.release_scp()
    print('Updating EF.DIR...')
    card.write_directory(hidden_directory(state['dir_records'], state['isim_aid']))
    print('Updating USIM EF.UST...')
    card.write_ust(state['usim_aid'], fallback_ust(state['ust']))
    for fid, lifecycle in state['files'].items():
        if lifecycle == ACTIVE:
            print(f'Deactivating USIM {fid} ({IMS_FILES[fid]})...')
            card.set_file_state(state['usim_aid'], fid, INACTIVE)
    restore_preflight(card, state)
    print('Disabled ISIM; writes were read back. Reinsert the card or power-cycle the phone.')


def enable(card, backup, dry_run=False):
    """Restore the exact enabled state from this card's original disable backup."""
    state = load_backup(backup)
    restore_preflight(card, state)
    print('Plan: restore ISIM lifecycle, EF.DIR, UST and IMS EF lifecycles from', backup)
    if dry_run:
        print('Dry run: no authentication or card writes.')
        return
    card.authenticate()
    print('Restoring ISIM application lifecycle...')
    card.set_gp_state(state['isim_aid'], state['gp_state'])
    print('Resetting to UICC file access and verifying ADM1 for the new session...')
    card.release_scp()
    for fid, lifecycle in state['files'].items():
        if lifecycle != 'absent':
            card.set_file_state(state['usim_aid'], fid, lifecycle)
    card.write_ust(state['usim_aid'], state['ust'])
    card.write_directory(state['dir_records'])
    if snapshot(card) != {key: value for key, value in state.items() if key != 'gp_state'}:
        raise ToggleError('Restored state does not match the original backup')
    print('Restored the previous ISIM configuration; this does not provision empty IMS identities.')


def main():
    """Detect the card and choose its backup, retaining explicit identity/path overrides."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('disable', 'enable'))
    parser.add_argument('-p', '--reader', type=int, default=0)
    parser.add_argument('--iccid', help='Optional expected ICCID; otherwise detect the inserted card')
    parser.add_argument('--backup', type=Path, help='Override the automatic per-card backup path')
    parser.add_argument('--dry-run', action='store_true', help='Inspect and show the plan without authentication or writes')
    args = parser.parse_args()
    PySimLogger.setup(print)
    card = None
    try:
        card = Card(args.reader, args.iccid)
        backup = args.backup if args.backup is not None else default_backup(args.action, card.iccid)
        print('Card ICCID:', card.iccid)
        print('Backup:', backup)
        if args.action == 'disable' and args.backup is None and not args.dry_run:
            backup.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        operation = disable if args.action == 'disable' else enable
        operation(card, backup, args.dry_run)
    except KeyboardInterrupt:
        print('Interrupted. If writes began, restore using enable and the original backup.', file=sys.stderr)
        return 130
    except Exception as error:
        # Do not print exception bodies: reader/authentication errors can contain credentials or APDUs.
        if isinstance(error, ToggleError):
            detail = str(error)
        elif isinstance(error, SwMatchError):
            detail = f'card status {error.sw_actual}'
        else:
            detail = type(error).__name__
        print(f'Operation stopped: {detail}. No retry was made.', file=sys.stderr)
        print('Check ICCID, backup path, reader, ADM1 and file permissions. If writes began, use enable with the original backup.',
              file=sys.stderr)
        return 1
    finally:
        if card is not None:
            card.close()
    return 0


if __name__ == '__main__':
    sys.exit(main())
