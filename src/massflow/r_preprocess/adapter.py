from massflow.module import MassSpectrumSet
from massflow.data_manager import MSDataManagerImzML
from massflow.r_preprocess.environment import REnvironment
from massflow.tools.imzml_monkey_patch import risky_imzml_loader
from massflow.tools.logger import get_logger

logger = get_logger("massflow.r_preprocess")

class CardinalAdapter:
    """
    Preprocessing adapter, calling the R language Cardinal package for data preprocessing.
    """
    @staticmethod
    def baseline_reduction(data_manager: MSDataManagerImzML,
                           method: str = "locmin",
                           smooth: str = "none",
                           span: float = 0.1,
                           upper: bool = False,
                           width: int | None = None,
                           decreasing: bool = True,
                           temp_dir: str = "./temp_baseline_data"
                           ) -> None:
        """
        Call Cardinal::reduceBaseline for baseline correction.
        """
        r_env = REnvironment()

        ms_cardinal = MassSpectrumSet()
        dm_cardinal = MSDataManagerImzML(ms_cardinal, temp_dir=temp_dir)
        dm_cardinal.copy_meta(data_manager)

        cardinal_method = method.strip().lower().removesuffix("_numba")
        logger.info(f"Starting baseline reduction using Cardinal::reduceBaseline(method={cardinal_method})")

        r_massdata = r_env.cardinal.readImzML(data_manager.imzml_filepath) # type: ignore

        kwargs = {"method": cardinal_method}
        if cardinal_method == "locmin":
            kwargs.update({
                "smooth": smooth,
                "span": span,
                "upper": upper,
            })
        elif cardinal_method == "snip":
            if width is not None:
                kwargs["width"] = int(width)
            kwargs["decreasing"] = decreasing
        elif cardinal_method in {"median", "med"}:
            kwargs["method"] = "median"
            if width is not None:
                kwargs["width"] = int(width)
        elif cardinal_method == "hull":
            kwargs["upper"] = upper

        processed = r_env.robjects.r["process"](
            r_env.cardinal.reduceBaseline(r_massdata, **kwargs) # type: ignore
        )
        _ = processed

    @staticmethod
    def noise_reduction(data_manager: MSDataManagerImzML,
                        method: str = "ma",
                        window: int = 5,
                        sd: float | None = None,
                        polyorder: int = 3,
                        deriv: int = 0,
                        delta: float = 1.0,
                        temp_dir: str = "./temp_noise_data"
                        ) -> None:
        """
        Call Cardinal::smooth for spectral smoothing/noise reduction.
        """
        r_env = REnvironment()

        ms_cardinal = MassSpectrumSet()
        dm_cardinal = MSDataManagerImzML(ms_cardinal, temp_dir=temp_dir)
        dm_cardinal.copy_meta(data_manager)

        method_norm = method.strip().lower()
        cardinal_method = "sgolay" if method_norm in {"savgol", "savgol_numba"} else method_norm
        cardinal_method = cardinal_method.removesuffix("_numba")

        logger.info(f"Starting noise reduction using Cardinal::smooth(method={cardinal_method})")

        r_massdata = r_env.cardinal.readImzML(data_manager.imzml_filepath) # type: ignore

        kwargs = {
            "method": cardinal_method,
            "width": int(window),
        }
        if cardinal_method == "gaussian" and sd is not None:
            kwargs["sd"] = sd
        elif cardinal_method == "sgolay":
            kwargs.update({
                "order": int(polyorder),
                "deriv": int(deriv),
                "delta": float(delta),
            })

        processed = r_env.robjects.r["process"](
            r_env.robjects.r["smooth"](r_massdata, **kwargs)
        )
        _ = processed

    @staticmethod
    def normalization(data_manager: MSDataManagerImzML,
                      method: str = "tic",
                      scale: float | None = None,
                      ref: float | None = None,
                      temp_dir: str = "./temp_normalization_data"
                      ) -> None:
        """
        Call Cardinal::normalize for intensity normalization.
        """
        r_env = REnvironment()

        ms_cardinal = MassSpectrumSet()
        dm_cardinal = MSDataManagerImzML(ms_cardinal, temp_dir=temp_dir)
        dm_cardinal.copy_meta(data_manager)

        method_norm = method.strip().lower().removesuffix("_numba")
        cardinal_method = "reference" if method_norm in {"ref", "reference"} else method_norm

        logger.info(f"Starting normalization using Cardinal::normalize(method={cardinal_method})")

        r_massdata = r_env.cardinal.readImzML(data_manager.imzml_filepath) # type: ignore

        kwargs = {"method": cardinal_method}
        if scale is not None:
            kwargs["scale"] = float(scale)
        if cardinal_method == "reference":
            if ref is None:
                raise ValueError("Cardinal reference normalization requires ref")
            kwargs["ref"] = r_env.float_vector([ref])

        processed = r_env.robjects.r["process"](
            r_env.robjects.r["normalize"](r_massdata, **kwargs)
        )
        _ = processed

    @staticmethod
    def peak_align(data_manager: MSDataManagerImzML,
                   reference=None,
                   tolerance=None,
                   units: str = "ppm",
                   binfun: str = "min",
                   binratio: float = 2.0,
                   temp_dir: str = "./temp_align_data"
                   ) -> None:
        """
        Call Cardinal::peakAlign for peak alignment.
        """
        # Initialize shared R runtime and Cardinal bindings.
        r_env = REnvironment()

        # Build output data manager and copy metadata from source dataset.
        ms_cardinal = MassSpectrumSet()
        dm_cardinal = MSDataManagerImzML(ms_cardinal, temp_dir=temp_dir)
        dm_cardinal.copy_meta(data_manager)
        dm_cardinal.ms.meta.continuous = True

        # Convert optional Python parameters to R-compatible values.
        # - reference=None -> NULL (let Cardinal auto-select reference)
        # - tolerance=None -> NA_real_ (use package default tolerance)
        r_reference = r_env.float_vector(reference) if reference is not None else r_env.robjects.NULL
        r_tol = r_env.float_vector([tolerance]) if tolerance is not None else r_env.robjects.NA_Real

        logger.info(f"Starting peak alignment using Cardinal::peakAlign(units={units}, binfun={binfun}, binratio={binratio})")

        # Read source imzML as Cardinal MSImagingExperiment.
        imzml_filepath = data_manager.imzml_filepath
        r_massdata = r_env.cardinal.readImzML(imzml_filepath) # type: ignore

        # Run Cardinal peak alignment in R.
        aligned_massdata = r_env.cardinal.peakAlign( # type: ignore
            r_massdata,
            ref=r_reference,
            tolerance=r_tol,
            units=units,
            binfun=binfun,
            binratio=binratio
        )

        # Persist aligned result to output imzML and reload Python-side headers.
        # aligned_filepath = dm_cardinal.imzml_filepath
        # r_env.cardinal.writeMSIData(aligned_massdata, file=aligned_filepath, bundle=False) # type: ignore


        # with risky_imzml_loader():
        #     dm_cardinal.load_head_data()

        # logger.info(f"Peak alignment completed and data saved to {aligned_filepath}")
        # return dm_cardinal

    @staticmethod
    def peak_pick(data_manager: MSDataManagerImzML,
                  width: int = 5,
                  method: str = "quantile", # "diff", "sd", "mad", "quantile", "filter", "cwt"
                  snr: float = 2.0,
                  return_type: str = "height", # "height", "area"
                  prominence: float | None = None,
                  relheight: float | None = None,
                  nbins: int = 1,
                  overlap: float = 0.5,
                  temp_dir: str = "./temp_pick_data"
                  ) -> None:
        """
        Call Cardinal::peakPick for peak picking.
        """
        if relheight is not None:
            logger.warning("The 'relheight' parameter is not supported in the Cardinal backend and will be ignored.")

        # Initialize shared R runtime and Cardinal bindings.
        r_env = REnvironment()

        # Build output data manager and copy metadata from source dataset.
        ms_cardinal = MassSpectrumSet()
        dm_cardinal = MSDataManagerImzML(ms_cardinal, temp_dir=temp_dir)
        dm_cardinal.copy_meta(data_manager)

        logger.info(f"Starting peak picking using Cardinal::peakPick (method={method}, SNR={snr}, type={return_type})")

        # Read source imzML as Cardinal MSImagingExperiment.
        imzml_filepath = data_manager.imzml_filepath
        r_massdata = r_env.cardinal.readImzML(imzml_filepath) # type: ignore
        r_as = r_env.robjects.r["as"]

        r_massdata_arrays = r_as(r_massdata, "MSImagingArrays") # type: ignore

        # Run Cardinal peak picking in R.
        picked_massdata = r_env.cardinal.peakPick( # type: ignore
            r_massdata_arrays,
            width=width,
            method=method,
            SNR=snr,
            type=return_type,
            prominence=prominence if prominence is not None else r_env.robjects.NULL,
            nbins=nbins,
            overlap=overlap
        )

        # Materialize the queued peak-pick on the arrays representation before export.
        picked_massdata_realize = r_env.cardinal.process(picked_massdata) # type: ignore

        # # Persist picked result to output imzML and reload Python-side headers.
        # picked_filepath = dm_cardinal.imzml_filepath
        # r_env.cardinal.writeMSIData(picked_massdata_realize, file=picked_filepath, bundle=False) # type: ignore

        # with risky_imzml_loader():
        #     dm_cardinal.load_head_data()

        # logger.info(f"Peak picking completed and data saved to {picked_filepath}")
        # return dm_cardinal
