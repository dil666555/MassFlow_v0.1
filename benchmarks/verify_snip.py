"""Check SNIP parameters and three real Ultra spectra before timing."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import tempfile

from run import HERE, read_json, validate_campaign, write_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, default=HERE / "results" / "read-compute")
    args = parser.parse_args()
    cfg = read_json(HERE / "config.json")
    for name in ("OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
        os.environ[name] = "1"
    os.environ["NUMBA_NUM_THREADS"] = str(cfg["numba_threads"])
    run = args.run_dir.resolve()
    manifest = validate_campaign(run, cfg)
    case = next(c for c in cfg["cases"] if c["id"] == "snip")
    if not (case["python"]["m"] == case["numba"]["m"] == case["cardinal"]["width"] == 5
            and all(case[b]["decreasing"] is True for b in ("python", "numba", "cardinal"))):
        raise ValueError("All three SNIP windows must be 5 with decreasing=True")
    if manifest["inputs"]["ultra"]["min_spectrum_points"] < 11:
        raise ValueError("Ultra has a spectrum too short for a common maximum SNIP offset of 5")

    import numpy as np
    from pyimzml.ImzMLParser import ImzMLParser
    from massflow.preprocess.helper.baseline_correction_helper import baseline_corrector
    from massflow.preprocess.numba.numba_runtime import apply_numba_runtime

    apply_numba_runtime(override_workers=cfg["numba_threads"])
    data = ImzMLParser(manifest["inputs"]["ultra"]["path"])
    indices = sorted({0, len(data.coordinates) // 2, len(data.coordinates) - 1})
    spectra = [data.getspectrum(i)[1] for i in indices]
    data.m.close()
    script = '''
suppressPackageStartupMessages(library(Cardinal))
suppressPackageStartupMessages(library(jsonlite))
args <- commandArgs(trailingOnly=TRUE)
values <- fromJSON(args[[1]], simplifyVector=FALSE)
fun <- get(".reduceBaseline_fun", asNamespace("Cardinal"))$snip
results <- lapply(values, function(x) fun(as.numeric(unlist(x)), NULL, width=5L, decreasing=TRUE))
write_json(results, args[[2]], digits=NA, auto_unbox=FALSE)
'''
    checks = []
    with tempfile.TemporaryDirectory() as temporary:
        inputs, outputs = Path(temporary) / "input.json", Path(temporary) / "output.json"
        write_json(inputs, [s.tolist() for s in spectra])
        subprocess.run(["Rscript", "--vanilla", "-e", script, str(inputs), str(outputs)], check=True)
        references = read_json(outputs)
    for index, values, reference in zip(indices, spectra, references):
        python, _ = baseline_corrector(values, method="snip", m=5, decreasing=True,
                                       smooth="none", baseline_scale=1.0)
        numba, _ = baseline_corrector(values, method="snip_numba", m=5, decreasing=True,
                                      smooth="none", baseline_scale=1.0,
                                      lengths=np.array([values.size], dtype=np.int32))
        cardinal = np.asarray(reference, dtype=values.dtype)
        if not (np.allclose(python, cardinal, rtol=1e-6, atol=1e-6)
                and np.allclose(numba, cardinal, rtol=1e-6, atol=1e-6)):
            raise ValueError(f"SNIP numerical mismatch at spectrum {index}")
        checks.append({"spectrum_index": index, "points": values.size,
                       "python_cardinal_max_abs_diff": float(np.max(np.abs(python - cardinal))),
                       "numba_cardinal_max_abs_diff": float(np.max(np.abs(numba - cardinal)))})
    write_json(run / "snip-parameter-check.json", {
        "campaign_id": manifest["id"], "m_or_width": 5, "decreasing": True,
        "clipping_offsets": [5, 4, 3, 2, 1], "baseline_scale": 1.0,
        "clip_negative_to_zero": True, "smoothing": "none", "checks": checks,
        "rtol": 1e-6, "atol": 1e-6,
        "comparison_dtype": str(spectra[0].dtype),
        "scope": "Corrected intensities checked on three real spectra, outside benchmark timing.",
    })
    print("SNIP parameter/numerical check passed on", len(checks), "Ultra spectra", flush=True)


if __name__ == "__main__":
    main()
