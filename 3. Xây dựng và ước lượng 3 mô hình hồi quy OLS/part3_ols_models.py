import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf


REQUIRED_COLUMNS = [
    "Age",
    "Gender",
    "Education Level",
    "Years of Experience",
    "Salary",
]

EDUCATION_LEVELS = ["High School", "Bachelor", "Master", "PhD"]


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


def prepare_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    out["Salary"] = pd.to_numeric(out["Salary"], errors="raise")
    out["Age"] = pd.to_numeric(out["Age"], errors="raise")
    out["Years of Experience"] = pd.to_numeric(out["Years of Experience"], errors="raise")

    if (out["Salary"] <= 0).any():
        raise ValueError("Salary must be positive to compute lnSalary.")

    if "lnSalary" not in out.columns:
        out["lnSalary"] = np.log(out["Salary"])

    if "Age2" not in out.columns:
        out["Age2"] = out["Age"] ** 2

    out["Gender"] = out["Gender"].astype(str).str.strip()
    out["Education Level"] = out["Education Level"].astype(str).str.strip()

    out["Gender"] = pd.Categorical(out["Gender"])
    if "Female" not in out["Gender"].cat.categories:
        raise ValueError("Gender column must contain 'Female' for base category.")

    available_education = [level for level in EDUCATION_LEVELS if level in set(out["Education Level"])]
    if "High School" not in available_education:
        raise ValueError("Education Level must contain 'High School' for base category.")

    # Keep known education order first and append any unexpected levels at the end.
    extra_levels = [
        level
        for level in sorted(set(out["Education Level"]))
        if level not in EDUCATION_LEVELS
    ]
    ordered_levels = [level for level in EDUCATION_LEVELS if level in available_education] + extra_levels
    out["Education Level"] = pd.Categorical(out["Education Level"], categories=ordered_levels, ordered=True)

    if "Exp_x_Bachelor" not in out.columns:
        out["Exp_x_Bachelor"] = np.where(
            out["Education Level"].astype(str).eq("Bachelor"),
            out["Years of Experience"],
            0.0,
        )
    if "Exp_x_Master" not in out.columns:
        out["Exp_x_Master"] = np.where(
            out["Education Level"].astype(str).eq("Master"),
            out["Years of Experience"],
            0.0,
        )
    if "Exp_x_PhD" not in out.columns:
        out["Exp_x_PhD"] = np.where(
            out["Education Level"].astype(str).eq("PhD"),
            out["Years of Experience"],
            0.0,
        )

    return out


def add_centered_age_terms(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["Age_c"] = out["Age"] - out["Age"].mean()
    out["Age2_c"] = out["Age_c"] ** 2
    return out


def detect_salary_outliers(df: pd.DataFrame) -> pd.DataFrame:
    q1 = float(df["Salary"].quantile(0.25))
    q3 = float(df["Salary"].quantile(0.75))
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    log_salary = np.log(df["Salary"].values)
    log_median = float(np.median(log_salary))
    mad = float(np.median(np.abs(log_salary - log_median)))
    if mad == 0.0:
        modified_z = np.zeros_like(log_salary)
    else:
        modified_z = 0.6745 * (log_salary - log_median) / mad

    report = pd.DataFrame(
        {
            "row_id": df.index,
            "Salary": df["Salary"].values,
            "lower_bound": lower_bound,
            "upper_bound": upper_bound,
            "modified_z_log_salary": modified_z,
        }
    )
    report["is_iqr_outlier"] = (report["Salary"] < lower_bound) | (report["Salary"] > upper_bound)
    report["is_log_mz_outlier"] = report["modified_z_log_salary"].abs() > 3.5
    report["is_hybrid_outlier"] = report["is_iqr_outlier"] | report["is_log_mz_outlier"]
    return report


def apply_outlier_handling(df: pd.DataFrame, outlier_mode: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    report = detect_salary_outliers(df)
    if outlier_mode == "none":
        kept_ids = set(report["row_id"].tolist())
    elif outlier_mode == "iqr":
        kept_ids = set(report.loc[~report["is_iqr_outlier"], "row_id"].tolist())
    else:
        kept_ids = set(report.loc[~report["is_hybrid_outlier"], "row_id"].tolist())

    out = df.loc[df.index.isin(kept_ids)].copy()
    report["kept_in_analysis"] = report["row_id"].isin(set(out.index))
    return out, report


def fit_models(df: pd.DataFrame, cov_type: str):
    formula_1 = (
        "Salary ~ Age + Q('Years of Experience') + "
        "C(Gender, Treatment(reference='Female')) + "
        "C(Q('Education Level'), Treatment(reference='High School'))"
    )

    formula_2 = (
        "lnSalary ~ Age + Q('Years of Experience') + "
        "C(Gender, Treatment(reference='Female')) + "
        "C(Q('Education Level'), Treatment(reference='High School'))"
    )

    formula_3 = (
        "lnSalary ~ Age_c + Age2_c + Q('Years of Experience') + "
        "C(Gender, Treatment(reference='Female')) + "
        "C(Q('Education Level'), Treatment(reference='High School')) + "
        "Exp_x_Bachelor + Exp_x_Master + Exp_x_PhD"
    )

    base_models = {
        "model1_level_level": smf.ols(formula_1, data=df).fit(),
        "model2_log_level": smf.ols(formula_2, data=df).fit(),
        "model3_log_level_extended": smf.ols(formula_3, data=df).fit(),
    }
    if cov_type.lower() == "nonrobust":
        models = base_models
    else:
        models = {
            name: result.get_robustcov_results(cov_type=cov_type)
            for name, result in base_models.items()
        }
    formulas = {
        "model1_level_level": formula_1,
        "model2_log_level": formula_2,
        "model3_log_level_extended": formula_3,
    }
    return models, formulas


def coefficient_table(model_name: str, result) -> pd.DataFrame:
    terms = list(result.model.exog_names)
    coef = np.asarray(result.params)
    std_err = np.asarray(result.bse)
    t_values = np.asarray(result.tvalues)
    p_values = np.asarray(result.pvalues)
    conf_int = result.conf_int()
    conf_arr = np.asarray(conf_int)
    table = pd.DataFrame(
        {
            "model": model_name,
            "term": terms,
            "coef": coef,
            "std_err": std_err,
            "t": t_values,
            "p_value": p_values,
            "ci_lower_95": conf_arr[:, 0],
            "ci_upper_95": conf_arr[:, 1],
        }
    )
    return table


def model_stats_table(model_name: str, result) -> dict[str, float | int | str]:
    return {
        "model": model_name,
        "n_obs": int(result.nobs),
        "r_squared": float(result.rsquared),
        "adj_r_squared": float(result.rsquared_adj),
        "f_stat": float(getattr(result, "fvalue", np.nan)) if getattr(result, "fvalue", None) is not None else np.nan,
        "f_p_value": float(getattr(result, "f_pvalue", np.nan)) if getattr(result, "f_pvalue", None) is not None else np.nan,
        "aic": float(result.aic),
        "bic": float(result.bic),
    }


def write_markdown_summary(
    output_file: Path,
    input_path: Path,
    formulas: dict[str, str],
    stats_df: pd.DataFrame,
    cov_type: str,
    outlier_mode: str,
    n_obs_before: int,
    n_obs_after: int,
) -> None:
    lines = [
        "# Part 3 - OLS Estimation Results",
        "",
        f"- Input data: {input_path.name}",
        "- Base categories: Gender = Female; Education Level = High School",
        f"- Covariance type: {cov_type}",
        f"- Outlier mode: {outlier_mode}",
        f"- Number of observations (before outlier handling): {n_obs_before}",
        f"- Number of observations (after outlier handling): {n_obs_after}",
        "- Model 3 uses centered age terms (Age_c, Age2_c).",
        "",
        "## Model Formulas",
    ]

    for name, formula in formulas.items():
        lines.append(f"- {name}: `{formula}`")

    lines.extend(["", "## Model Fit Statistics", ""])

    stat_cols = ["model", "n_obs", "r_squared", "adj_r_squared", "f_p_value", "aic", "bic"]
    show_df = stats_df[stat_cols].copy()
    lines.append("```text")
    lines.append(show_df.to_string(index=False))
    lines.append("```")
    lines.append("")
    lines.append("## Note")
    lines.append("- Detailed coefficient tables and full summaries are saved in the outputs folder.")

    output_file.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    project_root = Path(__file__).resolve().parents[1]
    default_candidates = [
        Path(__file__).resolve().parent / "Group13_DSEB66A_part1_cleaned.xlsx",
        project_root / "1.Data Cleaning" / "Group13_DSEB66A_part1_cleaned.xlsx",
        project_root / "Group13_DSEB66A.xlsx",
    ]
    default_input = next((p for p in default_candidates if p.exists()), default_candidates[0])

    parser = argparse.ArgumentParser(description="Part 3 OLS model estimation")
    parser.add_argument("--input", default=str(default_input), help="Input file path")
    parser.add_argument("--sheet", default=0, help="Excel sheet index/name")
    parser.add_argument(
        "--output-dir",
        default=str(Path(__file__).resolve().parent / "outputs"),
        help="Output directory",
    )
    parser.add_argument(
        "--cov-type",
        default="nonrobust",
        choices=["nonrobust", "HC1", "HC3"],
        help="Covariance estimator type for standard errors.",
    )
    parser.add_argument(
        "--outlier-mode",
        default="hybrid",
        choices=["none", "iqr", "hybrid"],
        help="Salary outlier handling mode before model estimation. Keep this aligned with Part 4 diagnostics mode.",
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
    df = prepare_features(df)
    n_obs_before = len(df)
    df, outlier_report = apply_outlier_handling(df, args.outlier_mode)
    df = add_centered_age_terms(df)
    n_obs_after = len(df)

    models, formulas = fit_models(df, cov_type=args.cov_type)
    suffix_parts = []
    if args.cov_type.lower() != "nonrobust":
        suffix_parts.append(args.cov_type.lower())
    if args.outlier_mode != "none":
        suffix_parts.append(args.outlier_mode)
    run_suffix = "" if not suffix_parts else "_" + "_".join(suffix_parts)

    all_coef_tables = []
    stats_rows = []
    for name, result in models.items():
        coef_df = coefficient_table(name, result)
        coef_df.to_csv(output_dir / f"{name}_coefficients{run_suffix}.csv", index=False)
        (output_dir / f"{name}_summary{run_suffix}.txt").write_text(result.summary().as_text(), encoding="utf-8")

        all_coef_tables.append(coef_df)
        stats_rows.append(model_stats_table(name, result))

    all_coef_df = pd.concat(all_coef_tables, ignore_index=True)
    all_coef_df.to_csv(output_dir / f"all_models_coefficients{run_suffix}.csv", index=False)

    stats_df = pd.DataFrame(stats_rows)
    stats_df.to_csv(output_dir / f"model_fit_stats{run_suffix}.csv", index=False)
    outlier_report.to_csv(output_dir / f"salary_outlier_report{run_suffix}.csv", index=False)

    write_markdown_summary(
        output_file=output_dir / f"part3_summary{run_suffix}.md",
        input_path=input_path,
        formulas=formulas,
        stats_df=stats_df,
        cov_type=args.cov_type,
        outlier_mode=args.outlier_mode,
        n_obs_before=n_obs_before,
        n_obs_after=n_obs_after,
    )

    print("=== PART 3 OLS ESTIMATION COMPLETED ===")
    print(f"Input file: {input_path}")
    print(f"Rows before outlier handling: {n_obs_before}")
    print(f"Rows after outlier handling: {n_obs_after}")
    print(f"Outlier mode: {args.outlier_mode}")
    print(f"Covariance type: {args.cov_type}")
    print(f"Output directory: {output_dir}")
    print("Saved coefficient tables for 3 models")
    print("Saved model summaries and model fit statistics")
    print("Saved salary outlier report")


if __name__ == "__main__":
    main()
