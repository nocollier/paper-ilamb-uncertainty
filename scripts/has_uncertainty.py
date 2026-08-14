from pathlib import Path

import pandas as pd
import xarray as xr


def check_dataset(nc_file: Path) -> list[dict[str, str | Path]]:
    """Return the dataset, variable, and uncertainty variable if present in the file."""
    ds = xr.open_dataset(nc_file)
    out = []
    for var, da in ds.items():
        uncert = [
            attr
            for attr in [
                da.attrs.get(attr, None) for attr in ["bounds", "ancillary_variables"]
            ]
            if attr is not None and attr in ds
        ]
        if uncert:
            for un in uncert:
                out.append({"dataset": nc_file, "variable": var, "uncertainty": un})
    return out


def has_uncertainty(root: str | Path) -> pd.DataFrame:
    """Recursively check dataset under the given root for the presence of uncertainty."""
    root = Path(root)
    df = []
    for sdir, _, files in root.walk():
        for f in files:
            if not f.endswith(".nc"):
                continue
            df += check_dataset(sdir / f)
    df = pd.DataFrame(df, columns=["dataset", "variable", "uncertainty"])
    for r, row in df.iterrows():
        df.loc[r, "dataset"] = row["dataset"].relative_to(root)  # type: ignore
    df.sort_values("dataset").reset_index(inplace=True)
    return df


if __name__ == "__main__":
    for root in [
        str(Path.home() / ".cache/ilamb3/0.1"),
        "/var/www/www.ilamb.org/html/ILAMB-Data/DATA",
        "/var/www/www.ilamb.org/html/ilamb3-data",
    ]:
        df = has_uncertainty(root)
        print(f"Searching in {root=}...")
        print(df.to_string())
