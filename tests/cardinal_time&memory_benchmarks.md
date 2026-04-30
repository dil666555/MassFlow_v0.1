# Cardinal Time And Memory Benchmarks

Run these directly in R. They do not use Python or rpy2.

Common setup:

```r
library(Cardinal)

FILE_MIN <- "/Users/dre/Desktop/data/test_data_profile/file_min_profile/file_min_profile.imzML"
FILE_MID <- "/Users/dre/Desktop/data/test_data_profile/file_max_profile/file_max_profile.imzML"
FILE_MAX <- "/Users/dre/Desktop/data/Example_read/example.imzML"
FILE_ULTRA <- "/Users/dre/Desktop/data/original/original.imzML"
FILES <- c(min = FILE_MIN, mid = FILE_MID, max = FILE_MAX, ultra = FILE_ULTRA)
ROUNDS <- 3

bench_time <- function(label, expr, rounds = ROUNDS, warmup = 1) {
  expr <- substitute(expr)
  for (i in seq_len(warmup)) invisible(eval(expr, parent.frame()))
  elapsed <- numeric(rounds)
  for (i in seq_len(rounds)) {
    gc()
    elapsed[[i]] <- system.time(invisible(eval(expr, parent.frame())))[["elapsed"]]
  }
  data.frame(
    label = label,
    min = min(elapsed),
    mean = mean(elapsed),
    median = median(elapsed),
    max = max(elapsed),
    stddev = sd(elapsed),
    rounds = rounds
  )
}

bench_memory <- function(label, expr) {
  if (!requireNamespace("peakRAM", quietly = TRUE)) {
    stop("Install peakRAM first: install.packages('peakRAM')")
  }
  expr <- substitute(expr)
  eval_env <- parent.frame()
  gc(full = TRUE)
  result <- peakRAM::peakRAM({
    invisible(eval(expr, envir = eval_env))
  })
  gc(full = TRUE)
  cbind(label = label, result)
}

run_for_files <- function(fun) {
  do.call(rbind, lapply(names(FILES), function(dataset) {
    gc(full = TRUE)
    result <- fun(dataset, FILES[[dataset]])
    gc(full = TRUE)
    result
  }))
}

read_arrays <- function(file) {
  as(readImzML(file), "MSImagingArrays")
}
```

For memory benchmarks, restart the R session before running a new algorithm group if you need clean resident-memory numbers. R and Cardinal may keep heap pages, compiled code, or on-disk array caches after large runs; `gc(full = TRUE)` frees objects for reuse inside R but does not guarantee that RSS returns to the operating system.

## Baseline Correction

Time command:

```r
baseline_time <- rbind(
  run_for_files(function(dataset, file) {
    x <- readImzML(file)
    bench_time(paste(dataset, "locmin"), {
      process(reduceBaseline(x, method = "locmin", smooth = "none", span = 0.1, upper = FALSE))
    })
  }),
  run_for_files(function(dataset, file) {
    x <- readImzML(file)
    bench_time(paste(dataset, "snip"), {
      process(reduceBaseline(x, method = "snip", width = 5, decreasing = TRUE))
    })
  })
)
baseline_time
```

```r
baseline_time
       label     min     mean  median     max      stddev rounds
1 min locmin   2.780   2.9126   2.900   3.031  0.09557353      5
2 mid locmin   3.941   4.0224   4.034   4.055  0.04648441      5
3 max locmin 172.863 177.2970 175.882 184.245  4.55675844      5
4   min snip   1.621   1.7986   1.666   2.411  0.34315492      5
5   mid snip   2.317   2.4388   2.439   2.618  0.11737206      5
6   max snip 100.706 115.1436 112.062 126.531 10.71232184      5
```

```R
> baseline_time
         label     min       mean  median     max      stddev rounds
1   min locmin   2.802   2.887000   2.866   2.993  0.09721625      3
2   mid locmin   3.872   3.969667   3.894   4.143  0.15051357      3
3   max locmin 161.255 173.571333 163.851 195.608 19.12840329      3
4 ultra locmin  78.036  78.830333  78.457  79.998  1.03290577      3
5     min snip   1.629   1.696333   1.701   1.759  0.06512552      3
6     mid snip   2.159   2.493333   2.608   2.713  0.29426235      3
7     max snip  95.968 106.933000 106.639 118.192 11.11491660      3
8   ultra snip  47.851  48.830667  48.731  49.910  1.03311197      3
```

![image-20260428185333549](https://neonexus-picture.oss-ap-southeast-1.aliyuncs.com/test/image-20260428185333549.png)

![image-20260429142917681](https://neonexus-picture.oss-ap-southeast-1.aliyuncs.com/test/image-20260429142917681.png)

Memory command:

```r
baseline_memory <- rbind(
  run_for_files(function(dataset, file) {
      x <- readImzML(file)
      bench_memory(paste(dataset, "locmin"), {
          process(reduceBaseline(x, method = "locmin", smooth = "none", span = 0.1, upper = FALSE))
      })
  }),
  run_for_files(function(dataset, file) {
      x <- readImzML(file)
      bench_memory(paste(dataset, "snip"), {
          process(reduceBaseline(x, method = "snip", width = 5, decreasing = TRUE))
      })
  })
)
baseline_memory
```

```R
> baseline_memory
       label                          Function_Call Elapsed_Time_sec Total_RAM_Used_MiB Peak_RAM_Used_MiB
1 min locmin {invisible(eval(expr,envir=eval_env))}            5.097              408.0          84452778
2 mid locmin {invisible(eval(expr,envir=eval_env))}            7.072              665.9         125737201
3 max locmin {invisible(eval(expr,envir=eval_env))}          134.873             9795.4        2567841898
4   min snip {invisible(eval(expr,envir=eval_env))}            7.077              407.7         104922394
5   mid snip {invisible(eval(expr,envir=eval_env))}            6.068              665.8         128370683
6   max snip {invisible(eval(expr,envir=eval_env))}          108.955             9795.3        2567837141
```

```R
> baseline_memory
         label                          Function_Call Elapsed_Time_sec Total_RAM_Used_MiB Peak_RAM_Used_MiB
1   min locmin {invisible(eval(expr,envir=eval_env))}            5.092              407.9          82548434
2   mid locmin {invisible(eval(expr,envir=eval_env))}            7.283              665.9         130062630
3   max locmin {invisible(eval(expr,envir=eval_env))}          139.252             9795.4        2567841898
4 ultra locmin {invisible(eval(expr,envir=eval_env))}           82.526            10776.5        2008841587
5     min snip {invisible(eval(expr,envir=eval_env))}            3.267              407.7         115940482
6     mid snip {invisible(eval(expr,envir=eval_env))}            4.579              665.8         125356535
7     max snip {invisible(eval(expr,envir=eval_env))}          117.278             9795.3        2567837149
8   ultra snip {invisible(eval(expr,envir=eval_env))}           57.739            10776.5        1893013771
```

![image-20260428205653982](https://neonexus-picture.oss-ap-southeast-1.aliyuncs.com/test/image-20260428205653982.png)

![image-20260429144721453](https://neonexus-picture.oss-ap-southeast-1.aliyuncs.com/test/image-20260429144721453.png)

## Noise Reduction

Time command:

```r
noise_time <- rbind(
  run_for_files(function(dataset, file) {
    x <- readImzML(file)
    bench_time(paste(dataset, "ma"), {
      process(Cardinal::smooth(x, method = "ma", width = 5))
    })
  }),
  run_for_files(function(dataset, file) {
    x <- readImzML(file)
    bench_time(paste(dataset, "gaussian"), {
      process(Cardinal::smooth(x, method = "gaussian", width = 5))
    })
  }),
  run_for_files(function(dataset, file) {
    x <- readImzML(file)
    bench_time(paste(dataset, "savgol"), {
      process(Cardinal::smooth(x, method = "sgolay", width = 5, order = 3, deriv = 0, delta = 1.0))
    })
  })
)
noise_time
```

```R
> noise_time
         label     min     mean  median     max     stddev rounds
1       min ma   1.361   1.3920   1.378   1.478 0.04892341      5
2       mid ma   1.879   2.1038   2.129   2.253 0.15830256      5
3       max ma 154.559 162.9622 164.816 167.002 4.86670568      5
4 min gaussian   1.649   1.8700   1.721   2.493 0.35126770      5
5 mid gaussian   2.332   2.6660   2.700   2.827 0.20019116      5
6 max gaussian 127.747 141.9114 146.512 151.402 9.65215330      5
7   min savgol   1.923   2.0708   1.932   2.607 0.30011781      5
8   mid savgol   2.768   2.9116   2.913   3.007 0.10077103      5
9   max savgol 118.325 124.1374 126.113 126.712 3.50466622      5
```

```R
> noise_time
            label     min       mean  median     max       stddev rounds
1          min ma   1.591   1.640000   1.635   1.694  0.051681718      3
2          mid ma   2.109   2.154000   2.136   2.217  0.056204982      3
3          max ma 124.583 142.227333 147.678 154.421 15.647967482      3
4        ultra ma  63.919  66.829000  68.225  68.343  2.520824468      3
5    min gaussian   1.688   1.719333   1.705   1.765  0.040451617      3
6    mid gaussian   2.362   2.589000   2.590   2.815  0.226501656      3
7    max gaussian 135.630 141.495000 140.078 148.777  6.687063556      3
8  ultra gaussian  71.123  75.651000  76.519  79.311  4.162439669      3
9      min savgol   1.958   1.963000   1.965   1.966  0.004358899      3
10     mid savgol   2.803   3.157667   3.256   3.414  0.317147179      3
11     max savgol 106.937 117.427333 121.999 123.346  9.109825593      3
12   ultra savgol  72.066  73.261333  72.682  75.036  1.567464619      3
```

![image-20260428200051837](https://neonexus-picture.oss-ap-southeast-1.aliyuncs.com/test/image-20260428200051837.png)

![image-20260429153308814](https://neonexus-picture.oss-ap-southeast-1.aliyuncs.com/test/image-20260429153308814.png)

Memory command:

```r
noise_memory <- rbind(
  run_for_files(function(dataset, file) {
    x <- readImzML(file)
    bench_memory(paste(dataset, "ma"), {
      process(Cardinal::smooth(x, method = "ma", width = 5))
    })
  }),
  run_for_files(function(dataset, file) {
    x <- readImzML(file)
    bench_memory(paste(dataset, "gaussian"), {
      process(Cardinal::smooth(x, method = "gaussian", width = 5))
    })
  }),
  run_for_files(function(dataset, file) {
    x <- readImzML(file)
    bench_memory(paste(dataset, "savgol"), {
      process(Cardinal::smooth(x, method = "sgolay", width = 5, order = 3, deriv = 0, delta = 1.0))
    })
  })
)
noise_memory
```

```r
> noise_memory
            label                          Function_Call Elapsed_Time_sec Total_RAM_Used_MiB Peak_RAM_Used_MiB
1          min ma {invisible(eval(expr,envir=eval_env))}            3.778              407.9          65624051
2          mid ma {invisible(eval(expr,envir=eval_env))}            5.193              665.9         100929328
3          max ma {invisible(eval(expr,envir=eval_env))}           85.256             9795.3        2567841888
4        ultra ma {invisible(eval(expr,envir=eval_env))}           66.961            10776.4        1981084897
5    min gaussian {invisible(eval(expr,envir=eval_env))}            4.333              407.8         101965599
6    mid gaussian {invisible(eval(expr,envir=eval_env))}            4.808              665.8         125368524
7    max gaussian {invisible(eval(expr,envir=eval_env))}          100.053             9795.3        2567837143
8  ultra gaussian {invisible(eval(expr,envir=eval_env))}           70.877            10776.5        1853627463
9      min savgol {invisible(eval(expr,envir=eval_env))}            5.725              407.7         108816588
10     mid savgol {invisible(eval(expr,envir=eval_env))}            5.674              665.9         125366913
11     max savgol {invisible(eval(expr,envir=eval_env))}          106.815             9795.3        2567835386
12   ultra savgol {invisible(eval(expr,envir=eval_env))}           73.652            10776.5        1867232585
```

![image-20260429155032914](https://neonexus-picture.oss-ap-southeast-1.aliyuncs.com/test/image-20260429155032914.png)

## Normalization

Time command:

```r
normalization_time <- rbind(
  run_for_files(function(dataset, file) {
    x <- readImzML(file)
    bench_time(paste(dataset, "tic"), {
      process(Cardinal::normalize(x, method = "tic"))
    })
  }),
  run_for_files(function(dataset, file) {
    x <- readImzML(file)
    bench_time(paste(dataset, "rms"), {
      process(Cardinal::normalize(x, method = "rms"))
    })
  }),
  run_for_files(function(dataset, file) {
    x <- readImzML(file)
    
    # 兼容性修复：提取 m/z 向量
    # 如果是 MSImagingArrays (Processed 数据)，先提取第一个像素的 m/z 列表
    mz_vec <- if (inherits(x, "MSImagingArrays")) mz(x)[[1]] else mz(x)
    
    # 然后从向量中提取中间的数值作为 reference
    ref <- mz_vec[ceiling(length(mz_vec) / 2)]
    
    bench_time(paste(dataset, "reference"), {
        process(Cardinal::normalize(x, method = "reference", ref = ref))
    })
	})
)
normalization_time
```

```R
> normalization_time
             label     min       mean  median     max      stddev rounds
1          min tic   1.278   1.338000   1.361   1.375  0.05243091      3
2          mid tic   1.544   1.585667   1.555   1.658  0.06288349      3
3          max tic 143.328 158.211667 162.977 168.330 13.16458516      3
4        ultra tic  46.621  47.315667  47.150  48.176  0.79062654      3
5          min rms   1.200   1.233000   1.248   1.251  0.02861818      3
6          mid rms   1.596   1.825333   1.934   1.946  0.19869910      3
7          max rms 147.646 153.117000 147.980 163.725  9.18831524      3
8        ultra rms  55.769  56.277667  55.858  57.206  0.80519087      3
9    min reference   1.244   1.293000   1.303   1.332  0.04484417      3
10   mid reference   1.628   1.879667   1.958   2.053  0.22306576      3
11   max reference 113.625 119.599333 114.119 131.054  9.92310689      3
12 ultra reference  38.724  39.299667  39.405  39.770  0.53089578      3
```

![image-20260429171835873](https://neonexus-picture.oss-ap-southeast-1.aliyuncs.com/test/image-20260429171835873.png)

Memory command:

```r
normalization_memory <- rbind(
  run_for_files(function(dataset, file) {
    x <- readImzML(file)
    bench_memory(paste(dataset, "tic"), {
      process(Cardinal::normalize(x, method = "tic"))
    })
  }),
  run_for_files(function(dataset, file) {
    x <- readImzML(file)
    bench_memory(paste(dataset, "rms"), {
      process(Cardinal::normalize(x, method = "rms"))
    })
  }),
  run_for_files(function(dataset, file) {
    x <- readImzML(file)
    mz_vec <- if (inherits(x, "MSImagingArrays")) mz(x)[[1]] else mz(x)
    ref <- mz_vec[ceiling(length(mz_vec) / 2)]
    bench_memory(paste(dataset, "reference"), {
      process(Cardinal::normalize(x, method = "reference", ref = ref))
    })
  })
)
normalization_memory
```

```
> normalization_memory
             label                          Function_Call Elapsed_Time_sec Total_RAM_Used_MiB Peak_RAM_Used_MiB
1          min tic {invisible(eval(expr,envir=eval_env))}            3.419              407.9          72499978
2          mid tic {invisible(eval(expr,envir=eval_env))}            4.593              665.9         116392614
3          max tic {invisible(eval(expr,envir=eval_env))}          100.774             9795.3        2567841898
4        ultra tic {invisible(eval(expr,envir=eval_env))}           55.342            10776.5        1838298649
5          min rms {invisible(eval(expr,envir=eval_env))}            2.723              407.8         129310619
6          mid rms {invisible(eval(expr,envir=eval_env))}            4.113              665.8         125368309
7          max rms {invisible(eval(expr,envir=eval_env))}          105.091             9795.3        2567837144
8        ultra rms {invisible(eval(expr,envir=eval_env))}           60.855            10776.5        2017693389
9    min reference {invisible(eval(expr,envir=eval_env))}            3.285              407.7         105024485
10   mid reference {invisible(eval(expr,envir=eval_env))}            4.487              665.9         125367906
11   max reference {invisible(eval(expr,envir=eval_env))}          113.426             9795.3        2567835374
12 ultra reference {invisible(eval(expr,envir=eval_env))}           54.215            10776.4        1769794793
```

![image-20260429183814520](https://neonexus-picture.oss-ap-southeast-1.aliyuncs.com/test/image-20260429183814520.png)

## Peak Pick

Time command:

```r
pick_time <- rbind(
  run_for_files(function(dataset, file) {
    x <- read_arrays(file)
    bench_time(paste(dataset, "quantile"), {
      process(peakPick(x, width = 5, method = "quantile", SNR = 2.0, type = "height", nbins = 1, overlap = 0.5))
    })
  }),
  run_for_files(function(dataset, file) {
    x <- read_arrays(file)
    bench_time(paste(dataset, "diff"), {
      process(peakPick(x, width = 5, method = "diff", SNR = 2.0, type = "height", nbins = 1, overlap = 0.5))
    })
  }),
  run_for_files(function(dataset, file) {
    x <- read_arrays(file)
    bench_time(paste(dataset, "sd"), {
      process(peakPick(x, width = 5, method = "sd", SNR = 2.0, type = "height", nbins = 1, overlap = 0.5))
    })
  }),
  run_for_files(function(dataset, file) {
    x <- read_arrays(file)
    bench_time(paste(dataset, "mad"), {
      process(peakPick(x, width = 5, method = "mad", SNR = 2.0, type = "height", nbins = 1, overlap = 0.5))
    })
  })
)
pick_time
```

```
> pick_time
            label     min       mean  median     max     stddev rounds
1    min quantile   5.219   5.351667   5.407   5.429 0.11541808      3
2    mid quantile   7.531   7.737000   7.836   7.844 0.17844607      3
3    max quantile  56.790  57.079667  57.158  57.291 0.25952328      3
4  ultra quantile  87.813  87.882667  87.854  87.981 0.08759186      3
5        min diff   3.122   3.184667   3.162   3.270 0.07655935      3
6        mid diff   5.822   6.096000   6.025   6.441 0.31554873      3
7        max diff  32.728  32.793333  32.764  32.888 0.08393648      3
8      ultra diff  59.485  59.712333  59.746  59.906 0.21250961      3
9          min sd   3.918   3.964667   3.921   4.055 0.07824534      3
10         mid sd   7.001   7.310333   7.010   7.920 0.52800600      3
11         max sd  53.188  54.422333  53.784  56.295 1.64892824      3
12       ultra sd  78.463  78.691667  78.723  78.889 0.21472153      3
13        min mad   5.217   5.273667   5.231   5.373 0.08630952      3
14        mid mad   8.963   9.499000   9.100  10.434 0.81262599      3
15        max mad  77.793  78.969333  79.325  79.790 1.04492887      3
16      ultra mad 105.276 105.347000 105.359 105.406 0.06582553      3
```

![image-20260429195919663](https://neonexus-picture.oss-ap-southeast-1.aliyuncs.com/test/image-20260429195919663.png)

Memory command:

```r
pick_memory <- rbind(
  run_for_files(function(dataset, file) {
    x <- read_arrays(file)
    bench_memory(paste(dataset, "quantile"), {
      process(peakPick(x, width = 5, method = "quantile", SNR = 2.0, type = "height", nbins = 1, overlap = 0.5))
    })
  }),
  run_for_files(function(dataset, file) {
    x <- read_arrays(file)
    bench_memory(paste(dataset, "diff"), {
      process(peakPick(x, width = 5, method = "diff", SNR = 2.0, type = "height", nbins = 1, overlap = 0.5))
    })
  }),
  run_for_files(function(dataset, file) {
    x <- read_arrays(file)
    bench_memory(paste(dataset, "sd"), {
      process(peakPick(x, width = 5, method = "sd", SNR = 2.0, type = "height", nbins = 1, overlap = 0.5))
    })
  }),
  run_for_files(function(dataset, file) {
    x <- read_arrays(file)
    bench_memory(paste(dataset, "mad"), {
      process(peakPick(x, width = 5, method = "mad", SNR = 2.0, type = "height", nbins = 1, overlap = 0.5))
    })
  })
)
pick_memory
```

```R
> pick_memory
            label                          Function_Call Elapsed_Time_sec Total_RAM_Used_MiB Peak_RAM_Used_MiB
1    min quantile {invisible(eval(expr,envir=eval_env))}            6.927               12.2          19312738
2    mid quantile {invisible(eval(expr,envir=eval_env))}           10.003               18.7          24689882
3    max quantile {invisible(eval(expr,envir=eval_env))}           61.674              890.4         269680595
4  ultra quantile {invisible(eval(expr,envir=eval_env))}           87.956              294.1         307169132
5        min diff {invisible(eval(expr,envir=eval_env))}            4.652               14.8          58598545
6        mid diff {invisible(eval(expr,envir=eval_env))}            8.326               21.2          24907530
7        max diff {invisible(eval(expr,envir=eval_env))}           37.830              240.6         160501269
8      ultra diff {invisible(eval(expr,envir=eval_env))}           60.320              350.8         316449307
9          min sd {invisible(eval(expr,envir=eval_env))}            5.299               12.9          60543012
10         mid sd {invisible(eval(expr,envir=eval_env))}            9.422               16.6          25863431
11         max sd {invisible(eval(expr,envir=eval_env))}           59.115             3032.9         735044849
12       ultra sd {invisible(eval(expr,envir=eval_env))}           79.551              157.4         291756098
13        min mad {invisible(eval(expr,envir=eval_env))}            6.772               55.9          55364866
14        mid mad {invisible(eval(expr,envir=eval_env))}           11.203               90.7          37175903
15        max mad {invisible(eval(expr,envir=eval_env))}           81.263             3449.7         776659948
16      ultra mad {invisible(eval(expr,envir=eval_env))}          106.644             1485.4         586152652
```

![image-20260429201256112](https://neonexus-picture.oss-ap-southeast-1.aliyuncs.com/test/image-20260429201256112.png)

## Peak Align

Time command:

```r
align_time <- run_for_files(function(dataset, file) {
  x <- read_arrays(file)
  picked <- process(peakPick(x, width = 5, method = "quantile", SNR = 2.0, type = "height", nbins = 1, overlap = 0.5))
  bench_time(paste(dataset, "ppm"), {
    process(peakAlign(picked, units = "ppm", binfun = "median", binratio = 2.0))
  })
})
align_time
```

```R
> align_time
      label    min      mean median    max     stddev rounds
1   min ppm  1.999  2.039667  2.009  2.111 0.06197849      3
2   mid ppm  2.770  2.813333  2.772  2.898 0.07333030      3
3   max ppm 11.265 11.354667 11.360 11.439 0.08712252      3
4 ultra ppm 18.840 18.889333 18.897 18.931 0.04598188      3
```

![image-20260429202147166](https://neonexus-picture.oss-ap-southeast-1.aliyuncs.com/test/image-20260429202147166.png)

Memory command:

```r
align_memory <- run_for_files(function(dataset, file) {
  x <- read_arrays(file)
  picked <- process(peakPick(x, width = 5, method = "quantile", SNR = 2.0, type = "height", nbins = 1, overlap = 0.5))
  bench_memory(paste(dataset, "ppm"), {
    process(peakAlign(picked, units = "ppm", binfun = "median", binratio = 2.0))
  })
})
align_memory
```

```R
> align_memory
      label                          Function_Call Elapsed_Time_sec Total_RAM_Used_MiB Peak_RAM_Used_MiB
1   min ppm {invisible(eval(expr,envir=eval_env))}            2.020                0.2           7573175
2   mid ppm {invisible(eval(expr,envir=eval_env))}            2.792                0.1          21204119
3   max ppm {invisible(eval(expr,envir=eval_env))}           11.379                0.2         163767478
4 ultra ppm {invisible(eval(expr,envir=eval_env))}           18.863                0.1          80068620
```

![image-20260429202832203](https://neonexus-picture.oss-ap-southeast-1.aliyuncs.com/test/image-20260429202832203.png)
