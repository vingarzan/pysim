"""Test the Bash card-processing loop without a reader or physical SIMs."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[2] / 'pySim-imsi-prefix.sh'

# Stand in for the Python executable used for PC/SC waiting and pySim-shell.
# Each wait yields one card; after the supplied cards, simulate Ctrl+C.
FAKE_PYTHON = r'''
import json
import os
from pathlib import Path
import re
import sys

state_file = Path(os.environ['MOCK_STATE'])
state = json.loads(state_file.read_text())
args = sys.argv[1:]
if args[0] == '-':
    expected = 'false' if state['waits'] == 0 else 'true'
    assert args[2] == expected, (args, expected)
    state['waits'] += 1
    state_file.write_text(json.dumps(state))
    if state['waits'] > len(state['cards']):
        sys.exit(130)
    sys.exit(0)

card = state['cards'][state['waits'] - 1]
commands = [args[i+1] for i, arg in enumerate(args[:-1]) if arg == '-e']
output = next(command.split(' > ', 1)[1] for command in commands
              if command.startswith('read_binary_decoded > '))
writing = '-a' in args or '-A' in args
if writing:
    option = '-a' if '-a' in args else '-A'
    state['pins'].append(args[args.index(option) + 1])
    state['writes'].append(state['waits'])
    state_file.write_text(json.dumps(state))
    if card.get('auth_fail'):
        print('Authentication failed with secret ' + state['pins'][-1])
        sys.exit(2)
    imsi = re.search(r'"imsi":"([0-9]+)"', ' '.join(commands)).group(1)
    imsi = card.get('readback', imsi)
else:
    state['reads'].append(state['waits'])
    state_file.write_text(json.dumps(state))
    if card.get('read_fail'):
        # pySim-shell may report success despite individual command failures.
        sys.exit(0)
    imsi = card.get('imsi', '999700000192019')
Path(output).write_text(json.dumps({'imsi': imsi}))
'''


class TestImsiPrefixScript(unittest.TestCase):
    def run_script(self, cards, args, input_text=None):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fake = root / 'python'
            fake.write_text('#!' + sys.executable + '\n' + FAKE_PYTHON)
            fake.chmod(0o700)
            state_file = root / 'state.json'
            state_file.write_text(json.dumps(dict(cards=cards, waits=0, reads=[], writes=[], pins=[])))
            environment = dict(os.environ, PYSIM_PYTHON=str(fake), MOCK_STATE=str(state_file))
            result = subprocess.run(['bash', str(SCRIPT), *args], env=environment,
                                    input=input_text, text=True, capture_output=True, timeout=10)
            return result, json.loads(state_file.read_text())

    def test_two_swaps_then_interrupt(self):
        result, state = self.run_script([{}, {'imsi': '999700000192020'}],
                                        ['26201', '--adm1', '01234567'])
        self.assertEqual(result.returncode, 130, result.stderr)
        self.assertEqual(state['reads'], [1, 2])
        self.assertEqual(state['writes'], [1, 2])
        self.assertEqual(state['pins'], ['01234567', '01234567'])
        self.assertIn('Verified IMSI: 262010000192019', result.stdout)
        self.assertIn('Verified IMSI: 262010000192020', result.stdout)
        self.assertIn('Processed: 2; failed: 0', result.stdout)

    def test_adm1_prompt_is_fresh_for_each_card(self):
        result, state = self.run_script([{}, {}], ['26201'], '00001234\n87654321\n')
        self.assertEqual(result.returncode, 130, result.stderr)
        self.assertEqual(state['pins'], ['00001234', '87654321'])
        self.assertNotIn('00001234', result.stdout + result.stderr)

    def test_auth_failure_continues_without_retry(self):
        result, state = self.run_script([{'auth_fail': True}, {}],
                                        ['26201', '--adm1', '01234567'])
        self.assertEqual(result.returncode, 130, result.stderr)
        self.assertEqual(state['writes'], [1, 2])
        self.assertIn('Processed: 1; failed: 1', result.stdout)
        self.assertNotIn('01234567', result.stdout + result.stderr)

    def test_failed_card_cannot_reuse_previous_output(self):
        result, state = self.run_script([{}, {'read_fail': True}, {}],
                                        ['26201', '--adm1', '01234567'])
        self.assertEqual(result.returncode, 130, result.stderr)
        self.assertEqual(state['writes'], [1, 3])
        self.assertIn('Processed: 2; failed: 1', result.stdout)

    def test_dry_run_never_authenticates(self):
        result, state = self.run_script([{}, {}], ['26201', '--dry-run'])
        self.assertEqual(result.returncode, 130, result.stderr)
        self.assertEqual(state['reads'], [1, 2])
        self.assertEqual(state['pins'], [])
        self.assertEqual(state['writes'], [])

    def test_once_stops_after_one_card(self):
        result, state = self.run_script([{}, {}], ['26201', '--adm1', '01234567', '--once'])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(state['waits'], 1)
        self.assertEqual(state['writes'], [1])

    def test_once_returns_failure(self):
        result, state = self.run_script([{'auth_fail': True}],
                                        ['26201', '--adm1', '01234567', '--once'])
        self.assertEqual(result.returncode, 1)
        self.assertEqual(state['writes'], [1])

    def test_unchanged_card_is_skipped(self):
        result, state = self.run_script([{'imsi': '262010000192019'}, {}],
                                        ['26201', '--adm1', '01234567'])
        self.assertEqual(result.returncode, 130, result.stderr)
        self.assertEqual(state['writes'], [2])
        self.assertIn('no change needed', result.stdout)

    def test_failed_readback_continues_to_next_card(self):
        result, state = self.run_script([{'readback': '999700000192019'}, {}],
                                        ['26201', '--adm1', '01234567'])
        self.assertEqual(result.returncode, 130, result.stderr)
        self.assertEqual(state['writes'], [1, 2])
        self.assertIn('Verification failed', result.stderr)
        self.assertIn('Processed: 1; failed: 1', result.stdout)

    def test_six_digit_prefix_preserves_suffix(self):
        result, _ = self.run_script([{}], ['001001', '--adm1', '00001234', '--once'])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Verified IMSI: 001001000192019', result.stdout)


if __name__ == '__main__':
    unittest.main()
