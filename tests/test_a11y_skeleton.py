"""Skeleton traversal and drill use the real adapter with fake AT-SPI nodes."""
import json
from pathlib import Path
import tempfile
import time
import unittest
from unittest import mock
from tests import test_a11y


class SkeletonTests(unittest.TestCase):
    restore=test_a11y.A11yObserveFileTests.restore
    root=test_a11y.A11yObserveFileTests.root
    def setUp(self):
        test_a11y.A11yObserveFileTests.setUp(self)
        folder=self.enterContext(tempfile.TemporaryDirectory())
        self.a11y.STATE=Path(folder)
        self.a11y.prepare_state=lambda: None
        self.tree=self.node('app', [self.node('frame', [self.node('panel', [
            self.node('container', [self.node('target')])])])])
        self.a11y.applications=lambda: [self.tree]

    def node(self,name,children=()):
        e=self.root(name=name)
        e.get_action_iface.return_value=None
        e.get_child_count.return_value=len(children)
        e.get_child_at_index.side_effect=lambda i: children[i]
        return e

    def test_depth_three_container_keeps_count_path_and_drill_ref(self):
        out=self.a11y.observe(4242,skeleton=True)
        self.assertEqual([e['name'] for e in out['elements']],['app','frame','panel','container'])
        last=out['elements'][-1]
        self.assertEqual(last['path'],[0,0,0])
        self.assertEqual(last['children_count'],1)
        self.assertTrue(out['truncated'])
        expanded=self.a11y.drill(out['snapshot'],last['ref'])
        self.assertEqual([e['name'] for e in expanded['elements']],['container','target'])
        self.assertEqual(expanded['elements'][-1]['path'],[0,0,0,0])
        self.assertNotEqual(expanded['snapshot'],out['snapshot'])
        self.assertFalse(expanded['truncated'])
        # A second observation does not overwrite or silently rebind old refs.
        self.assertEqual(self.a11y.drill(out['snapshot'],last['ref'])['elements'][0]['name'],'container')

    def test_default_observe_still_filters_non_actionable_containers(self):
        out=self.a11y.observe(4242)
        self.assertEqual(out['elements'],[])
        self.assertFalse(out['truncated'])

    def test_drill_rejects_invalid_stale_changed_and_disabled_ref(self):
        out=self.a11y.observe(4242,skeleton=True)
        for ref in ('e999',None):
            with self.assertRaisesRegex(ValueError,'valid accessibility ref'):
                self.a11y.drill(out['snapshot'],ref)
        self.tree.get_name.return_value='replacement'
        with self.assertRaisesRegex(ValueError,'tree changed'):
            self.a11y.drill(out['snapshot'],'e1')
        self.tree.get_name.return_value='app'
        self.tree.get_state_set.return_value.contains.return_value=False
        self.tree.get_state_set.return_value.contains.side_effect=None
        with self.assertRaisesRegex(ValueError,'disabled'):
            self.a11y.drill(out['snapshot'],'e1')
        stored=json.loads(Path(out['snapshot']).read_text())
        stored['created']=time.time()-91
        Path(out['snapshot']).write_text(json.dumps(stored))
        with self.assertRaisesRegex(ValueError,'stale'):
            self.a11y.drill(out['snapshot'],'e1')

    def test_eighty_item_budget_retains_drill_ref_for_unvisited_children(self):
        self.tree=self.node('app',[self.node(str(i),[self.node('leaf')]) for i in range(100)])
        out=self.a11y.observe(4242,skeleton=True)
        self.assertEqual(len(out['elements']),80)
        self.assertTrue(out['truncated'])
        last=out['elements'][-1]
        self.assertEqual(last['children_count'],1)
        self.assertEqual(len(self.a11y.drill(out['snapshot'],last['ref'])['elements']),2)

    def test_two_second_budget_preserves_root_drill_ref(self):
        with mock.patch.object(self.a11y.time,'monotonic',side_effect=[0,0,3]):
            out=self.a11y.observe(4242,skeleton=True)
        self.assertEqual(len(out['elements']),1)
        self.assertTrue(out['truncated'])
        self.assertGreater(len(self.a11y.drill(out['snapshot'],'e1')['elements']),1)

    def test_out_of_range_path_does_not_resolve_another_node(self):
        out=self.a11y.observe(4242,skeleton=True)
        self.tree.get_child_at_index.side_effect=IndexError('gone')
        with self.assertRaises(IndexError):
            self.a11y.drill(out['snapshot'],'e2')

    def test_drill_depth_is_three_and_absolute_paths_stay_bounded(self):
        tree=self.node('leaf')
        for i in range(16):tree=self.node(str(i),[tree])
        self.tree=tree
        out=self.a11y.observe(4242,skeleton=True)
        for expected in (3,6,9,12):
            self.assertEqual(max(len(e['path']) for e in out['elements']),expected)
            self.assertTrue(out['truncated'])
            out=self.a11y.drill(out['snapshot'],out['elements'][-1]['ref'])
        self.assertEqual(len(out['elements']),1)
        self.assertEqual(len(out['elements'][0]['path']),12)

    def test_skeleton_actionable_ref_still_works_with_existing_act(self):
        self.tree.get_action_iface.return_value=self.tree
        self.tree.get_n_actions.return_value=1
        self.tree.get_action_name.return_value='click'
        self.tree.do_action.return_value=True
        out=self.a11y.observe(4242,skeleton=True)
        result=self.a11y.act(out['snapshot'],[{'type':'click','ref':'e1'}])
        self.assertTrue(result['ok'])
        self.assertEqual(result['completed'],1)
        self.tree.do_action.assert_called_once_with(0)
