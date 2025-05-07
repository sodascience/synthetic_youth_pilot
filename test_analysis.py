import polars as pl
from asciibars import plot
from pathlib import Path

def main():
    # file names
    demgr_fn = "P_DEMOGRAFY_1.csv"
    medic_fn = "P_LIFSTYLE_1_MED_STOREY.csv"

    # data folders
    real_dir = Path("raw_data")
    synt_dir = Path("output", "csv")

    # some test analysis to get counts of diseases per 10-year age bucket
    print("\nParacetamol use in real data:\n")
    df_demgr = pl.read_csv(real_dir / demgr_fn, encoding="cp1252", separator=";", try_parse_dates=True)
    df_medic = pl.read_csv(real_dir / medic_fn, encoding="cp1252", separator=";")

    dfd = (
        df_demgr.select(["SubjectNo", "DOB_DT", "FormDate"])
        .with_columns(
            # Compute age in years
            pl.col.FormDate.dt.date()
            .sub(pl.col.DOB_DT)
            .dt.total_days()
            .floordiv(3652.5)
            .alias("decades")
            .cast(int)
        )
        .select(["SubjectNo", "decades"])
    )

    dfm = df_medic.select(["SubjectNo", "SOURCE"]).with_columns(
        # check if someone takes paracetamol
        pl.col("SOURCE").str.contains("(?i)paracet").alias("paracetamol")
    )

    df_final = (
        dfd.join(dfm, on="SubjectNo")
        .group_by("SubjectNo")
        .agg(pl.col.decades.first(), pl.col.paracetamol.any())
        .group_by("decades")
        .agg(pl.col.paracetamol.mean())
        .sort(pl.col.decades)
    )

    plot([(f"Age: {age * 10} - {age * 10 + 9}", round(prop, 2)) for age, prop in df_final.iter_rows()])


    # Now run the exact same analysis on the synthetic data:
    print("\n\nParacetamol use in synthetic data:\n")
    df_demgr = pl.read_csv(synt_dir / demgr_fn, encoding="cp1252", separator=";", try_parse_dates=True)
    df_medic = pl.read_csv(synt_dir / medic_fn, encoding="cp1252", separator=";")

    dfd = (
        df_demgr.select(["SubjectNo", "DOB_DT", "FormDate"])
        .with_columns(
            # Compute age in years
            pl.col.FormDate.dt.date()
            .sub(pl.col.DOB_DT)
            .dt.total_days()
            .floordiv(3652.5)
            .alias("decades")
            .cast(int)
        )
        .select(["SubjectNo", "decades"])
    )

    dfm = df_medic.select(["SubjectNo", "SOURCE"]).with_columns(
        # check if someone takes paracetamol
        pl.col("SOURCE").str.contains("(?i)paracet").alias("paracetamol")
    )

    df_final = (
        dfd.join(dfm, on="SubjectNo")
        .group_by("SubjectNo")
        .agg(pl.col.decades.first(), pl.col.paracetamol.any())
        .group_by("decades")
        .agg(pl.col.paracetamol.mean())
        .sort(pl.col.decades)
    )

    plot([(f"Age: {age * 10} - {age * 10 + 9}", round(prop, 2)) for age, prop in df_final.iter_rows()])

if __name__ == "__main__":
    main()