import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from statsmodels.graphics.gofplots import qqplot
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.stattools import jarque_bera


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


def detect_salary_outliers_iqr(df: pd.DataFrame) -> pd.DataFrame:
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
            "q1": q1,
            "q3": q3,
            "iqr": iqr,
            "lower_bound": lower_bound,
            "upper_bound": upper_bound,
            "log_salary": log_salary,
            "modified_z_log_salary": modified_z,
        }
    )
    report["is_iqr_outlier"] = (report["Salary"] < lower_bound) | (report["Salary"] > upper_bound)
    report["is_low_outlier"] = report["Salary"] < lower_bound
    report["is_high_outlier"] = report["Salary"] > upper_bound
    report["is_log_mz_outlier"] = report["modified_z_log_salary"].abs() > 3.5
    report["is_log_mz_low_outlier"] = report["modified_z_log_salary"] < -3.5
    report["is_hybrid_outlier"] = report["is_iqr_outlier"] | report["is_log_mz_outlier"]
    return report


def apply_outlier_handling(df: pd.DataFrame, outlier_mode: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    report = detect_salary_outliers_iqr(df)
    if outlier_mode == "none":
        kept_ids = set(report["row_id"].tolist())
    elif outlier_mode == "iqr":
        kept_ids = set(report.loc[~report["is_iqr_outlier"], "row_id"].tolist())
    else:
        kept_ids = set(report.loc[~report["is_hybrid_outlier"], "row_id"].tolist())

    out = df.loc[df.index.isin(kept_ids)].copy()
    report["kept_in_analysis"] = report["row_id"].isin(set(out.index))
    return out, report


def get_formulas() -> dict[str, str]:
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

    return {
        "model1_level_level": formula_1,
        "model2_log_level": formula_2,
        "model3_log_level_extended": formula_3,
    }


def fit_nonrobust_models(df: pd.DataFrame, formulas: dict[str, str]):
    return {name: smf.ols(formula, data=df).fit() for name, formula in formulas.items()}


def coefficient_table(model_name: str, result, cov_type: str) -> pd.DataFrame:
    terms = list(result.model.exog_names)
    coef = np.asarray(result.params)
    std_err = np.asarray(result.bse)
    t_values = np.asarray(result.tvalues)
    p_values = np.asarray(result.pvalues)
    conf_arr = np.asarray(result.conf_int())

    return pd.DataFrame(
        {
            "model": model_name,
            "cov_type": cov_type,
            "term": terms,
            "coef": coef,
            "std_err": std_err,
            "t": t_values,
            "p_value": p_values,
            "ci_lower_95": conf_arr[:, 0],
            "ci_upper_95": conf_arr[:, 1],
        }
    )


def compute_vif_table(model_name: str, result) -> pd.DataFrame:
    exog = np.asarray(result.model.exog)
    names = list(result.model.exog_names)

    rows = []
    for idx, name in enumerate(names):
        if name.lower() == "intercept":
            continue
        vif = variance_inflation_factor(exog, idx)
        rows.append({"model": model_name, "variable": name, "vif": float(vif)})

    return pd.DataFrame(rows)


def compute_bp_table(model_name: str, result) -> pd.DataFrame:
    lm_stat, lm_p_value, f_stat, f_p_value = het_breuschpagan(result.resid, result.model.exog)
    return pd.DataFrame(
        [
            {
                "model": model_name,
                "lm_stat": float(lm_stat),
                "lm_p_value": float(lm_p_value),
                "f_stat": float(f_stat),
                "f_p_value": float(f_p_value),
                "heteroskedasticity_at_5pct": bool(f_p_value < 0.05),
            }
        ]
    )


def compute_jb_table(model_name: str, result) -> pd.DataFrame:
    jb_stat, jb_p_value, skew, kurtosis = jarque_bera(result.resid)
    return pd.DataFrame(
        [
            {
                "model": model_name,
                "jb_stat": float(jb_stat),
                "jb_p_value": float(jb_p_value),
                "skew": float(skew),
                "kurtosis": float(kurtosis),
                "normality_at_5pct": bool(jb_p_value >= 0.05),
            }
        ]
    )


def save_qq_plot(model_name: str, result, output_file: Path) -> None:
    fig = qqplot(result.resid, line="45", fit=True)
    plt.title(f"QQ Plot of Residuals: {model_name}")
    plt.tight_layout()
    fig.savefig(output_file, dpi=150)
    plt.close(fig)


def write_summary(
    output_file: Path,
    input_path: Path,
    n_obs_before: int,
    n_obs_after: int,
    outlier_mode: str,
    outlier_report: pd.DataFrame,
    vif_df: pd.DataFrame,
    bp_df: pd.DataFrame,
    jb_df: pd.DataFrame,
) -> None:
    high_vif = vif_df[vif_df["vif"] >= 8].sort_values(["model", "vif"], ascending=[True, False])
    hetero_models = bp_df[bp_df["heteroskedasticity_at_5pct"]]["model"].tolist()

    lines = [
        "# Part 4 - Diagnostics Summary",
        "",
        f"- Input data: {input_path.name}",
        f"- Number of observations (before outlier handling): {n_obs_before}",
        f"- Number of observations (after outlier handling): {n_obs_after}",
        f"- Salary outlier mode: {outlier_mode}",
        "- Alpha level: 5%",
        "",
        "## Key Findings",
    ]

    n_iqr_outliers = int(outlier_report["is_iqr_outlier"].sum())
    n_low_outliers = int(outlier_report["is_low_outlier"].sum())
    n_high_outliers = int(outlier_report["is_high_outlier"].sum())
    n_log_outliers = int(outlier_report["is_log_mz_outlier"].sum())
    n_hybrid_outliers = int(outlier_report["is_hybrid_outlier"].sum())
    lines.append(
        "- Salary outlier detection (IQR rule): "
        f"{n_iqr_outliers} outlier(s), including {n_low_outliers} low and {n_high_outliers} high outlier(s)."
    )
    lines.append(
        "- Salary outlier detection (log modified z-score): "
        f"{n_log_outliers} outlier(s). Hybrid flagged outliers: {n_hybrid_outliers}."
    )
    lines.append("- Model 3 uses centered age terms (Age_c, Age2_c) to reduce structural multicollinearity.")

    if high_vif.empty:
        lines.append("- VIF: No variable with VIF >= 8.")
    else:
        lines.append("- VIF: High multicollinearity exists for variables listed below (VIF >= 8).")
        lines.append("```text")
        lines.append(high_vif.to_string(index=False))
        lines.append("```")

    if hetero_models:
        lines.append("- Breusch-Pagan: Heteroskedasticity detected in model(s): " + ", ".join(hetero_models))
        lines.append("- Recommendation: Use HC3 robust standard errors for inference.")
    else:
        lines.append("- Breusch-Pagan: No heteroskedasticity detected at 5%.")

    non_normal_models = jb_df[~jb_df["normality_at_5pct"]]["model"].tolist()
    if non_normal_models:
        lines.append("- Jarque-Bera: Residual normality rejected in model(s): " + ", ".join(non_normal_models))
    else:
        lines.append("- Jarque-Bera: Residual normality not rejected at 5% for all models.")

    lines.extend(
        [
            "",
            "## Output Files",
            "- vif_table.csv",
            "- breusch_pagan_results.csv",
            "- jarque_bera_results.csv",
            "- all_models_coefficients_nonrobust.csv",
            "- all_models_coefficients_hc3.csv",
            "- salary_outlier_report.csv",
            "- qqplot_model1_level_level.png",
            "- qqplot_model2_log_level.png",
            "- qqplot_model3_log_level_extended.png",
        ]
    )

    output_file.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    project_root = Path(__file__).resolve().parents[1]
    default_candidates = [
        Path(__file__).resolve().parent / "Group13_DSEB66A_part1_cleaned.xlsx",
        project_root / "1.Data Cleaning" / "Group13_DSEB66A_part1_cleaned.xlsx",
        project_root / "Group13_DSEB66A.xlsx",
    ]
    default_input = next((p for p in default_candidates if p.exists()), default_candidates[0])

    parser = argparse.ArgumentParser(description="Part 4 diagnostics for OLS models")
    parser.add_argument("--input", default=str(default_input), help="Input file path")
    parser.add_argument("--sheet", default=0, help="Excel sheet index/name")
    parser.add_argument(
        "--output-dir",
        default=str(Path(__file__).resolve().parent / "outputs"),
        help="Output directory",
    )
    parser.add_argument(
        "--outlier-mode",
        default="hybrid",
        choices=["none", "iqr", "hybrid"],
        help="Salary outlier handling mode. 'hybrid' drops IQR or log-modified-z outliers.",
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

    raw_df = load_dataframe(input_path, sheet_name=sheet_name)
    check_required_columns(raw_df)
    raw_df = prepare_features(raw_df)

    n_obs_before = len(raw_df)
    df, outlier_report = apply_outlier_handling(raw_df, args.outlier_mode)
    df = add_centered_age_terms(df)
    n_obs_after = len(df)

    formulas = get_formulas()
    nonrobust_models = fit_nonrobust_models(df, formulas)

    vif_tables = []
    bp_tables = []
    jb_tables = []
    nonrobust_coef_tables = []
    hc3_coef_tables = []

    for model_name, result in nonrobust_models.items():
        vif_tables.append(compute_vif_table(model_name, result))
        bp_tables.append(compute_bp_table(model_name, result))
        jb_tables.append(compute_jb_table(model_name, result))

        nonrobust_coef_tables.append(coefficient_table(model_name, result, "nonrobust"))

        hc3_result = result.get_robustcov_results(cov_type="HC3")
        hc3_coef_tables.append(coefficient_table(model_name, hc3_result, "HC3"))

        save_qq_plot(model_name, result, output_dir / f"qqplot_{model_name}.png")

    vif_df = pd.concat(vif_tables, ignore_index=True).sort_values(["model", "vif"], ascending=[True, False])
    bp_df = pd.concat(bp_tables, ignore_index=True)
    jb_df = pd.concat(jb_tables, ignore_index=True)

    nonrobust_coef_df = pd.concat(nonrobust_coef_tables, ignore_index=True)
    hc3_coef_df = pd.concat(hc3_coef_tables, ignore_index=True)

    vif_df.to_csv(output_dir / "vif_table.csv", index=False)
    bp_df.to_csv(output_dir / "breusch_pagan_results.csv", index=False)
    jb_df.to_csv(output_dir / "jarque_bera_results.csv", index=False)
    outlier_report.to_csv(output_dir / "salary_outlier_report.csv", index=False)

    nonrobust_coef_df.to_csv(output_dir / "all_models_coefficients_nonrobust.csv", index=False)
    hc3_coef_df.to_csv(output_dir / "all_models_coefficients_hc3.csv", index=False)

    write_summary(
        output_file=output_dir / "part4_summary.md",
        input_path=input_path,
        n_obs_before=n_obs_before,
        n_obs_after=n_obs_after,
        outlier_mode=args.outlier_mode,
        outlier_report=outlier_report,
        vif_df=vif_df,
        bp_df=bp_df,
        jb_df=jb_df,
    )

    print("=== PART 4 DIAGNOSTICS COMPLETED ===")
    print(f"Input file: {input_path}")
    print(f"Rows before outlier handling: {n_obs_before}")
    print(f"Rows after outlier handling: {n_obs_after}")
    print(f"Outlier mode: {args.outlier_mode}")
    print(f"Output directory: {output_dir}")
    print("Saved: vif_table.csv, breusch_pagan_results.csv, jarque_bera_results.csv")
    print("Saved: all_models_coefficients_nonrobust.csv, all_models_coefficients_hc3.csv")
    print("Saved: salary_outlier_report.csv")
    print("Saved QQ plots for all 3 models")


if __name__ == "__main__":
    main()
