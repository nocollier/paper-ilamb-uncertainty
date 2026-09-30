from pathlib import Path

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import ilamb3.dataset as ild
import matplotlib.pyplot as plt
import xarray as xr

plt.rcParams.update({"text.usetex": True, "font.family": "serif", "font.size": 14})


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
    dsa = xr.open_dataset(un_file).drop_vars("mean")
    dsa = dsa.drop_vars([v for v in dsa if v not in ["biasscore", "rmsescore"]]).rename(
        {
            key: val
            for key, val in {
                "biasscore": "unbiasscore",
                "rmsescore": "unrmsescore",
            }.items()
            if key in dsa
        },
    )
    dsb = (
        xr.open_dataset(no_file)
        .drop_vars("mean")
        .rename({"lat_nested": "lat1", "lon_nested": "lon1"})
    )
    dsb = dsb.drop_vars([v for v in dsb if v not in ["biasscore", "rmsescore"]])
    ds = xr.merge([dsa, dsb])
    return ds


def plot_panel(
    ref: xr.Dataset,
    com: xr.Dataset,
    ref_name: str,
    model_name: str,
    var_name: str,
    cmap: str = "viridis",
):
    cmap = plt.get_cmap(cmap, 9)
    xf = ccrs.PlateCarree()
    score = {
        "cmap": plt.get_cmap("plasma", 9),
        "vmin": 0,
        "vmax": 1,
        "cbar_kwargs": {"label": "[1]"},
        "transform": xf,
    }
    nrow = 3 if "rmsescore" in com else 2
    fig, axs = plt.subplots(
        figsize=(12, 3.0 * nrow),
        nrows=nrow,
        ncols=2,
        tight_layout=True,
        subplot_kw={"projection": ccrs.Robinson()},
    )
    ref["mean"].plot(
        ax=axs[0, 0],
        cmap=cmap,
        transform=xf,
        vmin=float(ref["mean"].quantile(0.02)),
        vmax=float(ref["mean"].quantile(0.98)),
        cbar_kwargs={"label": f"[{ref['mean'].attrs.get('units', '')}]"},
    )
    ref["uncert"].plot(
        ax=axs[0, 1],
        cmap=plt.get_cmap("Reds", 9),
        vmin=0,
        vmax=float(ref["uncert"].quantile(0.98)),
        transform=xf,
        cbar_kwargs={"label": f"[{ref['mean'].attrs.get('units', '')}]"},
    )
    com["biasscore"].plot(ax=axs[1, 0], **score)
    com["unbiasscore"].plot(ax=axs[1, 1], **score)
    if "rmsescore" in com:
        com["rmsescore"].plot(ax=axs[2, 0], **score)
        com["unrmsescore"].plot(ax=axs[2, 1], **score)
    # Subfigure titles
    axs[0, 0].set_title(f"{ref_name} (Reference) {var_name} Mean")
    axs[0, 1].set_title(f"{ref_name} (Reference) {var_name} Uncertainty")
    axs[1, 0].set_title(f"{model_name} (Model) Bias Score")
    axs[1, 1].set_title(f"{model_name} (Model) Uncertainty Bias Score")
    if "rmsescore" in com:
        axs[2, 0].set_title(f"{model_name} (Model) RMSE Score")
        axs[2, 1].set_title(f"{model_name} (Model) Uncertainty RMSE Score")
    # Subfigure labels
    lbls = "abcdef"
    for i in range(axs.shape[0]):
        for j in range(axs.shape[1]):
            axs[i, j].text(
                0,
                0,
                f"$({lbls[2 * i + j]})$",
                color="k",
                ha="left",
                va="bottom",
                transform=axs[i, j].transAxes,
                fontdict={"size": 18},
            )
            axs[i, j].add_feature(
                cfeature.NaturalEarthFeature(
                    "physical", "land", "110m", edgecolor="face", facecolor="0.95"
                ),
                zorder=-1,
            )
            axs[i, j].add_feature(
                cfeature.NaturalEarthFeature(
                    "physical", "ocean", "110m", edgecolor="face", facecolor="0.85"
                ),
                zorder=-1,
            )
    return fig


if __name__ == "__main__":
    if True:
        dsr = xr.open_dataset(
            Path("ilamb/_build/Uncertainty/Precipitation/CLASS-1-1/Reference.nc")
        )
        dsc = combine_sister_files(
            *get_sister_files(
                Path(
                    "ilamb/_build/NoUncertainty/Precipitation/CLASS-1-1/UKESM1-0-LL.nc"
                )
            )
        )
        dsr = ild.convert(dsr, "mm d-1", "mean")
        dsr = ild.convert(dsr, "mm d-1", "uncert")
        fig = plot_panel(dsr, dsc, "CLASS-1-1", "UKESM1-0-LL", "pr", cmap="Blues")
        fig.savefig("pr.png", dpi=200)

    if True:
        dsr = xr.open_dataset(
            Path("ilamb/_build/Uncertainty/SoilCarbon/SoilGrids2/Reference.nc")
        )
        dsc = combine_sister_files(
            *get_sister_files(
                Path("ilamb/_build/NoUncertainty/SoilCarbon/SoilGrids2/CESM2.nc")
            )
        )
        fig = plot_panel(dsr, dsc, "SoilGrids2", "CESM2", "cSoil", cmap="viridis")
        fig.savefig("cSoil.png", dpi=200)

    if True:
        dsr = xr.open_dataset(
            Path("ilamb/_build/Uncertainty/SurfaceNetRadiation/CLASS-1-1/Reference.nc")
        )
        dsc = combine_sister_files(
            *get_sister_files(
                Path(
                    "ilamb/_build/NoUncertainty/SurfaceNetRadiation/CLASS-1-1/E3SM-1-1.nc"
                )
            )
        )
        fig = plot_panel(dsr, dsc, "CLASS-1-1", "E3SM-1-1", "rns", cmap="cool")
        fig.savefig("rns.png", dpi=200)
