"""Utility functions for youth data synthetization."""

import polars as pl
import metasyn as ms
from pathlib import Path


def clean_dirs(*dirs: Path) -> None:
    """Empties directories and makes sure they exist. Ignores hidden files starting with a `.` symbol, such as the .gitignore file."""
    for dir in dirs:
        if dir.exists():
            for file in dir.glob("[!.]*"):
                file.unlink()
        dir.mkdir(exist_ok=True)

# look-up-table from metadata field type <-> polars dtypes
TYPES_LUT = pl.DataFrame(
    {
        "Field_type": ["Date", "Radiobutton", "Text", "Integer", "Checkbox", "Decimal"],
        "dtype": [pl.Date, pl.Categorical, str, pl.Int64, pl.Categorical, pl.Float64],
    }
)

def read_metadata(path: Path) -> pl.DataFrame:
    spec_metadata = {
        "StudyName": pl.Categorical,
        "Form": pl.Categorical,
        "Form_Varname": pl.Categorical,
        "VersionNumber": pl.Int64,
        "bestand": pl.Categorical,
    }
    return pl.read_csv(
        source=path,
        encoding="cp850",
        separator=";",
        schema_overrides=spec_metadata,
        null_values="",
    ).select(
        [
            "StudyName",
            "Form",
            "bestand",
            "QNAME",
            "Qlabel",
            "Form_Varname",
            "VersionNumber",
            "Field_type",
            "Q_AnswerType",
        ]
    )


# function to create a polars dtypes dict from the metadata information
def create_polars_dtypes_dict(data_name: str, metadata: pl.DataFrame) -> dict:
    """Use metadata to create dtypes dict for use in Polars.read_csv()."""
    dem_spec_df = (
        metadata.filter(pl.col("bestand") == data_name)
        .select(["QNAME", "Field_type"])
        .join(TYPES_LUT, on="Field_type")
        .drop("Field_type")
    )
    table_spec = {nm: dtp for nm, dtp in zip(dem_spec_df["QNAME"], dem_spec_df["dtype"])}
    table_spec["StudyName"] = pl.Categorical
    table_spec["SiteName"] = pl.Categorical
    table_spec["FormStatus"] = pl.Categorical
    return table_spec



# function to read a dataset
def read_youth_csv(data_name: str, metadata: pl.DataFrame) -> tuple[pl.DataFrame, ms.file.BaseFileInterface]:
    """Read in a youth data csv"""
    dtypes = create_polars_dtypes_dict(data_name, metadata=metadata)
    return ms.read_csv(
        f"raw_data/{data_name}.csv",
        encoding="cp1252",
        separator=";",
        schema_overrides=dtypes,
        try_parse_dates=True,
    )

def add_descriptions(mf: ms.MetaFrame, data_name: str, metadata: pl.DataFrame):
    """Add variable descriptions to a metaframe"""
    # get descriptions from metadata
    label_df = metadata.filter(pl.col.bestand == data_name).select(["QNAME", "Qlabel"])
    desc = {name: label for name, label in label_df.iter_rows()}
    for var in mf:
        var.description = desc.get(var.name)
