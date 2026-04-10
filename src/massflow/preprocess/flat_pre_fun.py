from typing import Optional
import numpy as np

from massflow.preprocess.helper.baseline_correction_helper import baseline_corrector
from massflow.preprocess.helper.noise_reduction_helper import smoother
from massflow.preprocess.helper.normalizer_helper import normalizer
from massflow.tools.logger import get_logger

logger = get_logger("massflow.preprocess")


class FlatPreprocess:
    """Flat-array preprocessing helpers."""

    @staticmethod
    def noise_reduction_flat(
        intensity: np.ndarray,
        method: str = "ma_numba",
        window: int = 5,
        sd: float | None = None,
        sd_intensity: float | None = None,
        p: int = 2,
        coef: np.ndarray | None = None,
        polyorder: int = 3,
        deriv: int = 0,
        delta: float = 1.0,
        wavelet: str = "db4",
        threshold_mode: str = "soft",
        lengths: Optional[np.ndarray] = None,
    ) -> np.ndarray:
        """Perform flat-mode noise reduction and return processed flat intensity.

        Supported methods are limited to:
        - ``savgol_numba``
        - ``gaussian_numba``
        - ``ma_numba``
        """
        method_norm = (method or "").strip().lower()
        supported_methods = {"savgol_numba", "gaussian_numba", "ma_numba"}
        if method_norm not in supported_methods:
            raise ValueError("noise_reduction_flat only supports: savgol_numba, gaussian_numba, ma_numba")


        return smoother(
            intensity=intensity,
            method=method_norm,
            window=window,
            sd=sd,
            sd_intensity=sd_intensity,
            p=p,
            coef=coef,
            polyorder=polyorder,
            deriv=deriv,
            delta=delta,
            wavelet=wavelet,
            threshold_mode=threshold_mode,
            lengths=lengths,
        )

    @staticmethod
    def normalization_flat(
        intensity: np.ndarray,
        method: str = "tic_numba",
        scale: float = 1.0,
        scale_method: str = "none",
        lengths: Optional[np.ndarray] = None,
    ) -> np.ndarray:
        """Perform flat-mode normalization and return processed flat intensity.

        Supported methods are limited to:
        - ``tic_numba``
        - ``rms_numba``
        - ``median_numba``

        """

        method_norm = (method or "").strip().lower()
        supported_methods = {"tic_numba", "rms_numba", "median_numba"}
        if method_norm not in supported_methods:
            raise ValueError("normalization_flat only supports: tic_numba, rms_numba, median_numba")

        return normalizer(
            intensity=intensity,
            method=method_norm,
            scale=scale,
            scale_method=scale_method,
            lengths=lengths,
        )

    @staticmethod
    def baseline_reduction_flat(
        intensity: np.ndarray,
        method: str = "locmin_numba",
        smooth: str = "none",
        span: float = 0.1,
        s: float | None = 0.0,
        upper: bool = False,
        width: int = 5,
        lam: float = 1e7,
        p: float = 0.01,
        niter: int = 15,
        baseline_scale: float = 1.0,
        m: int | None = None,
        decreasing: bool = True,
        lengths: Optional[np.ndarray] = None,
    ) -> np.ndarray:
        """Perform flat-mode baseline reduction and return corrected flat intensity.

        Supported methods are limited to:
        - ``locmin_numba``
        - ``snip_numba``
        """
        method_norm = (method or "").strip().lower()
        supported_methods = {"locmin_numba", "snip_numba"}
        if method_norm not in supported_methods:
            raise ValueError("baseline_reduction_flat only supports: locmin_numba, snip_numba")

        corrected, _ = baseline_corrector(
            intensity=intensity,
            method=method_norm,
            smooth=smooth,
            span=span,
            s=s,
            upper=upper,
            width=width,
            lam=lam,
            p=p,
            niter=niter,
            baseline_scale=baseline_scale,
            m=m,
            decreasing=decreasing,
            lengths=lengths,
        )
        return corrected
