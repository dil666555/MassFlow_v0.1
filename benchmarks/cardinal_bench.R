# Cardinal calls follow tests/new_mid_file_pipeline_cardinal.md on the original branch.
suppressPackageStartupMessages(library(Cardinal))
suppressPackageStartupMessages(library(jsonlite))

args <- commandArgs(trailingOnly = TRUE)
versions <- function() {
    pkgs <- c("Cardinal", "CardinalIO", "matter", "BiocParallel", "jsonlite")
    bp <- BiocParallel::bpparam()
    list(R = R.version.string, packages = setNames(
        lapply(pkgs, function(p) as.character(packageVersion(p))), pkgs
    ), parallel_backend = class(bp)[[1]], workers = BiocParallel::bpworkers(bp))
}
if (identical(args, "--probe")) {
    cat(toJSON(versions(), auto_unbox = TRUE), "\n")
    quit(save = "no")
}

job <- fromJSON(args[[1]], simplifyVector = FALSE)
cfg <- job$config
stage <- job$case$stage
kwargs <- job$case$cardinal

# As in the original script: read/convert and prepare picked data before timing.
x <- readImzML(job$input)
if (stage %in% c("pick", "align")) x <- as(x, "MSImagingArrays")
if (job$case$id == "reference") {
    mz_vec <- if (inherits(x, "MSImagingArrays")) mz(x)[[1]] else mz(x)
    kwargs$ref <- as.numeric(mz_vec[ceiling(length(mz_vec) / 2)])
}
if (stage == "align") {
    picked <- process(peakPick(
        x, width = 5, method = "quantile", SNR = 2.0,
        type = "height", nbins = 1, overlap = 0.5
    ))
}

run_operator <- function() {
    switch(stage,
        baseline = process(do.call(reduceBaseline, c(list(object = x), kwargs))),
        noise = process(do.call(Cardinal::smooth, c(list(x = x), kwargs))),
        normalization = process(do.call(Cardinal::normalize, c(list(object = x), kwargs))),
        pick = process(do.call(peakPick, c(list(object = x), kwargs))),
        align = process(do.call(peakAlign, c(list(object = picked), kwargs)))
    )
}

memory_marker <- function(name, round_number) {
    file.create(file.path(job$control, paste0(name, "-", round_number)))
    ack <- if (name == "ready") "go" else "collected"
    while (!file.exists(file.path(job$control, paste0(ack, "-", round_number)))) Sys.sleep(0.005)
    invisible(NULL)
}

elapsed <- numeric()
outputs <- list()
for (i in seq_len(cfg$warmup + cfg$rounds)) {
    measured <- i > cfg$warmup
    gc(full = TRUE)
    if (measured && job$mode == "memory") memory_marker("ready", i - cfg$warmup)
    seconds <- system.time(invisible(result <- run_operator()))[["elapsed"]]
    if (measured && job$mode == "memory") memory_marker("done", i - cfg$warmup)
    stopifnot(length(result) == job$expected_spectra)
    if (measured) {
        info <- list(spectra = length(result), output_storage = "Cardinal native result; no export")
        if (stage == "align") info$reference_length <- length(mz(result))
        elapsed <- c(elapsed, seconds)
        outputs[[length(outputs) + 1L]] <- info
    }
    rm(result)
}
write_json(list(elapsed_seconds = as.list(elapsed), outputs = outputs,
                parameters = kwargs, environment = versions()),
           job$output, auto_unbox = TRUE, pretty = TRUE, digits = NA)
