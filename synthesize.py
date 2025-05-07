import polars as pl
import metasyn as ms
from metasyncontrib.disclosure import DisclosurePrivacy
from pathlib import Path

# Paths
METADATA_PATH = Path("raw_data", "metadata", "YOUth_baby_en_kind-metadata.csv")
CSV_OUTFOLDER = Path("output", "csv")
GMF_OUTFOLDER = Path("output", "gmf")

def main():
    # Reset out paths
    if CSV_OUTFOLDER.exists():
        for file in CSV_OUTFOLDER.glob("*csv"):
            file.unlink()
    if GMF_OUTFOLDER.exists():
        for file in GMF_OUTFOLDER.glob("*json"):
            file.unlink()
    CSV_OUTFOLDER.mkdir(exist_ok=True)
    GMF_OUTFOLDER.mkdir(exist_ok=True)

    # First, we read the metadata
    # NB: encoding of this file is CP850(?)
    # read metadata
    print("Reading metadata")
    spec_metadata = {
        "StudyName": pl.Categorical,
        "Form": pl.Categorical,
        "Form_Varname": pl.Categorical,
        "VersionNumber": pl.Int64,
        "bestand": pl.Categorical,
    }
    metadata = pl.read_csv(
        source=METADATA_PATH,
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

    # then, create a look-up-table for the metadata to create polars dtypes
    TYPES_LUT = pl.DataFrame(
        {
            "Field_type": ["Date", "Radiobutton", "Text", "Integer", "Checkbox", "Decimal"],
            "dtype": [pl.Date, pl.Categorical, str, pl.Int64, pl.Categorical, pl.Float64],
        }
    )

    # privacy stuff
    priv_loose = ms.privacy.BasicPrivacy()
    priv_strict = DisclosurePrivacy(partition_size=11)

    # Most common metadata-like columns do not need to be privacy-constrained
    subj_dist = ms.distribution.UniqueRegexDistribution(r"B[0-9]{5}")

    vs_common = [
        ms.VarSpec(name="FilledFormID", unique=True),
        ms.VarSpec(name="SubjectNo", distribution=subj_dist),
        ms.VarSpec(name="StudyName", privacy=priv_loose),
        ms.VarSpec(name="SiteName", privacy=priv_loose),
        ms.VarSpec(name="VisitName", privacy=priv_loose),
        ms.VarSpec(name="VisitSchedule", privacy=priv_loose),
        ms.VarSpec(name="VisitScheduleInst", privacy=priv_loose),
        ms.VarSpec(name="FormSchedule", privacy=priv_loose),
        ms.VarSpec(name="FormScheduleInst", privacy=priv_loose),
        ms.VarSpec(name="FormVarname", privacy=priv_loose),
        ms.VarSpec(name="VersionNumber", privacy=priv_loose),
        ms.VarSpec(name="FormStatus", privacy=priv_loose),
        ms.VarSpec(name="ffSDVStatus", privacy=priv_loose),
        ms.VarSpec(name="ffIsLocked", privacy=priv_loose),
    ]


    # function to create a polars dtypes dict from the metadata information
    def create_polars_dtypes_dict(data_name: str, metadata: pl.DataFrame = metadata) -> dict:
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


    def add_descriptions(mf: ms.MetaFrame, data_name: str, metadata: pl.DataFrame = metadata):
        """Add variable descriptions to a metaframe"""
        # get descriptions from metadata
        label_df = metadata.filter(pl.col.bestand == data_name).select(["QNAME", "Qlabel"])
        desc = {name: label for name, label in label_df.iter_rows()}
        for var in mf:
            var.description = desc.get(var.name)


    # function to read a dataset
    def read_youth_csv(data_name: str) -> tuple[pl.DataFrame, ms.filereader.BaseFileReader]:
        """Read in a youth data csv"""
        dtypes = create_polars_dtypes_dict(data_name, metadata=metadata)
        return ms.read_csv(
            f"raw_data/{data_name}.csv",
            encoding="cp1252",
            separator=";",
            schema_overrides=dtypes,
            try_parse_dates=True,
        )


    # Let's go synthesize things!

    ### CECPAQ_2 ###
    dname = "CECPAQ_2"
    print(f"Fitting and generating {dname}")
    df, fmt = read_youth_csv(dname)
    mf = ms.MetaFrame.fit_dataframe(
        df=df,
        file_format=fmt,
        privacy=priv_strict,
        var_specs=vs_common,
    )
    add_descriptions(mf, dname)
    mf.save(GMF_OUTFOLDER / f"{dname}.json")
    mf.write_synthetic(CSV_OUTFOLDER / f"{dname}.csv", seed=45)
    # New api would be like this?
    # df = mf.synthesize(seed=45)
    # ms.write_csv(df, CSV_OUTFOLDER / f"{dname}.csv", file_format=fmt)

    ### M_DEMOGRAFY_1 ###
    dname = "M_DEMOGRAFY_1"
    print(f"Fitting and generating {dname}")
    df, fmt = read_youth_csv(dname)

    # custom varspec stuff
    dist = ms.distribution.PoissonDistribution(1.2)
    vs_custom = [
        ms.VarSpec(name="LIVING_TOGETHER_4_AANTAL", distribution=dist, prop_missing=0.995),
        ms.VarSpec(name="LIVING_TOGETHER_5_AANTAL", distribution=dist, prop_missing=0.996),
        ms.VarSpec(name="LIVING_TOGETHER_6_AANTAL", distribution=dist, prop_missing=0.997),
        ms.VarSpec(name="LIVING_TOGETHER_7_AANTAL", distribution=dist, prop_missing=0.998),
        ms.VarSpec(name="LIVING_TOGETHER_9_AANTAL", distribution=dist, prop_missing=0.999),
        ms.VarSpec(name="LIVING_TOGETHER_8_AANTAL", distribution=dist, prop_missing=0.999),
        ms.VarSpec(name="LIVING_TOGETHER_10_AANTAL", distribution=dist, prop_missing=0.999),
    ]

    mf = ms.MetaFrame.fit_dataframe(
        df=df,
        file_format=fmt,
        privacy=priv_strict,
        var_specs=[*vs_common, *vs_custom],
    )
    add_descriptions(mf, dname)
    mf.save(GMF_OUTFOLDER / f"{dname}.json")
    mf.write_synthetic(CSV_OUTFOLDER / f"{dname}.csv", seed=45)

    ### P_DEMOGRAFY_1 ###
    dname = "P_DEMOGRAFY_1"
    print(f"Fitting and generating {dname}")
    df, fmt = read_youth_csv(dname)

    mf = ms.MetaFrame.fit_dataframe(
        df=df,
        file_format=fmt,
        privacy=priv_strict,
        var_specs=vs_common,
    )
    add_descriptions(mf, dname)
    mf.save(GMF_OUTFOLDER / f"{dname}.json")
    mf.write_synthetic(CSV_OUTFOLDER / f"{dname}.csv", seed=45)

    ### P_LIFSTYLE_1_MED_STOREY ###
    dname = "P_LIFSTYLE_1_MED_STOREY"
    print(f"Fitting and generating {dname}")
    df, fmt = read_youth_csv(dname)

    mf = ms.MetaFrame.fit_dataframe(
        df=df,
        file_format=fmt,
        privacy=priv_strict,
        var_specs=vs_common,
    )
    add_descriptions(mf, dname)
    mf.save(GMF_OUTFOLDER / f"{dname}.json")
    mf.write_synthetic(CSV_OUTFOLDER / f"{dname}.csv", seed=45)

    ### P_LIFSTYLE_1_MEDICATIONY ###
    dname = "P_LIFSTYLE_1_MEDICATIONY"
    print(f"Fitting and generating {dname}")
    df, fmt = read_youth_csv(dname)

    mf = ms.MetaFrame.fit_dataframe(
        df=df,
        file_format=fmt,
        privacy=priv_strict,
        var_specs=vs_common,
    )
    add_descriptions(mf, dname)
    mf.save(GMF_OUTFOLDER / f"{dname}.json")
    mf.write_synthetic(CSV_OUTFOLDER / f"{dname}.csv", seed=45)

    ### P_LIFSTYLE_1 ###
    dname = "P_LIFSTYLE_1"
    print(f"Fitting and generating {dname}")
    df, fmt = read_youth_csv(dname)

    vs_custom = [
        ms.VarSpec(name="SMOKING_Y1_SIGAR_AMOUNT", privacy=priv_loose),
        ms.VarSpec(name="SMOKING_Y1_OTH_AMOUNT", privacy=priv_loose),
    ]

    mf = ms.MetaFrame.fit_dataframe(
        df=df,
        file_format=fmt,
        privacy=priv_strict,
        var_specs=[*vs_common, *vs_custom],
    )
    add_descriptions(mf, dname)
    mf.save(GMF_OUTFOLDER / f"{dname}.json")
    mf.write_synthetic(CSV_OUTFOLDER / f"{dname}.csv", seed=45)

    ### Q_1 ###
    dname = "Q_1"
    print(f"Fitting and generating {dname}")
    df, fmt = read_youth_csv(dname)

    mf = ms.MetaFrame.fit_dataframe(
        df=df,
        file_format=fmt,
        privacy=priv_strict,
        var_specs=vs_common,
    )
    add_descriptions(mf, dname)
    mf.save(GMF_OUTFOLDER / f"{dname}.json")
    mf.write_synthetic(CSV_OUTFOLDER / f"{dname}.csv", seed=45)

if __name__ == "__main__":
    main()