import unittest

from graph_optimizer import GraphOptimizer


class GraphOptimizerTests(unittest.TestCase):
    def test_path_does_not_cross_unrelated_node(self):
        optimizer = GraphOptimizer(width=3, height=2)
        result = optimizer.optimize(
            nodes=["A", "B", "C"],
            edges=[("A", "C")],
        )

        path = result.paths[("A", "C")]
        node_positions = result.positions
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


if __name__ == "__main__":
    unittest.main()
