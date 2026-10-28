from pathlib import Path

# import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import MultipleLocator

plt.rcParams.update({"text.usetex": True, "font.family": "serif", "font.size": 24})


def rank_changes(df: pd.DataFrame) -> float:
    """
    Count rank changes defined as how many have different neighbors.
    """

    return float(df.corr(numeric_only=True).iloc[0, 1])


def by_var_dset(df: pd.DataFrame, nrow: int = 6, filename: str = "composite.png"):
    colors = {
        key: plt.rcParams["axes.prop_cycle"].by_key()["color"][c]
        for c, key in zip([1, 4], ["Bias", "RMSE"])
    }
    ycoord = {"Bias": 0.02, "RMSE": 0.1}
    df = df.reset_index()
    fig, axs = plt.subplots(
        figsize=(25, 25 * nrow / 4), nrows=nrow, ncols=4, tight_layout=True, dpi=200
    )
    count = -1
    subfig = "abcdefghijklmnopqrstuvwxyz"
    rem_ax = None
    for (var, dset), grp in df.groupby(["variable", "dataset"]):
        if "Salinity" in var:
            continue
        if "Temperature" in var and ("200" in var or "700" in var):
            continue
        print(count + 2, var, dset)
        count += 1
        ax = axs[count // axs.shape[1], count % axs.shape[1]]
        if "RMSE" in grp["analysis"].unique():
            rem_ax = ax
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
                color="k",  # colors[lbl],
                ha="right",
                va="bottom",
                fontdict=dict(size=24),
            )
            ax.text(
                0.025,
                1,
                f"$({''.join([subfig[count % 26]] * (int(count / 26) + 1))})$",
                color="k",
                ha="left",
                va="top",
                fontdict={"size": 36},
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
    handles, labels = rem_ax.get_legend_handles_labels()
    ax = axs[-1, -1]
    ax.legend(handles=handles, labels=labels, loc="center")
    fig.savefig(filename)
    plt.close()


def interactive_plot(df):
    import plotly
    import plotly.express as px

    df = df.reset_index()
    df["panel"] = df["variable"] + "/" + df["dataset"]
    fig = px.scatter(
        df,
        x="NoUncertainty",
        y="Uncertainty",
        color="analysis",
        facet_col="panel",
        facet_col_wrap=8,
        hover_data=df.columns,
    )
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    plotly.offline.plot(fig, filename="uncertainty.html")


if __name__ == "__main__":
    df = pd.read_parquet("../data/uncertainty.parquet")
    df = df[~df.index.get_level_values(0).str.endswith("Surface")]
    df = df[~df.index.get_level_values(1).str.startswith("CARDAMOM")]
    by_var_dset(df)

    df = pd.read_parquet("../data/uncertainty.parquet")
    df = df[df.index.get_level_values(1).str.startswith("CARDAMOM")]
    by_var_dset(df, 4, "cardamom.png")
