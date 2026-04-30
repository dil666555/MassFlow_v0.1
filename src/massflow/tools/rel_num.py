from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

import numpy as np
from pyimzml.ImzMLParser import ImzMLParser

from massflow.tools.funs import is_valid_file


@dataclass(frozen=True, slots=True)
class SpectrumCountSummary:
    """Summary of total and deduplicated spectrum counts for one imzML dataset."""

    imzml_path: str
    total_spectra: int
    unique_spectra: int

    @property
    def duplicate_spectra(self) -> int:
        """Return the number of spectra removed by storage-level deduplication."""
        return self.total_spectra - self.unique_spectra


_STORAGE_KEY_DTYPE = np.dtype(
    [
        ("mz_offset", np.int64),
        ("mz_length", np.int32),
        ("intensity_offset", np.int64),
        ("intensity_length", np.int32),
    ]
)


def resolve_imzml_path(path: str | Path) -> Path:
    """Resolve user input to an existing non-empty `.imzML` file path."""
    candidate = Path(path).expanduser()

    if candidate.suffix.lower() == ".imzml" and is_valid_file(str(candidate)):
        return candidate

    if candidate.suffix:
        base_path = candidate.with_suffix("")
    else:
        base_path = candidate

    possible_paths = (
        Path(f"{base_path}.imzML"),
        Path(f"{base_path}.imzml"),
    )
    for possible_path in possible_paths:
        if is_valid_file(str(possible_path)):
            return possible_path

    raise FileNotFoundError(f"Cannot find a non-empty imzML file for input path: {path}")


def _as_array(values: Sequence[Any], dtype: np.dtype[Any]) -> np.ndarray:
    """Convert parser lists to NumPy arrays without changing logical values."""
    return np.asarray(values, dtype=dtype)


def build_spectrum_storage_keys(parser: Any) -> np.ndarray:
    """
    Build one structured storage key per spectrum.

    Two spectra are considered identical here only when both their mz array and
    intensity array point to the same `.ibd` offsets with the same element counts.
    """
    mz_offsets = _as_array(parser.mzOffsets, np.int64)
    mz_lengths = _as_array(parser.mzLengths, np.int32)
    intensity_offsets = _as_array(parser.intensityOffsets, np.int64)
    intensity_lengths = _as_array(parser.intensityLengths, np.int32)

    spectrum_count = int(intensity_offsets.size)
    expected_sizes = {
        spectrum_count,
        int(mz_offsets.size),
        int(mz_lengths.size),
        int(intensity_lengths.size),
    }
    if len(expected_sizes) != 1:
        raise ValueError(
            "Inconsistent imzML parser arrays: "
            f"mzOffsets={mz_offsets.size}, mzLengths={mz_lengths.size}, "
            f"intensityOffsets={intensity_offsets.size}, intensityLengths={intensity_lengths.size}."
        )

    keys = np.empty(spectrum_count, dtype=_STORAGE_KEY_DTYPE)
    keys["mz_offset"] = mz_offsets
    keys["mz_length"] = mz_lengths
    keys["intensity_offset"] = intensity_offsets
    keys["intensity_length"] = intensity_lengths
    return keys


def summarize_parser(parser: Any, *, imzml_path: str = "") -> SpectrumCountSummary:
    """Count all spectra and deduplicated spectra from an initialized ImzML parser."""
    storage_keys = build_spectrum_storage_keys(parser)
    total_spectra = int(storage_keys.size)
    unique_spectra = int(np.unique(storage_keys).size)
    return SpectrumCountSummary(
        imzml_path=imzml_path,
        total_spectra=total_spectra,
        unique_spectra=unique_spectra,
    )


def close_parser(parser: Any) -> None:
    """Best-effort cleanup for parser-backed file handles."""
    close_method = getattr(parser, "close", None)
    if callable(close_method):
        close_method()

    mmap_handle = getattr(parser, "m", None)
    if mmap_handle is not None and hasattr(mmap_handle, "close"):
        mmap_handle.close()


def summarize_imzml_file(path: str | Path) -> SpectrumCountSummary:
    """Open one imzML file and return total / unique spectrum counts."""
    imzml_path = resolve_imzml_path(path)
    parser = ImzMLParser(str(imzml_path))
    try:
        return summarize_parser(parser, imzml_path=str(imzml_path))
    finally:
        close_parser(parser)


def format_summary(summary: SpectrumCountSummary) -> str:
    """Render a human-readable summary."""
    return "\n".join(
        [
            f"imzML: {summary.imzml_path}",
            f"total_spectra: {summary.total_spectra}",
            f"unique_spectra: {summary.unique_spectra}",
            f"duplicate_spectra: {summary.duplicate_spectra}",
        ]
    )


def build_arg_parser() -> argparse.ArgumentParser:
    """Build CLI argument parser."""
    parser = argparse.ArgumentParser(
        description=(
            "Count spectra in one imzML dataset and deduplicate spectra that share the same "
            "mz/intensity storage positions in the paired .ibd file."
        )
    )
    parser.add_argument("path", help="Path to the .imzML file, .ibd file, or base file path.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entry point."""
    args = build_arg_parser().parse_args(argv)
    summary = summarize_imzml_file(args.path)
    print(format_summary(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
