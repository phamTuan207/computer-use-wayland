"""Skeleton traversal and drill use the real adapter with fake AT-SPI nodes."""
import json
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest import mock

# Single-pass discover (shard children) may not have the repo
# root on sys.path yet; the package import below needs it.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
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

    def test_cut_flags_and_complete_accounting(self):
        out=self.a11y.observe(4242,skeleton=True)
        by_name={e['name']:e for e in out['elements']}
        # Depth limit (skeleton depth 3) cuts the container: its
        # child exists but was not walked.
        self.assertTrue(by_name['container'].get('cut'))
        self.assertEqual(by_name['container']['children_count'],1)
        # Fully walked nodes carry no cut flag.
        self.assertNotIn('cut',by_name['app'])
        self.assertNotIn('cut',by_name['frame'])
        self.assertNotIn('cut',by_name['panel'])
        self.assertTrue(out['truncated'])
        self.assertFalse(out['complete'])
        # Drill into the cut node: complete, no cut flags.
        expanded=self.a11y.drill(out['snapshot'],by_name['container']['ref'])
        self.assertTrue(expanded['complete'])
        self.assertFalse(expanded['truncated'])
        self.assertTrue(all('cut' not in e for e in expanded['elements']))
        self.assertEqual(expanded['elements'][-1]['children_count'],0)

    def test_read_failure_marks_snapshot_incomplete_at_root(self):
        bad=self.node('bad')
        bad.get_name.side_effect=RuntimeError('app hung')
        good=self.node('good')
        self.tree=self.node('app',[good,bad])
        self.a11y.applications=lambda: [self.tree]
        out=self.a11y.observe(4242,skeleton=True)
        # The unreadable node is dropped from elements but the
        # root marking says so: unknown, not absent (I15).
        self.assertEqual([e['name'] for e in out['elements']],['app','good'])
        self.assertEqual(out['read_errors'],1)
        self.assertTrue(out['incomplete'])
        self.assertFalse(out['complete'])
        self.assertFalse(out['truncated'])
        # The stored snapshot file carries the same marking.
        stored=json.loads(Path(out['snapshot']).read_text())
        self.assertTrue(stored['incomplete'])
        self.assertEqual(stored['read_errors'],1)

    def test_clean_walk_is_complete_with_zero_read_errors(self):
        out=self.a11y.observe(4242,skeleton=True)
        self.assertEqual(out['read_errors'],0)
        # This tree is depth-cut, so incomplete via truncated.
        self.assertTrue(out['incomplete'])
        expanded=self.a11y.drill(out['snapshot'],out['elements'][-1]['ref'])
        self.assertEqual(expanded['read_errors'],0)
        self.assertFalse(expanded['incomplete'])
        self.assertTrue(expanded['complete'])

    def test_children_count_present_in_default_mode(self):
        leaf=self.node('leaf')
        iface=mock.Mock()
        iface.get_n_actions.return_value=1
        iface.get_action_name.return_value='click'
        leaf.get_action_iface.return_value=iface
        parent=self.node('parent',[leaf])
        self.tree=self.node('app',[parent])
        self.a11y.applications=lambda: [self.tree]
        out=self.a11y.observe(4242)
        self.assertEqual([e['name'] for e in out['elements']],['leaf'])
        self.assertEqual(out['elements'][0]['children_count'],0)
        self.assertTrue(out['complete'])

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

    def test_eighty_item_cap_marks_incomplete_in_default_mode(self):
        # M7: 80 actionable children, the 80th still has unwalked children
        # and pending is empty. The cap must mark the snapshot incomplete.
        def actionable(name,children=()):
            e=self.node(name,children)
            iface=mock.Mock()
            iface.get_n_actions.return_value=1
            iface.get_action_name.return_value='click'
            e.get_action_iface.return_value=iface
            return e
        children=[actionable(str(i)) for i in range(79)]
        children.append(actionable('last',[self.node('g%d'%i) for i in range(5)]))
        self.tree=self.node('app',children)
        out=self.a11y.observe(4242)
        self.assertEqual(len(out['elements']),80)
        self.assertEqual(out['elements'][-1]['children_count'],5)
        self.assertTrue(out['truncated'])
        self.assertTrue(out['incomplete'])
        self.assertFalse(out['complete'])

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
