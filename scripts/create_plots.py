from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import MultipleLocator

matplotlib.rc("font", size=18)


def rank_changes(df: pd.DataFrame) -> float:
    """
    Count rank changes defined as how many have different neighbors.
    """

    return float(df.corr(numeric_only=True).iloc[0, 1])


def by_var_dset(df: pd.DataFrame, path: Path | None = None):
    colors = {
        key: plt.rcParams["axes.prop_cycle"].by_key()["color"][c]
        for c, key in zip([1, 4], ["Bias", "RMSE"])
    }
    ycoord = {"Bias": 0.02, "RMSE": 0.1}
    if path is None:
        path = Path("_figs")
    path.mkdir(exist_ok=True, parents=True)
    df = df.reset_index()
    fig, axs = plt.subplots(
        figsize=(35, 35 * 7 / 5), nrows=7, ncols=5, tight_layout=True, dpi=200
    )
    count = -1
    for (var, dset), grp in df.groupby(["variable", "dataset"]):
        if "Salinity" in var:
            continue
        if "Temperature" in var and ("200" in var or "700" in var):
            continue
        print(count + 2, var, dset)
        count += 1
        ax = axs[count // axs.shape[1], count % axs.shape[1]]
        for lbl, pl in grp.groupby("analysis"):
            ax.scatter(
                pl["NoUncertainty"],
                pl["Uncertainty"],
                s=50,
                label=lbl,
                color=colors[lbl],
            )
            ax.text(
                1.0,
                ycoord[lbl],
                f"$r_{{{lbl}}} = ${rank_changes(pl):.3f}",
                color=colors[lbl],
                ha="right",
                va="bottom",
                fontdict=dict(size=24),
            )
        ax.set_title(f"{var}\n{dset}")
        ax.set_xlabel("Score, No Uncertainty [1]")
        ax.set_ylabel("Score, Uncertainty [1]")
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
        ax.set_xlim([0, 1.05])
        ax.set_ylim([0, 1.05])
        ax.grid(color="0.85")
        ax.xaxis.set_major_locator(MultipleLocator(0.2))
        ax.yaxis.set_major_locator(MultipleLocator(0.2))
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
    df = df[~df.index.get_level_values(0).str.endswith("Surface")]
    by_var_dset(df)
