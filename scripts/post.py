from pathlib import Path

import pandas as pd
from ilamb3.meta import build_global_dataframe


def build_uncertainty_comparison_dataframe(
    output_path: Path, includes: list[str] = ["Bias Score [1]", "RMSE Score [1]"]
) -> pd.DataFrame:
    """Call the ilamb3 meta function, filter, and pivot for uncertainty comparisons."""
    df = build_global_dataframe(output_path)
    df = df.query(" | ".join([f"(name=='{inc}')" for inc in includes]))
    df = df[(df["name"] == "Bias Score [1]") | (df["name"] == "RMSE Score [1]")]
    df = df.set_index(["variable", "dataset", "source", "analysis"]).pivot(
        columns="section", values="value"
    )
    return df


if __name__ == "__main__":
    df = build_uncertainty_comparison_dataframe(Path("../ilamb/_build"))
    print(df)
