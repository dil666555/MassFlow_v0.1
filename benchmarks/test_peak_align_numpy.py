"""Small correctness checks; no real dataset or performance measurements."""
import ast
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from peak_align_numpy import compute_reference, search_nearest_numpy


def test_nearest_ties_boundaries_and_missing_matches():
    actual = search_nearest_numpy(
        np.array([0.0, 1.0, 2.0, 3.0, 4.1]), np.array([1.0, 3.0]), 1.0,
    )
    np.testing.assert_array_equal(actual, [0, 0, 0, 1, -1])


def test_relative_tolerance_and_empty_targets():
    queries = np.array([100.0, 200.0, 0.0])
    np.testing.assert_array_equal(
        search_nearest_numpy(queries, np.array([101.0, 203.0]), 0.01, code=0),
        [0, -1, -1],
    )
    np.testing.assert_array_equal(search_nearest_numpy(queries, np.array([]), 1.0), [-1, -1, -1])


@pytest.mark.parametrize("clear_memory", [False, True])
def test_frequency_weighted_reference(clear_memory):
    spectra = [SimpleNamespace(mz_list=np.array(mz, dtype=float))
               for mz in ([100, 101, 104], [100, 102, 104])]

    class Input:
        ms = spectra
        cleared = 0

        def batch_generator(self, batch_size):
            yield [spectra[0]]
            yield [spectra[1]]

        def clear_batch_data_memory(self, batch):
            self.cleared += 1

    data = Input()
    reference, tolerance = compute_reference(
        data, binfun="min", binratio=2.0, units="mz", clear_memory=clear_memory,
    )
    # Counts 2/1/1 descend from m/z=100; the rise at 104 starts a new mode.
    np.testing.assert_allclose(reference, [100.75, 104.0])
    assert tolerance == 2.0
    assert data.cleared == (4 if clear_memory else 0)


def test_reference_module_has_no_numba_dependencies():
    tree = ast.parse(Path(__file__).with_name("peak_align_numpy.py").read_text())
    modules = [alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names]
    assert modules == ["numpy"]
    assert not any(isinstance(node, ast.ImportFrom) for node in ast.walk(tree))
