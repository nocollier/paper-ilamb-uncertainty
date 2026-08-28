from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import MultipleLocator

matplotlib.rc("font", size=18)


def zoom_out(
    xlim: tuple[float, float], ylim: tuple[float, float]
) -> tuple[list[float], list[float]]:
    xlim = list(xlim)
    ylim = list(ylim)
    dx = xlim[1] - xlim[0]
    dy = ylim[1] - ylim[0]
    ar = dy / dx
    if min(dx, dy) > 0.1:
        return xlim, ylim
    xlim[0] = 0.5 * (xlim[0] + xlim[1]) - 0.05
    xlim[1] = 0.5 * (xlim[0] + xlim[1]) + 0.05
    ylim[0] = 0.5 * (ylim[0] + ylim[1]) - ar * 0.05
    ylim[1] = 0.5 * (ylim[0] + ylim[1]) + ar * 0.05
    return xlim, ylim


def check_lims(
    xlim: tuple[float, float], ylim: tuple[float, float]
) -> tuple[list[float], list[float]]:
    xlim, ylim = zoom_out(xlim, ylim)
    ar = (ylim[1] - ylim[0]) / (xlim[1] - xlim[0])
    if xlim[0] < 0:
        xlim[0] = 0
        xlim[1] = (ylim[1] - ylim[0]) / ar
    if xlim[1] > 1:
        xlim[1] = 1
        xlim[0] = 1 - (ylim[1] - ylim[0]) / ar
    return xlim, ylim


def by_var_dset(df: pd.DataFrame, path: Path = Path("_figs")):
    path.mkdir(exist_ok=True, parents=True)
    df = df.reset_index()
    # cmap = plt.get_cmap("rainbow")
    # labels = list(df["variable"].unique())
    # colors = {key: cmap(i / (len(labels) - 1)) for i, key in enumerate(labels)}
    fig, axs = plt.subplots(
        figsize=(35, 35), nrows=6, ncols=6, tight_layout=True, dpi=200
    )
    count = -1
    for (var, dset), grp in df.groupby(["variable", "dataset"]):
        count += 1
        ax = axs[count // axs.shape[1], count % axs.shape[1]]
        # fig, ax = plt.subplots(figsize=(8, 8), tight_layout=True, dpi=200)
        for lbl, pl in grp.groupby("analysis"):
            ax.scatter(pl["NoUncertainty"], pl["Uncertainty"], s=40, label=lbl)
            ax.set_title(f"{var}\n{dset}")
        ax.set_aspect("equal", adjustable="datalim")
        ax.set_xlabel("Score, No Uncertainty [1]")
        ax.set_ylabel("Score, Uncertainty [1]")
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        ax.fill_between(
            [-1, 2],
            [-1, -1],
            [-1, 2],
            color="k",
            alpha=0.15,
            lw=0,
            label="Score Degrade Zone",
        )
        # xlim, ylim = check_lims(xlim, ylim)
        ax.set_xlim([0, 1])
        ax.set_ylim([0, 1.05])
        ax.grid(color="0.85")
        ax.xaxis.set_major_locator(MultipleLocator(0.2))
        ax.yaxis.set_major_locator(MultipleLocator(0.2))
        # ax.legend(loc="lower right")
        # fig.savefig(path / f"{var}_{dset}.png")
        # plt.close()
    for blank in range(count + 1, axs.size):
        axs[blank // axs.shape[1], blank % axs.shape[1]].axis("off")
    handles, labels = ax.get_legend_handles_labels()
    ax = axs[-1, -1]
    ax.text(
        0.5,
        1.0,
        "A Comparison of ILAMB Bias\nand RMSE Scores With\nand Without Uncertainty",
        va="top",
        ha="center",
        fontdict=dict(size=30),
    )
    ax.legend(handles=handles, labels=labels, loc="lower center")
    fig.savefig("composite.png")
    plt.close()


if __name__ == "__main__":
    df = pd.read_parquet("../data/uncertainty.parquet")
    by_var_dset(df)
