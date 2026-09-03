from pathlib import Path
from typing import Literal

import ilamb3.load as ill
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr

matplotlib.rc("font", size=18)


def get_sister_files(nc_file: Path) -> tuple[Path, Path]:
    if not nc_file.is_file():
        raise ValueError(f"Not a file {nc_file=}")
    un_file = (
        nc_file
        if "Uncertainty" in nc_file.parts
        else Path(
            *["Uncertainty" if p == "NoUncertainty" else p for p in nc_file.parts]
        )
    )
    no_file = (
        nc_file
        if "NoUncertainty" in nc_file.parts
        else Path(
            *["NoUncertainty" if p == "Uncertainty" else p for p in nc_file.parts]
        )
    )
    if not un_file.is_file():
        raise ValueError(f"Not a file {un_file=}")
    if not no_file.is_file():
        raise ValueError(f"Not a file {no_file=}")

    return un_file, no_file


def combine_sister_files(un_file: Path, no_file: Path) -> xr.Dataset:
    dsa = xr.open_dataset(un_file)
    dsa = dsa.drop_vars([v for v in dsa if v not in ["biasscore", "rmsescore"]]).rename(
        {"biasscore": "unbiasscore", "rmsescore": "unrmsescore"}
    )
    dsb = xr.open_dataset(no_file)
    dsb = dsb.drop_vars([v for v in dsb if v not in ["biasscore", "rmsescore"]])
    ds = xr.merge([dsa, dsb])
    for plot in ["biasscore", "rmsescore"]:
        if plot not in ds:
            continue
        ds[f"diff{plot}"] = ds[f"un{plot}"] - ds[plot]
    return ds


def plot_panel(ds: xr.Dataset, plot: Literal["biasscore", "rmsescore"]):
    if plot not in ds:
        raise ValueError(f"Dataset does not contain {plot=}")
    fig, axs = plt.subplots(figsize=(8, 12), nrows=3, tight_layout=True)
    ds[plot].plot(ax=axs[0], vmin=0, vmax=1)
    ds[f"un{plot}"].plot(ax=axs[1], vmin=0, vmax=1)
    da = ds[f"diff{plot}"].values.flatten()
    da = da[~np.isnan(da)]
    ds[f"diff{plot}"].plot(ax=axs[2], vmin=0, vmax=np.quantile(da, 0.95))
    return fig


if __name__ == "__main__":
    ds = combine_sister_files(
        *get_sister_files(
            Path("ilamb/_build/NoUncertainty/LatentHeat/CLASS-1-1/CanESM5.nc")
        )
    )
    fig = plot_panel(ds, "biasscore")
    fig.savefig("bias.png")
    plt.close()
    fig = plot_panel(ds, "rmsescore")
    fig.savefig("rmse.png")
    plt.close()
    ds.load()
