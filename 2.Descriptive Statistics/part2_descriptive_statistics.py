import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

try:
    from ydata_profiling import ProfileReport
except Exception:  # pragma: no cover
    ProfileReport = None


REQUIRED_COLUMNS = [
    "Age",
    "Gender",
    "Education Level",
    "Years of Experience",
    "Salary",
]

EDUCATION_ORDER = ["High School", "Bachelor", "Master", "PhD"]


def load_dataframe(input_path: Path, sheet_name: str | int) -> pd.DataFrame:
    suffix = input_path.suffix.lower()
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(input_path, sheet_name=sheet_name)
    if suffix == ".csv":
        return pd.read_csv(input_path)
    raise ValueError("Input file must end with .xlsx, .xls, or .csv")


def check_required_columns(df: pd.DataFrame) -> None:
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def build_descriptive_table(df: pd.DataFrame) -> pd.DataFrame:
    cols = ["Age", "Years of Experience", "Salary"]
    summary = df[cols].agg(["mean", "std", "min", "max"]).T
    summary = summary.rename(columns={"std": "sd"})
    summary.index.name = "variable"
    return summary.reset_index()


def build_distribution_table(df: pd.DataFrame, col: str) -> pd.DataFrame:
    counts = df[col].value_counts(dropna=False).rename("count")
    perc = (counts / len(df) * 100).rename("percent")
    out = pd.concat([counts, perc], axis=1).reset_index()
    out = out.rename(columns={"index": col})
    out["percent"] = out["percent"].round(2)
    return out


def build_correlation_table(df: pd.DataFrame) -> pd.DataFrame:
    numeric_df = df.select_dtypes(include=["number"]).copy()
    preferred = ["Age", "Years of Experience", "Salary", "lnSalary"]
    selected = [c for c in preferred if c in numeric_df.columns]
    if len(selected) >= 2:
        numeric_df = numeric_df[selected]
    corr = numeric_df.corr(numeric_only=True)
    corr.index.name = "variable"
    return corr.reset_index()


def save_plot_scatter(df: pd.DataFrame, x_col: str, y_col: str, output_file: Path) -> None:
    plt.figure(figsize=(8, 5))
    sns.scatterplot(data=df, x=x_col, y=y_col, alpha=0.7)
    plt.title(f"Scatter Plot: {y_col} vs {x_col}")
    plt.tight_layout()
    plt.savefig(output_file, dpi=150)
    plt.close()


def save_plot_box(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    output_file: Path,
    order: list[str] | None = None,
) -> None:
    plt.figure(figsize=(8, 5))
    sns.boxplot(data=df, x=x_col, y=y_col, order=order)
    plt.title(f"Boxplot: {y_col} by {x_col}")
    plt.tight_layout()
    plt.savefig(output_file, dpi=150)
    plt.close()


def generate_ydata_profile(df: pd.DataFrame, output_file: Path, title: str) -> tuple[bool, str]:
    if ProfileReport is None:
        return False, "ydata-profiling import failed"

    try:
        profile = ProfileReport(
            df,
            title=title,
            explorative=True,
            minimal=False,
            progress_bar=False,
            correlations={
                "auto": {"calculate": True},
                "pearson": {"calculate": True},
                "spearman": {"calculate": True},
            },
        )
        profile.to_file(str(output_file))
        return True, "ok"
    except Exception as exc:  # pragma: no cover
        return False, str(exc)


def write_markdown_summary(
    output_file: Path,
    n_obs: int,
    descriptive_path: Path,
    gender_path: Path,
    education_path: Path,
    corr_path: Path,
    profile_path: Path,
    profile_ok: bool,
) -> None:
    lines = [
        "# Part 2 - Descriptive Statistics",
        "",
        f"- Number of observations: {n_obs}",
        f"- Descriptive table: {descriptive_path.name}",
        f"- Gender distribution: {gender_path.name}",
        f"- Education distribution: {education_path.name}",
        f"- Correlation matrix: {corr_path.name}",
        f"- YData profile: {profile_path.name if profile_ok else 'not generated'}",
        "",
        "## Notes",
        "- Correlation between Age and Years of Experience should be checked for multicollinearity risk in OLS.",
    ]
    output_file.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    project_root = Path(__file__).resolve().parents[1]
    default_candidates = [
        Path(__file__).resolve().parent / "Group13_DSEB66A_part1_cleaned.xlsx",
        project_root / "1.Data Cleaning" / "Group13_DSEB66A_part1_cleaned.xlsx",
        project_root / "Group13_DSEB66A.xlsx",
    ]
    default_input = next((p for p in default_candidates if p.exists()), default_candidates[0])

    parser = argparse.ArgumentParser(description="Part 2 descriptive statistics and profiling")
    parser.add_argument("--input", default=str(default_input), help="Input file path")
    parser.add_argument("--sheet", default=0, help="Excel sheet index/name")
    parser.add_argument(
        "--output-dir",
        default=str(Path(__file__).resolve().parent / "outputs"),
        help="Output directory",
    )
    parser.add_argument(
        "--profile-title",
        default="Salary Dataset - Descriptive Statistics Profile",
        help="Title used for ydata-profiling report",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = Path(args.input).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    sheet_name: str | int = args.sheet
    if isinstance(sheet_name, str) and sheet_name.isdigit():
        sheet_name = int(sheet_name)

    output_dir.mkdir(parents=True, exist_ok=True)

    df = load_dataframe(input_path, sheet_name=sheet_name)
    check_required_columns(df)

    descriptive = build_descriptive_table(df)
    gender_dist = build_distribution_table(df, "Gender")
    education_dist = build_distribution_table(df, "Education Level")
    corr = build_correlation_table(df)

    descriptive_path = output_dir / "descriptive_stats.csv"
    gender_path = output_dir / "gender_distribution.csv"
    education_path = output_dir / "education_distribution.csv"
    corr_path = output_dir / "correlation_matrix.csv"

    descriptive.to_csv(descriptive_path, index=False)
    gender_dist.to_csv(gender_path, index=False)
    education_dist.to_csv(education_path, index=False)
    corr.to_csv(corr_path, index=False)

    save_plot_scatter(df, "Age", "Salary", output_dir / "scatter_age_salary.png")
    save_plot_scatter(df, "Years of Experience", "Salary", output_dir / "scatter_experience_salary.png")
    save_plot_box(df, "Gender", "Salary", output_dir / "boxplot_salary_by_gender.png")
    education_order = [
        level for level in EDUCATION_ORDER if level in set(df["Education Level"].dropna().astype(str))
    ]
    save_plot_box(
        df,
        "Education Level",
        "Salary",
        output_dir / "boxplot_salary_by_education.png",
        order=education_order,
    )

    profile_path = output_dir / "ydata_profile_report.html"
    profile_ok, profile_msg = generate_ydata_profile(df, profile_path, args.profile_title)

    summary_path = output_dir / "part2_summary.md"
    write_markdown_summary(
        output_file=summary_path,
        n_obs=len(df),
        descriptive_path=descriptive_path,
        gender_path=gender_path,
        education_path=education_path,
        corr_path=corr_path,
        profile_path=profile_path,
        profile_ok=profile_ok,
    )

    print("=== PART 2 DESCRIPTIVE STATISTICS COMPLETED ===")
    print(f"Input file: {input_path}")
    print(f"Rows: {len(df)}")
    print(f"Output directory: {output_dir}")
    print(f"Saved: {descriptive_path.name}, {gender_path.name}, {education_path.name}, {corr_path.name}")
    print("Saved plots: scatter and boxplots")
    print(f"YData profile generated: {profile_ok}")
    if not profile_ok:
        print(f"YData profile message: {profile_msg}")


if __name__ == "__main__":
    main()
