import metasyn as ms
from metasyncontrib.disclosure import DisclosurePrivacy
from metasyn.privacy import BasicPrivacy
from pathlib import Path
from src.utils import clean_dirs, read_metadata, read_youth_csv, add_descriptions


# Paths
METADATA_PATH = Path("raw_data", "metadata", "YOUth_baby_en_kind-metadata.csv")
CSV_OUTFOLDER = Path("output", "csv")
GMF_OUTFOLDER = Path("output", "gmf")




def main():
    # Reset out paths
    clean_dirs(CSV_OUTFOLDER, GMF_OUTFOLDER)

    # First, we read the metadata
    # NB: encoding of this file is CP850(?)
    # read metadata
    print("Reading metadata")
    metadata = read_metadata(METADATA_PATH)

    # privacy stuff
    priv_loose = BasicPrivacy()
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

    # Let's go synthesize things!

    ### CECPAQ_2 ###
    dname = "CECPAQ_2"
    print(f"Fitting and generating {dname}")
    df, fmt = read_youth_csv(dname, metadata)
    mf = ms.MetaFrame.fit_dataframe(
        df=df,
        file_format=fmt,
        privacy=priv_strict,
        var_specs=vs_common,
    )
    add_descriptions(mf, dname, metadata)
    mf.save(GMF_OUTFOLDER / f"{dname}.json")
    mf.write_synthetic(CSV_OUTFOLDER / f"{dname}.csv", seed=45)
    # New api would be like this?
    # df = mf.synthesize(seed=45)
    # ms.write_csv(df, CSV_OUTFOLDER / f"{dname}.csv", file_format=fmt)

    ### M_DEMOGRAFY_1 ###
    dname = "M_DEMOGRAFY_1"
    print(f"Fitting and generating {dname}")
    df, fmt = read_youth_csv(dname, metadata)

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
    add_descriptions(mf, dname, metadata)
    mf.save(GMF_OUTFOLDER / f"{dname}.json")
    mf.write_synthetic(CSV_OUTFOLDER / f"{dname}.csv", seed=45)

    ### P_DEMOGRAFY_1 ###
    dname = "P_DEMOGRAFY_1"
    print(f"Fitting and generating {dname}")
    df, fmt = read_youth_csv(dname, metadata)

    mf = ms.MetaFrame.fit_dataframe(
        df=df,
        file_format=fmt,
        privacy=priv_strict,
        var_specs=vs_common,
    )
    add_descriptions(mf, dname, metadata)
    mf.save(GMF_OUTFOLDER / f"{dname}.json")
    mf.write_synthetic(CSV_OUTFOLDER / f"{dname}.csv", seed=45)

    ### P_LIFSTYLE_1_MED_STOREY ###
    dname = "P_LIFSTYLE_1_MED_STOREY"
    print(f"Fitting and generating {dname}")
    df, fmt = read_youth_csv(dname,metadata)

    mf = ms.MetaFrame.fit_dataframe(
        df=df,
        file_format=fmt,
        privacy=priv_strict,
        var_specs=vs_common,
    )
    add_descriptions(mf, dname, metadata)
    mf.save(GMF_OUTFOLDER / f"{dname}.json")
    mf.write_synthetic(CSV_OUTFOLDER / f"{dname}.csv", seed=45)

    ### P_LIFSTYLE_1_MEDICATIONY ###
    dname = "P_LIFSTYLE_1_MEDICATIONY"
    print(f"Fitting and generating {dname}")
    df, fmt = read_youth_csv(dname,metadata)

    mf = ms.MetaFrame.fit_dataframe(
        df=df,
        file_format=fmt,
        privacy=priv_strict,
        var_specs=vs_common,
    )
    add_descriptions(mf, dname, metadata)
    mf.save(GMF_OUTFOLDER / f"{dname}.json")
    mf.write_synthetic(CSV_OUTFOLDER / f"{dname}.csv", seed=45)

    ### P_LIFSTYLE_1 ###
    dname = "P_LIFSTYLE_1"
    print(f"Fitting and generating {dname}")
    df, fmt = read_youth_csv(dname, metadata)

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
    add_descriptions(mf, dname, metadata)
    mf.save(GMF_OUTFOLDER / f"{dname}.json")
    mf.write_synthetic(CSV_OUTFOLDER / f"{dname}.csv", seed=45)

    ### Q_1 ###
    dname = "Q_1"
    print(f"Fitting and generating {dname}")
    df, fmt = read_youth_csv(dname, metadata)

    mf = ms.MetaFrame.fit_dataframe(
        df=df,
        file_format=fmt,
        privacy=priv_strict,
        var_specs=vs_common,
    )
    add_descriptions(mf, dname, metadata)
    mf.save(GMF_OUTFOLDER / f"{dname}.json")
    mf.write_synthetic(CSV_OUTFOLDER / f"{dname}.csv", seed=45)


if __name__ == "__main__":
    main()
