from pathlib import Path
from typing import Literal

import ilamb3.load as ill
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr

matplotlib.rc("font", size=18)


def plot_bias_cartoon(
    ref: xr.Dataset, com: xr.Dataset, lat: float, lon: float, var: str, filename: Path
):
    ref = (
        ref.sel(lat=lat, lon=lon, method="nearest", drop=True)
        .sel(time=slice("2008-01-01", "2010-01-01"))
        .convert_calendar("standard")
    )
    com = (
        com.sel(lat=lat, lon=(lon + 360), method="nearest", drop=True)
        .sel(time=slice("2008-01-01", "2010-01-01"))
        .convert_calendar("standard")
    )
    fig, ax = plt.subplots(figsize=(8, 5), tight_layout=True)

    # plot main reference and comparison variable
    ax.fill_between(
        ref["time"].values,
        (ref[var] - ref[f"{var}_sd"]).values,
        (ref[var] + ref[f"{var}_sd"]).values,
        color="k",
        alpha=0.15,
        lw=0,
    )
    ref[var].plot(ax=ax, color="k")
    com[var].plot(ax=ax, color="r")
    ax.text(
        np.datetime64("2008-01-01"),
        ref[var][0],
        r"$v_{\mathrm{ref}}(t)$",
        size=18,
        ha="right",
        va="center",
    )
    ax.text(
        com["time"].isel({"time": com[var].argmax(dim="time")}),
        com[var].max(),
        r"$v_{\mathrm{com}}(t)$",
        size=18,
        ha="center",
        va="bottom",
        color="r",
    )

    # label the uncertainty
    low = ref[var] - ref[f"{var}_sd"]
    hi = ref[var] + ref[f"{var}_sd"]
    ax.text(
        low["time"].isel({"time": low.argmin(dim="time")}),
        low.min(),
        r"$\delta(t)$",
        size=18,
        ha="center",
        va="top",
        color="0.5",
    )

    # plot reference mean and label
    ref_mean = ref.mean(dim="time")
    print(f"{ref_mean=}")
    print(f"{ref[var].std(dim='time')}")
    ax.fill_between(
        [np.datetime64("2010-02-01"), np.datetime64("2010-04-01")],
        [float(ref_mean[var] - ref_mean[f"{var}_sd"])] * 2,
        [float(ref_mean[var] + ref_mean[f"{var}_sd"])] * 2,
        color="k",
        alpha=0.15,
        lw=0,
    )
    ax.plot(
        [np.datetime64("2010-02-01"), np.datetime64("2010-04-01")],
        [ref_mean[var]] * 2,
        "--k",
    )
    ax.text(
        np.datetime64("2010-04-05"),
        ref_mean[var],
        r"$\overline{v_{\mathrm{ref}}}$",
        size=18,
        va="center",
    )
    ax.text(
        np.datetime64("2010-03-01"),
        (ref_mean[var] - 1.05 * ref_mean[f"{var}_sd"]),
        r"$\overline{\delta}$",
        size=18,
        ha="center",
        va="top",
        color="0.5",
    )

    # plot comparison mean and label
    com_mean = com.mean(dim="time")
    print(f"{com_mean=}")
    ax.plot(
        [np.datetime64("2010-02-01"), np.datetime64("2010-04-01")],
        [com_mean[var]] * 2,
        "--r",
    )
    ax.text(
        np.datetime64("2010-04-05"),
        com_mean[var],
        r"$\overline{v_{\mathrm{com}}}$",
        size=18,
        color="r",
        va="center",
    )

    hi = max(hi.max(), com[var].max())
    lo = min(low.min(), com[var].min())
    rng = hi - lo
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_xlim(np.datetime64("2007-08-01"), np.datetime64("2010-06-01"))
    ax.set_ylim(lo - 0.08 * rng, hi + 0.05 * rng)
    ax.set_xticks([np.datetime64(f"{y}-01-01") for y in range(2008, 2011)])
    ax.set_xlabel("")
    ax.set_ylabel(f"Latent Heat Flux [W m$^{{-2}}$]")
    fig.savefig(filename, dpi=200)
    plt.close()


def plot_rmse_cartoon(
    ref: xr.Dataset, com: xr.Dataset, lat: float, lon: float, var: str, filename: Path
):
    ref = (
        ref.sel(lat=lat, lon=lon, method="nearest", drop=True)
        .sel(time=slice("2008-01-01", "2010-01-01"))
        .convert_calendar("standard")
    )
    com = (
        com.sel(lat=lat, lon=(lon + 360), method="nearest", drop=True)
        .sel(time=slice("2008-01-01", "2010-01-01"))
        .convert_calendar("standard")
    )
    ref[var] = ref[var] - ref[var].mean(dim="time")
    com[var] = com[var] - com[var].mean(dim="time")
    ref = ref.resample(time="D").interpolate()
    com = com.resample(time="D").interpolate()

    fig, ax = plt.subplots(figsize=(8, 5), tight_layout=True)

    # plot main reference and comparison variable
    ax.fill_between(
        ref["time"].values,
        (ref[var] - ref[f"{var}_sd"]).values,
        (ref[var] + ref[f"{var}_sd"]).values,
        color="k",
        alpha=0.15,
        lw=0,
    )
    ref[var].plot(ax=ax, color="k")
    com[var].plot(ax=ax, color="r")
    ax.text(
        np.datetime64("2008-01-01"),
        ref[var][1],
        r"$\widehat{v_{\mathrm{ref}}}(t)$",
        size=18,
        ha="right",
        va="top",
    )
    ax.text(
        com["time"].isel({"time": com[var].argmax(dim="time")}),
        com[var].max(),
        r"$\widehat{v_{\mathrm{com}}}(t)$",
        size=18,
        ha="center",
        va="bottom",
        color="r",
    )

    # label the uncertainty
    low = ref[var] - ref[f"{var}_sd"]
    hi = ref[var] + ref[f"{var}_sd"]

    ax.fill_between(
        com["time"],
        hi,
        com[var],
        where=(com[var].values > hi.values),
        color="r",
        alpha=0.15,
    )
    ax.fill_between(
        com["time"],
        low,
        com[var],
        where=(com[var].values < low.values),
        color="r",
        alpha=0.15,
        label="Discounted Error",
    )
    ax.text(
        low["time"].isel({"time": low.argmin(dim="time")}),
        low.min(),
        r"$\delta(t)$",
        size=18,
        ha="center",
        va="top",
        color="0.5",
    )

    hi = max(hi.max(), com[var].max())
    lo = min(low.min(), com[var].min())
    rng = hi - lo
    ax.spines["bottom"].set_position("zero")
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_xlim(np.datetime64("2007-08-01"), np.datetime64("2010-06-01"))
    ax.set_ylim(lo - 0.08 * rng, hi + 0.05 * rng)
    ax.set_xticks([np.datetime64(f"{y}-01-01") for y in range(2008, 2011)])
    ax.set_xlabel("")
    ax.set_ylabel(f"Latent Heat Flux [W m$^{{-2}}$]")
    fig.legend(loc="outside lower right")
    fig.savefig(filename, dpi=200)
    plt.close()


if __name__ == "__main__":
    ref = ill.load_key_or_filename(
        "CLASS-1-1/obs4MIPs_UNSW_CLASS-1-1_mon_hfls_gn_v20260302.nc"
    )
    com = xr.open_dataset(
        "/home/nate/esgf-data/CMIP6/CMIP/CCCma/CanESM5/historical/r1i1p1f1/Amon/hfls/gn/v20190429/hfls_Amon_CanESM5_historical_r1i1p1f1_gn_185001-201412.nc"
    )

    # moderate gain 50.12,-99.92
    plot_bias_cartoon(
        ref,
        com,
        lat=50.12,
        lon=-99.92,
        var="hfls",
        filename=Path("bias_moderate.png"),
    )
    # big gain 0.25,115.2
    plot_bias_cartoon(
        ref, com, lat=0.25, lon=115.2, var="hfls", filename=Path("bias_large.png")
    )

    # moderate gain 50.12,-99.92
    plot_rmse_cartoon(
        ref, com, lat=50.12, lon=-99.92, var="hfls", filename=Path("rmse_moderate.png")
    )
    # big gain 0.25,115.2
    plot_rmse_cartoon(
        ref, com, lat=0.25, lon=115.2, var="hfls", filename=Path("rmse_large.png")
    )
