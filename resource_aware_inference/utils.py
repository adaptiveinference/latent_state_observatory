
import numpy as np

def crossCorrelation(x, y, normalize=True):
    """
    Compute layerwise cross-correlation between two arrays x, and y

    Parameters
    ----------
    x : np.ndarray
        Shape: [nSteps, 1]

    y : np.ndarray
        Shape: [nSteps, 1]

    normalize : bool
        If True, z-normalize each signal before correlation.

    Returns
    -------
    xcorr : np.ndarray
        Shape: [2*nSteps - 1, 1]

    lags : np.ndarray
        Shape: [2*nSteps - 1]
        Negative lag:
            y leads x
        Positive lag:
            x leads y
    """
    assert x.shape == y.shape 

    nSteps = x.shape[0]

    # remove mean
    x = x - np.mean(x)
    y = y - np.mean(y)

    # optional normalization
    if normalize:
        x_std = np.std(x)
        y_std = np.std(y)

        if x_std > 0:
            x = x / x_std

        if y_std > 0:
            y = y / y_std

    # full cross-correlation
    corr = np.correlate(x, y, mode='full')

    # optional normalization by sequence length
    corr = corr / nSteps

    lags = np.arange(-(nSteps - 1), nSteps)

    return corr, lags    



