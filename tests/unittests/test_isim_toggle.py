"""Exercise reversible ISIM changes with a fake card, including partial failures."""

import contextlib
import copy
import importlib.util
import io
import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch


SPEC = importlib.util.spec_from_file_location('isim_toggle', Path(__file__).resolve().parents[2] / 'pySim-isim.py')
toggle = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(toggle)

USIM = 'a0000000871002ffffffff8907090000'
ISIM = 'a0000000871004ffffffff8907090000'
DIRECTORY = [
    '61194f10' + USIM + '50055553696d31' + 'ff' * 16,
    '61194f10' + ISIM + '50054953696d31' + 'ff' * 16,
    'ff' * 43,
]


class FakeCard:
    """Model the state the workflow may change and track authentication/write calls."""

    iccid = '8900000000000000000'

    def __init__(self):
        self.records = list(DIRECTORY)
        self.ust = 'ff' * 20
        self.files = dict.fromkeys(toggle.IMS_FILES, toggle.ACTIVE)
        self.files['6ff3'] = toggle.INACTIVE
        self.files['6fe7'] = 'absent'
        self.lifecycle = 'personalized'
        self.auth_count = 0
        self.writes = []

    def directory(self):
        return list(self.records)

    def read_ust(self, aid):
        assert aid == USIM
        return self.ust

    def file_state(self, aid, fid):
        assert aid == USIM
        return self.files[fid]

    def authenticate(self):
        self.auth_count += 1

    def gp_state(self, aid):
        assert aid == ISIM
        return self.lifecycle

    def set_gp_state(self, aid, state):
        assert aid == ISIM
        self.writes.append(('gp', state))
        self.lifecycle = state

    def release_scp(self):
        pass

    def write_directory(self, records):
        self.writes.append(('directory',))
        self.records = list(records)

    def write_ust(self, aid, raw):
        assert aid == USIM
        self.writes.append(('ust',))
        self.ust = raw

    def set_file_state(self, aid, fid, state):
        assert aid == USIM
        self.writes.append(('file', fid))
        self.files[fid] = state


class TestIsimToggle(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.backup = Path(self.directory.name) / 'backup.json'
        self.card = FakeCard()
        self.output = contextlib.redirect_stdout(io.StringIO())
        self.output.__enter__()
        self.addCleanup(self.output.__exit__, None, None, None)

    def test_round_trip_preserves_original_disabled_and_absent_files(self):
        original = copy.deepcopy(self.card.__dict__)
        toggle.disable(self.card, self.backup)
        self.assertEqual(self.card.lifecycle, 'locked')
        self.assertEqual(self.card.records, [DIRECTORY[0], 'ff' * 43, DIRECTORY[2]])
        self.assertEqual(self.card.ust, toggle.fallback_ust(original['ust']))
        self.assertEqual(self.backup.stat().st_mode & 0o777, 0o600)
        self.assertNotIn('key', self.backup.read_text())
        toggle.enable(self.card, self.backup)
        for name in ('records', 'ust', 'files', 'lifecycle'):
            self.assertEqual(getattr(self.card, name), original[name])
        self.assertEqual(self.card.auth_count, 2)

    def test_disable_dry_run_never_authenticates_writes_or_creates_backup(self):
        toggle.disable(self.card, self.backup, True)
        self.assertEqual(self.card.auth_count, 0)
        self.assertEqual(self.card.writes, [])
        self.assertFalse(self.backup.exists())

    def test_enable_dry_run_never_authenticates_or_writes(self):
        toggle.disable(self.card, self.backup)
        self.card.auth_count = 0
        self.card.writes.clear()
        toggle.enable(self.card, self.backup, True)
        self.assertEqual(self.card.auth_count, 0)
        self.assertEqual(self.card.writes, [])

    def test_existing_backup_is_never_overwritten(self):
        self.backup.write_text('original')
        with self.assertRaises(toggle.ToggleError):
            toggle.disable(self.card, self.backup)
        self.assertEqual(self.backup.read_text(), 'original')
        self.assertEqual(self.card.auth_count, 0)

    def test_authentication_failure_never_creates_backup_or_writes(self):
        self.card.authenticate = Mock(side_effect=toggle.ToggleError('Authentication failed'))
        with self.assertRaises(toggle.ToggleError):
            toggle.disable(self.card, self.backup)
        self.card.authenticate.assert_called_once()
        self.assertFalse(self.backup.exists())
        self.assertEqual(self.card.writes, [])

    def test_gp_failure_precedes_all_filesystem_writes_and_keeps_backup(self):
        self.card.set_gp_state = Mock(side_effect=toggle.ToggleError('GP operation failed'))
        with self.assertRaises(toggle.ToggleError):
            toggle.disable(self.card, self.backup)
        self.assertTrue(self.backup.exists())
        self.assertEqual(self.card.writes, [])

    def test_partial_disable_can_be_restored(self):
        original = copy.deepcopy(self.card.__dict__)
        self.card.set_file_state = Mock(side_effect=toggle.ToggleError('Removed card'))
        with self.assertRaises(toggle.ToggleError):
            toggle.disable(self.card, self.backup)
        del self.card.set_file_state
        toggle.enable(self.card, self.backup)
        for name in ('records', 'ust', 'files', 'lifecycle'):
            self.assertEqual(getattr(self.card, name), original[name])

    def test_wrong_iccid_backup_rejected_before_authentication(self):
        toggle.disable(self.card, self.backup)
        state = json.loads(self.backup.read_text())
        state['iccid'] = '8900000000000000001'
        self.backup.write_text(json.dumps(state))
        self.card.auth_count = 0
        self.card.writes.clear()
        with self.assertRaises(toggle.ToggleError):
            toggle.enable(self.card, self.backup)
        self.assertEqual(self.card.auth_count, 0)
        self.assertEqual(self.card.writes, [])

    def test_stale_backup_refuses_unrelated_service_changes(self):
        toggle.disable(self.card, self.backup)
        raw = bytearray.fromhex(self.card.ust)
        raw[0] ^= 1
        self.card.ust = raw.hex()
        self.card.auth_count = 0
        with self.assertRaises(toggle.ToggleError):
            toggle.enable(self.card, self.backup)
        self.assertEqual(self.card.auth_count, 0)

    def test_stale_backup_refuses_other_directory_changes(self):
        toggle.disable(self.card, self.backup)
        self.card.records[0] = 'ff' * 43
        self.card.auth_count = 0
        with self.assertRaises(toggle.ToggleError):
            toggle.enable(self.card, self.backup)
        self.assertEqual(self.card.auth_count, 0)

    def test_backup_cannot_target_arbitrary_files(self):
        state = toggle.snapshot(self.card)
        state['gp_state'] = 'selectable'
        state['files']['6f07'] = toggle.ACTIVE
        with self.assertRaises(toggle.ToggleError):
            toggle.validate_backup(state, self.card.iccid)

    def test_mask_preserves_sms_5gs_and_unrelated_capabilities(self):
        mask = bytes.fromhex(toggle.fallback_ust('ff' * 20))
        for service in range(1, 161):
            bit = bool(mask[(service - 1) // 8] & (1 << ((service - 1) % 8)))
            self.assertEqual(bit, service not in toggle.IMS_SERVICES)
        self.assertEqual(toggle.fallback_ust('ff'), 'ff')

    def test_select_failure_never_deactivates_last_selected_file(self):
        card = toggle.Card.__new__(toggle.Card)
        card.scc = Mock()
        card.file_state = Mock(side_effect=toggle.SwMatchError('6982', '9000'))
        with self.assertRaises(toggle.SwMatchError):
            card.set_file_state(USIM, '6ff3', toggle.INACTIVE)
        card.scc.deactivate_file.assert_not_called()

    def test_file_activation_selects_parent_first(self):
        card = toggle.Card.__new__(toggle.Card)
        card.file_state = Mock(side_effect=[toggle.INACTIVE, toggle.ACTIVE])
        calls = []
        card.usim = lambda aid: calls.append(('parent', aid))
        card.scc = SimpleNamespace(activate_file=lambda fid: calls.append(('activate', fid)))
        card.set_file_state(USIM, '6ff3', toggle.ACTIVE)
        self.assertEqual(calls, [('parent', USIM), ('activate', '6ff3')])

    def test_gp_commands_keep_the_authenticated_isd_selected(self):
        card = toggle.Card.__new__(toggle.Card)
        registry = 'e3194f10' + ISIM + '9f700183c50100'
        card.scc = Mock()
        enabled = 'e3194f10' + ISIM + '9f700107c50100'
        card.scc.send_apdu_checksw.side_effect = [(enabled, '9000'), ('', '9000'), (registry, '9000')]
        card.set_gp_state(ISIM, 'locked')
        card.scc.select_adf.assert_not_called()
        self.assertEqual(card.scc.send_apdu_checksw.call_args_list[1].args[0], '80f0408310' + ISIM)

    def test_gp_already_enabled_does_not_send_set_status(self):
        card = toggle.Card.__new__(toggle.Card)
        card.scc = Mock()
        card.scc.send_apdu_checksw.return_value = ('e3194f10' + ISIM + '9f700107c50100', '9000')
        card.set_gp_state(ISIM, 'selectable')
        card.scc.send_apdu_checksw.assert_called_once()
        self.assertTrue(card.scc.send_apdu_checksw.call_args.args[0].startswith('80f24002'))

    def test_unexpected_errors_do_not_echo_credential_material(self):
        self.card.authenticate = Mock(side_effect=RuntimeError('example-private-credential'))
        self.card.close = Mock()
        stderr = io.StringIO()
        argv = ['pySim-isim.py', 'disable', '--iccid', self.card.iccid, '--backup', str(self.backup)]
        with patch.object(toggle.sys, 'argv', argv), patch.object(toggle, 'Card', return_value=self.card):
            with contextlib.redirect_stderr(stderr), patch.object(toggle.PySimLogger, 'setup'):
                self.assertEqual(toggle.main(), 1)
        self.assertNotIn('example-private-credential', stderr.getvalue())
        self.card.close.assert_called_once()

    def test_bare_commands_round_trip_using_detected_card_and_automatic_backup(self):
        original = copy.deepcopy(self.card.__dict__)
        self.card.close = Mock()
        with patch.dict(os.environ, {'XDG_STATE_HOME': self.directory.name}):
            with patch.object(toggle, 'Card', return_value=self.card), patch.object(toggle.PySimLogger, 'setup'):
                with patch.object(toggle.sys, 'argv', ['pySim-isim.py', 'disable']):
                    self.assertEqual(toggle.main(), 0)
                backup = toggle.default_backup('enable', self.card.iccid)
                self.assertTrue(backup.is_file())
                self.assertEqual(backup.parent.name, self.card.iccid)
                self.assertEqual(backup.parent.stat().st_mode & 0o777, 0o700)
                with patch.object(toggle.sys, 'argv', ['pySim-isim.py', 'enable']):
                    self.assertEqual(toggle.main(), 0)
        for name in ('records', 'ust', 'files', 'lifecycle'):
            self.assertEqual(getattr(self.card, name), original[name])

    def test_bare_dry_run_does_not_create_state_directory(self):
        self.card.close = Mock()
        with patch.dict(os.environ, {'XDG_STATE_HOME': self.directory.name}):
            with patch.object(toggle, 'Card', return_value=self.card), patch.object(toggle.PySimLogger, 'setup'):
                with patch.object(toggle.sys, 'argv', ['pySim-isim.py', 'disable', '--dry-run']):
                    self.assertEqual(toggle.main(), 0)
        self.assertEqual(self.card.auth_count, 0)
        self.assertEqual(self.card.writes, [])
        self.assertFalse((Path(self.directory.name) / 'pysim').exists())

    def test_bare_enable_without_backup_does_not_authenticate(self):
        self.card.close = Mock()
        stderr = io.StringIO()
        with patch.dict(os.environ, {'XDG_STATE_HOME': self.directory.name}):
            with patch.object(toggle, 'Card', return_value=self.card), patch.object(toggle.PySimLogger, 'setup'):
                with patch.object(toggle.sys, 'argv', ['pySim-isim.py', 'enable']), contextlib.redirect_stderr(stderr):
                    self.assertEqual(toggle.main(), 1)
        self.assertIn('No saved backup for this card', stderr.getvalue())
        self.assertEqual(self.card.auth_count, 0)
        self.assertEqual(self.card.writes, [])

    def test_auto_restore_selects_latest_backup_for_current_card_only(self):
        with patch.dict(os.environ, {'XDG_STATE_HOME': self.directory.name}):
            first = toggle.default_backup('disable', self.card.iccid)
            first.parent.mkdir(parents=True)
            first.write_text('first')
            second = first.with_name('before-disable-newer.json')
            second.write_text('second')
            os.utime(first, ns=(1, 1))
            os.utime(second, ns=(2, 2))
            other = toggle.default_backup('disable', '8900000000000000001')
            other.parent.mkdir(parents=True)
            other.write_text('another card')
            self.assertEqual(toggle.default_backup('enable', self.card.iccid), second)
            self.assertEqual(toggle.default_backup('disable', self.card.iccid), second)

    def test_relative_state_directory_is_rejected(self):
        with patch.dict(os.environ, {'XDG_STATE_HOME': 'relative-directory'}):
            with self.assertRaises(toggle.ToggleError):
                toggle.default_backup('disable', self.card.iccid)

    def test_resume_after_real_world_lock_verification_failure(self):
        toggle.disable(self.card, self.backup)
        # The initial real-card failure happened just after the lock: filesystem
        # changes were still untouched, but the original backup was already saved.
        state = json.loads(self.backup.read_text())
        original_backup = self.backup.read_bytes()
        self.card.records = state['dir_records']
        self.card.ust = state['ust']
        self.card.files = state['files'].copy()
        toggle.disable(self.card, self.backup)
        self.assertEqual(self.card.lifecycle, 'locked')
        self.assertEqual(self.card.ust, toggle.fallback_ust(state['ust']))
        self.assertEqual(self.backup.read_bytes(), original_backup)
        self.assertEqual(self.card.records[1], 'ff' * 43)

    def test_repeated_disable_is_idempotent_and_preserves_backup(self):
        toggle.disable(self.card, self.backup)
        original_backup = self.backup.read_bytes()
        toggle.disable(self.card, self.backup)
        self.assertEqual(self.backup.read_bytes(), original_backup)
        toggle.enable(self.card, self.backup)
        self.assertEqual(self.card.records, DIRECTORY)

    def test_gp_locked_flag_accepts_sja5_selectable_and_personalized_states(self):
        for encoded in ('83', '87', '8f'):
            with self.subTest(encoded=encoded):
                card = toggle.Card.__new__(toggle.Card)
                card.scc = Mock()
                card.scc.send_apdu_checksw.return_value = ('e3194f10' + ISIM + '9f7001' + encoded + 'c50100', '9000')
                self.assertEqual(card.gp_state(ISIM), 'locked')

    def test_filesystem_transition_resets_before_reverifying_adm(self):
        card = toggle.Card.__new__(toggle.Card)
        old_scc = SimpleNamespace(scp=object())
        fresh_scc = SimpleNamespace(scp=None)
        card.scc = old_scc
        calls = []
        card.rs = SimpleNamespace(reset=lambda: calls.append('reset'), lchan={0: SimpleNamespace(scc=fresh_scc)})
        card.verify_adm = lambda: calls.append(('adm', card.scc))
        card.release_scp()
        self.assertIsNone(old_scc.scp)
        self.assertEqual(calls, ['reset', ('adm', fresh_scc)])


if __name__ == '__main__':
    unittest.main()
