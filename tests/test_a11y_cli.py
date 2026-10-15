"""Semantic traversal routes remain read-only; malformed routes never reach GI."""
import contextlib
import io
import json
import sys
import unittest
from unittest.mock import patch
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import cu


class TraversalCli(unittest.TestCase):
    def call(self,args):
        with patch.object(cu,'environment',return_value={}),patch.object(cu,'check_cancel'), \
             patch.object(cu,'locked',return_value=contextlib.nullcontext()), \
             patch.object(cu,'require_session',side_effect=AssertionError('read-only traversal')), \
             patch.object(cu,'run_cancelable',return_value='{"ok":true}') as adapter, \
             patch.object(sys,'argv',['cu','a11y',*args]),contextlib.redirect_stdout(io.StringIO()):
            cu.main()
        return json.loads(adapter.call_args.kwargs['input'])

    def test_skeleton_and_drill_do_not_require_input_session(self):
        self.assertTrue(self.call(['observe','--pid','7','--skeleton'])['skeleton'])
        request=self.call(['drill','e3','--snapshot','snapshot'])
        self.assertEqual((request['operation'],request['ref'],request['snapshot']),('drill','e3','snapshot'))
        self.assertNotIn('skeleton',self.call(['observe','--pid','7']))

    def test_invalid_traversal_arguments_refuse_before_adapter(self):
        for args in (['drill','e1'],['drill','--snapshot','snapshot'],['observe','e1','--pid','7'],['apps','--skeleton']):
            with self.subTest(args=args),patch.object(cu,'run_cancelable') as adapter:
                with patch.object(cu,'environment',return_value={}),patch.object(cu,'check_cancel'), \
                     patch.object(sys,'argv',['cu','a11y',*args]),self.assertRaises(ValueError):
                    cu.main()
                adapter.assert_not_called()
