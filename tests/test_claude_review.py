import json
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

RUNNER = Path(__file__).resolve().parents[1] / 'skills/claude-consensus/scripts/review.py'

class ReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.packet = self.root / 'packet.txt'
        self.packet.write_text('Sanitized fixture: add returns subtraction.')
        cli = self.root / 'claude'
        cli.write_text('''#!/usr/bin/env python3
import json, os, sys, time
if '--version' in sys.argv:
    print('test-cli'); sys.exit(0)
args = sys.argv[1:]
assert args[args.index('--tools') + 1] == ''
assert '--safe-mode' in args and '--strict-mcp-config' in args
assert '--disable-slash-commands' in args and '--no-session-persistence' in args
assert json.loads(args[args.index('--mcp-config') + 1]) == {'mcpServers': {}}
assert sys.stdin.buffer.read() == bytes.fromhex(os.environ['PACKET_HEX'])
if os.environ.get('EXPECT_MODEL'): assert args[args.index('--model') + 1] == os.environ['EXPECT_MODEL']
if os.environ.get('SLEEP'): time.sleep(5)
print(os.environ['RESPONSE'])
sys.exit(int(os.environ.get('EXIT', '0')))
''')
        cli.chmod(0o755)
    def run_review(self, response, code=0, timeout=5, sleep=False, model=None):
        env = dict(os.environ, PATH=str(self.root) + os.pathsep + os.environ['PATH'], RESPONSE=response, EXIT=str(code), PACKET_HEX=self.packet.read_bytes().hex())
        if sleep: env['SLEEP'] = '1'
        if model: env['EXPECT_MODEL'] = model
        result = subprocess.run([sys.executable, str(RUNNER), '--packet', str(self.packet), '--output-dir', str(self.root/'results'), '--timeout', str(timeout)] + (['--model', model] if model else []), env=env, capture_output=True, text=True)
        attempt = Path(result.stdout.splitlines()[0])
        return result, attempt, json.loads((attempt/'status.json').read_text())
    def response(self, text, **kwargs):
        return json.dumps(dict(subtype='success', is_error=False, result=text, **kwargs))
    def test_consensus_and_no_overwrite(self):
        value = self.response('지적 없음\n판정: 합의', modelUsage={'test-model': {}})
        first, a, status = self.run_review(value)
        second, b, _ = self.run_review(value)
        self.assertEqual(first.returncode, 0)
        self.assertEqual(second.returncode, 0)
        self.assertNotEqual(a, b)
        self.assertTrue((a/'review.md').exists())
        self.assertEqual(status['cli_version'], 'test-cli')
        self.assertEqual(len(status['packet_sha256']), 64)
    def test_valid_disagreement_is_not_execution_permission(self):
        result, _, status = self.run_review(self.response('F-01 | 높음 | 정적확인 | wrong operator | use addition\n판정: 미합의'))
        self.assertEqual(result.returncode, 0)
        self.assertEqual(status['verdict'], '판정: 미합의')
    def test_rejects_errors_malformed_and_contradictory_results(self):
        for value, code in [('not json',0), ('[]',0), (self.response('지적 없음\n판정: 합의'),1), (self.response('arbitrary output'),0), (self.response('F-01 | 높음 | 정적확인 | bug | fix\n판정: 합의'),0), (json.dumps({'subtype':'error','is_error':True}),0)]:
            with self.subTest(value=value):
                result, attempt, status = self.run_review(value, code)
                self.assertEqual(result.returncode, 1)
                self.assertEqual(status['status'], 'failed')
                self.assertFalse((attempt/'review.md').exists())
                self.assertTrue((attempt/'raw.json').exists())
    def test_utf8_crlf_bytes_hash_and_model(self):
        data = '한글 검토\r\n원본 줄바꿈\r\n'.encode('utf-8')
        self.packet.write_bytes(data)
        result, attempt, status = self.run_review(self.response('지적 없음\n\n판정: 합의'), model='requested-model')
        self.assertEqual(result.returncode, 0)
        self.assertEqual((attempt/'packet.txt').read_bytes(), data)
        self.assertEqual(status['packet_sha256'], hashlib.sha256(data).hexdigest())
    def test_rejects_hidden_findings_and_tool_metadata(self):
        samples = [self.response('- F-01 | 높음 | 정적확인 | bug | fix\n지적 없음\n판정: 합의'),
                   self.response('F-01 | blocker | static | bug | fix\n판정: 합의'),
                   self.response('지적 없음\n판정: 합의', permission_denials=[{'tool_name':'Read'}]),
                   self.response('지적 없음\n판정: 합의', num_turns=2)]
        for value in samples:
            result, _, status = self.run_review(value)
            self.assertEqual(result.returncode, 1)
            self.assertEqual(status['status'], 'failed')
    def test_nonpositive_timeout_rejected_before_call(self):
        result = subprocess.run([sys.executable, str(RUNNER), '--packet', str(self.packet), '--output-dir', str(self.root/'results'), '--timeout', '0'], capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.root/'results').exists())
    def test_timeout_is_failure(self):
        result, _, status = self.run_review('{}', timeout=1, sleep=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn('timed out', status['error'])

if __name__ == '__main__':
    unittest.main()
