import unittest

from graph_optimizer import GraphOptimizer, create_directed_graph


class TestGraphOptimizer(unittest.TestCase):
    @staticmethod
    def _compute_degrees(nodes, edges):
        indegree = {node: 0 for node in nodes}
        outdegree = {node: 0 for node in nodes}
        for source, target in edges:
            outdegree[source] += 1
            indegree[target] += 1
        return indegree, outdegree

    def test_create_directed_graph_is_continuous(self):
        generated = create_directed_graph(size=14, complexity=3)
        self.assertEqual(len(generated.nodes), 14)
        self.assertGreater(len(generated.edges), 0)
        indegree, outdegree = self._compute_degrees(generated.nodes, generated.edges)
        entries = [node for node in generated.nodes if indegree[node] == 0]
        exits = [node for node in generated.nodes if outdegree[node] == 0]

        outgoing = {node: set() for node in generated.nodes}
        incoming = {node: set() for node in generated.nodes}
        for source, target in generated.edges:
            outgoing[source].add(target)
            incoming[target].add(source)

        forward_reachable = set()
        stack = list(entries)
        while stack:
            node = stack.pop()
            if node in forward_reachable:
                continue
            forward_reachable.add(node)
            stack.extend(outgoing[node] - forward_reachable)

        backward_reachable = set()
        stack = list(exits)
        while stack:
            node = stack.pop()
            if node in backward_reachable:
                continue
            backward_reachable.add(node)
            stack.extend(incoming[node] - backward_reachable)

        self.assertEqual(forward_reachable, set(generated.nodes))
        self.assertEqual(backward_reachable, set(generated.nodes))

    def test_create_directed_graph_has_multi_level_entries_and_exits(self):
        generated = create_directed_graph(size=16, complexity=4)
        indegree, outdegree = self._compute_degrees(generated.nodes, generated.edges)

        entries = [node for node in generated.nodes if indegree[node] == 0]
        exits = [node for node in generated.nodes if outdegree[node] == 0]
        entry_levels = {generated.levels[node] for node in entries}
        exit_levels = {generated.levels[node] for node in exits}

        self.assertGreaterEqual(len(entries), 2)
        self.assertGreaterEqual(len(exits), 2)
        self.assertGreaterEqual(len(entry_levels), 2)
        self.assertGreaterEqual(len(exit_levels), 2)

    def test_create_directed_graph_has_multi_parents_and_children(self):
        generated = create_directed_graph(size=18, complexity=4)
        indegree, outdegree = self._compute_degrees(generated.nodes, generated.edges)

        has_multi_parent = any(count > 1 for count in indegree.values())
        has_multi_child = any(count > 1 for count in outdegree.values())
        self.assertTrue(has_multi_parent)
        self.assertTrue(has_multi_child)

    def test_path_does_not_traverse_intermediate_node(self):
        optimizer = GraphOptimizer(width=3, height=2)
        result = optimizer.optimize(
            nodes=["A", "B", "C"],
            edges=[("A", "C")],
        )

        path = result.paths[("A", "C")]
        node_positions = result.positions
        self.assertEqual(path[0], node_positions["A"])
        self.assertEqual(path[-1], node_positions["C"])
        self.assertNotIn(node_positions["B"], path)

    def test_paths_do_not_cross_without_common_endpoints(self):
        optimizer = GraphOptimizer(width=3, height=3)
        result = optimizer.optimize(
            nodes=["A", "B", "C", "D"],
            edges=[("A", "D"), ("B", "C")],
        )

        path_ad = set(result.paths[("A", "D")])
        path_bc = set(result.paths[("B", "C")])
        intersections = path_ad & path_bc
        self.assertEqual(intersections, set())

    def test_paths_can_meet_on_common_destination_only(self):
        optimizer = GraphOptimizer(width=3, height=3)
        result = optimizer.optimize(
            nodes=["A", "B", "C"],
            edges=[("A", "C"), ("B", "C")],
        )

        path_ac = set(result.paths[("A", "C")])
        path_bc = set(result.paths[("B", "C")])
        intersections = path_ac & path_bc
        self.assertEqual(intersections, {result.positions["C"]})

    def test_paths_can_meet_on_common_source_only(self):
        optimizer = GraphOptimizer(width=3, height=3)
        result = optimizer.optimize(
            nodes=["A", "B", "C"],
            edges=[("A", "B"), ("A", "C")],
        )

        path_ab = set(result.paths[("A", "B")])
        path_ac = set(result.paths[("A", "C")])
        intersections = path_ab & path_ac
        self.assertEqual(intersections, {result.positions["A"]})


if __name__ == "__main__":
    unittest.main()
