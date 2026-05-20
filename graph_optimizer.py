from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from itertools import permutations
from math import prod
from random import Random


Position = tuple[int, int]
Edge = tuple[str, str]
Path = list[Position]


@dataclass(frozen=True)
class OptimizationResult:
    positions: dict[str, Position]
    paths: dict[Edge, Path]
    total_length: int


class GraphOptimizer:
    def __init__(self, width: int, height: int) -> None:
        if width <= 0 or height <= 0:
            raise ValueError("Grid dimensions must be positive.")
        self.width = width
        self.height = height
        self._cells: list[Position] = [
            (x, y) for y in range(self.height) for x in range(self.width)
        ]

    def optimize(
        self,
        nodes: list[str],
        edges: list[Edge],
        *,
        max_layouts: int = 50_000,
        max_random_layouts: int = 3_000,
        seed: int = 0,
    ) -> OptimizationResult:
        if len(set(nodes)) != len(nodes):
            raise ValueError("Nodes must be unique.")
        for source, target in edges:
            if source not in nodes or target not in nodes:
                raise ValueError("Every edge endpoint must exist in nodes.")
        if len(nodes) > len(self._cells):
            raise ValueError("The grid does not have enough cells for all nodes.")

        best: OptimizationResult | None = None
        for layout in self._generate_layouts(
            nodes,
            max_layouts=max_layouts,
            max_random_layouts=max_random_layouts,
            seed=seed,
        ):
            routed = self._route_edges(layout, edges)
            if routed is None:
                continue
            paths, total = routed
            candidate = OptimizationResult(layout, paths, total)
            if best is None or candidate.total_length < best.total_length:
                best = candidate
        if best is None:
            raise ValueError("No valid layout found with the routing constraints.")
        return best

    def _generate_layouts(
        self,
        nodes: list[str],
        *,
        max_layouts: int,
        max_random_layouts: int,
        seed: int,
    ):
        n = len(nodes)
        permutation_count = prod(range(len(self._cells) - n + 1, len(self._cells) + 1))
        if permutation_count <= max_layouts:
            for picked_cells in permutations(self._cells, n):
                yield {node: picked_cells[i] for i, node in enumerate(nodes)}
            return

        random = Random(seed)
        initial_cells = self._cells[:]
        for _ in range(max_random_layouts):
            random.shuffle(initial_cells)
            picked = initial_cells[:n]
            yield {node: picked[i] for i, node in enumerate(nodes)}

    def _route_edges(
        self, positions: dict[str, Position], edges: list[Edge]
    ) -> tuple[dict[Edge, Path], int] | None:
        routed_paths: dict[Edge, Path] = {}
        total = 0
        node_cells = {position: node for node, position in positions.items()}
        ordered_edges = sorted(
            edges,
            key=lambda edge: (
                abs(positions[edge[0]][0] - positions[edge[1]][0])
                + abs(positions[edge[0]][1] - positions[edge[1]][1]),
                edge[0],
                edge[1],
            ),
        )

        def backtrack(index: int) -> bool:
            nonlocal total
            if index == len(ordered_edges):
                return True
            edge = ordered_edges[index]
            source, target = edge
            source_pos = positions[source]
            target_pos = positions[target]
            candidate_paths = self._find_shortest_paths(
                source_pos,
                target_pos,
                node_cells=node_cells,
                routed_paths=routed_paths,
                current_edge=edge,
            )
            for path in candidate_paths:
                routed_paths[edge] = path
                total += len(path) - 1
                if backtrack(index + 1):
                    return True
                total -= len(path) - 1
                del routed_paths[edge]
            return False

        if not backtrack(0):
            return None
        return routed_paths, total

    def _find_shortest_paths(
        self,
        source_pos: Position,
        target_pos: Position,
        *,
        node_cells: dict[Position, str],
        routed_paths: dict[Edge, Path],
        current_edge: Edge,
        max_candidates: int = 8,
    ) -> list[Path]:
        queue = deque([source_pos])
        distance: dict[Position, int] = {source_pos: 0}
        parents: dict[Position, list[Position]] = {source_pos: []}
        best_distance: int | None = None

        while queue:
            position = queue.popleft()
            step = distance[position]
            if best_distance is not None and step >= best_distance:
                continue
            for neighbor in self._neighbors(position):
                if not self._is_move_allowed(
                    neighbor,
                    target_pos,
                    node_cells=node_cells,
                    routed_paths=routed_paths,
                    current_edge=current_edge,
                ):
                    continue
                new_distance = step + 1
                known_distance = distance.get(neighbor)
                if known_distance is None:
                    distance[neighbor] = new_distance
                    parents[neighbor] = [position]
                    if neighbor == target_pos:
                        best_distance = new_distance
                    else:
                        queue.append(neighbor)
                elif known_distance == new_distance:
                    parents[neighbor].append(position)

        if target_pos not in distance:
            return []

        paths: list[Path] = []

        def build_paths(cursor: Position, path_suffix: list[Position]) -> None:
            if len(paths) >= max_candidates:
                return
            if cursor == source_pos:
                paths.append([source_pos] + path_suffix)
                return
            for parent in parents[cursor]:
                build_paths(parent, [cursor] + path_suffix)

        build_paths(target_pos, [])
        return paths

    def _is_move_allowed(
        self,
        position: Position,
        target_pos: Position,
        *,
        node_cells: dict[Position, str],
        routed_paths: dict[Edge, Path],
        current_edge: Edge,
    ) -> bool:
        if not self._in_bounds(position):
            return False
        if position in node_cells and position != target_pos:
            return False
        for edge, path in routed_paths.items():
            if position not in path:
                continue
            if not self._shared_endpoint_cell(current_edge, edge, position, node_cells):
                return False
        return True

    @staticmethod
    def _shared_endpoint_cell(
        edge_a: Edge,
        edge_b: Edge,
        position: Position,
        node_cells: dict[Position, str],
    ) -> bool:
        node = node_cells.get(position)
        if node is None:
            return False
        a_source, a_target = edge_a
        b_source, b_target = edge_b
        return node in {a_source, a_target} and node in {b_source, b_target}

    def _neighbors(self, position: Position):
        x, y = position
        return ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1))

    def _in_bounds(self, position: Position) -> bool:
        x, y = position
        return 0 <= x < self.width and 0 <= y < self.height
