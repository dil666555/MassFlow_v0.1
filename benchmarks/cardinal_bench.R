# One Cardinal pipeline case; run.py supplies the JSON job and measures RSS.
suppressPackageStartupMessages(library(Cardinal))
suppressPackageStartupMessages(library(jsonlite))

args <- commandArgs(trailingOnly = TRUE)
versions <- function() {
    pkgs <- c("Cardinal", "CardinalIO", "matter", "BiocParallel", "jsonlite")
    list(R = R.version.string, packages = setNames(
        lapply(pkgs, function(p) as.character(packageVersion(p))), pkgs
    ))
}
if (identical(args, "--probe")) {
    cat(toJSON(versions(), auto_unbox = TRUE), "\n")
    quit(save = "no")
}

job <- fromJSON(args[[1]], simplifyVector = FALSE)
cfg <- job$config
stopifnot(cfg$cardinal_workers == 1L)
bp <- BiocParallel::SerialParam()
BiocParallel::register(bp, default = TRUE)
setCardinalBPPARAM(bp)
chunks <- list(chunksize = as.integer(cfg$batch_size))

memory_marker <- function(name, round_number) {
    file.create(file.path(job$control, paste0(name, "-", round_number)))
    ack <- if (name == "ready") "go" else "collected"
    while (!file.exists(file.path(job$control, paste0(ack, "-", round_number)))) Sys.sleep(0.005)
    invisible(NULL)
}

# ---------------------------------------------------------------------------
# Native Cardinal operator and streaming output
# ---------------------------------------------------------------------------
run_pipeline <- function(outfile) {
    x <- readImzML(job$input, memory = FALSE, verbose = FALSE, BPPARAM = bp)
    stage <- job$case$stage
    kwargs <- job$case$cardinal
    if (stage == "pick" || stage == "align") x <- as(x, "MSImagingArrays")
    if (job$case$id == "reference") kwargs$ref <- job$reference
    queued <- switch(stage,
        baseline = do.call(reduceBaseline, c(list(object = x), kwargs)),
        noise = do.call(Cardinal::smooth, c(list(x = x), kwargs)),
        normalization = do.call(Cardinal::normalize, c(list(object = x), kwargs)),
        pick = do.call(peakPick, c(list(object = x), kwargs)),
        align = do.call(peakAlign, c(list(object = x, verbose = FALSE,
                                        chunkopts = chunks, BPPARAM = bp), kwargs))
    )
    if (stage == "align") {
        # peakAlign returns a lazy sparse experiment with no queued processing.
        result <- queued
    } else {
        # Stream native intermediate chunks to disk, not a complete result in RAM.
        intermediate <- file.path(dirname(outfile), "intermediate.imzML")
        result <- process(queued, outfile = intermediate, verbose = FALSE,
                          chunkopts = chunks, BPPARAM = bp)
    }
    meta <- experimentData(result)
    meta$spectrumRepresentation <- if (stage %in% c("pick", "align")) {
        "centroid spectrum"
    } else "profile spectrum"
    experimentData(result) <- meta
    # Final output precision matches MassFlow. Both the native intermediate I/O
    # and this chunked export are part of Cardinal's end-to-end pipeline time.
    writeImzML(result, file = outfile, bundle = FALSE, verbose = FALSE,
               chunkopts = chunks, BPPARAM = bp,
               mz.type = "float64", intensity.type = "float32")
    info <- list(spectra = length(result))
    if (stage == "align") info$reference_length <- length(mz(result))
    info
}

elapsed <- numeric()
outputs <- list()
count <- as.integer(cfg$rounds)
dir.create(job$scratch, recursive = TRUE, showWarnings = FALSE)
for (i in seq_len(cfg$warmup + count)) {
    measured <- i > cfg$warmup
    tmp <- tempfile(pattern = "cardinal-", tmpdir = job$scratch)
    dir.create(tmp)
    outfile <- file.path(tmp, "output.imzML")
    gc(full = TRUE)
    if (measured && job$mode == "memory") memory_marker("ready", i - cfg$warmup)
    start <- proc.time()[["elapsed"]]
    info <- run_pipeline(outfile)
    seconds <- proc.time()[["elapsed"]] - start
    if (measured && job$mode == "memory") memory_marker("done", i - cfg$warmup)
    # Output validation, statistics and deletion are outside the timed/RSS region.
    stopifnot(info$spectra == job$expected_spectra,
              file.exists(outfile),
              file.exists(file.path(tmp, "output.ibd")))
    if (measured) {
        info$imzml_bytes <- file.info(outfile)$size
        info$ibd_bytes <- file.info(file.path(tmp, "output.ibd"))$size
        info$output_storage <- "CardinalIO export: float64 mz, float32 intensity"
        elapsed <- c(elapsed, seconds)
        outputs[[length(outputs) + 1L]] <- info
    }
    unlink(tmp, recursive = TRUE)
}
write_json(list(elapsed_seconds = as.list(elapsed), outputs = outputs,
                cardinal_workers = 1L, environment = versions()),
           job$output, auto_unbox = TRUE, pretty = TRUE, digits = NA)
