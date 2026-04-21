
 # Mặc định: drop duplicates, đọc Group13_DSEB66A.xlsx, xuất Group13_DSEB66A_part1_cleaned.xlsx
 #python .\part1_data_cleaning.py
 
 # Giữ duplicates
 #python .\part1_data_cleaning.py --dedup keep --output .\Group13_DSEB66A_part1_keepdup.xlsx


import argparse
from pathlib import Path

import numpy as np
import pandas as pd


EDUCATION_MAP = {
    "bachelor's degree": "Bachelor",
    "bachelor's": "Bachelor",
    "master's degree": "Master",
    "master's": "Master",
    "phd": "PhD",
    "high school": "High School",
}

APOSTROPHE_TRANSLATION = str.maketrans({
    "’": "'",
    "‘": "'",
    "`": "'",
    "´": "'",
    "ʼ": "'",
})


def normalize_education(value: object) -> str:
    key = str(value).strip().lower().translate(APOSTROPHE_TRANSLATION)
    if key in EDUCATION_MAP:
        return EDUCATION_MAP[key]
    raise ValueError(f"Unexpected education value: {value!r}")


def save_dataframe(df: pd.DataFrame, output_path: Path) -> None:
    suffix = output_path.suffix.lower()
    if suffix == ".csv":
        df.to_csv(output_path, index=False)
        return
    if suffix in {".xlsx", ".xls"}:
        df.to_excel(output_path, index=False)
        return
    raise ValueError("Output file must end with .csv, .xlsx, or .xls")


def run_cleaning(input_path: Path, output_path: Path, dedup_mode: str, sheet_name: str | int) -> None:
    df = pd.read_excel(input_path, sheet_name=sheet_name)

    required_columns = ["Age", "Gender", "Education Level", "Years of Experience", "Salary"]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    original_rows = len(df)
    duplicate_rows = int(df.duplicated().sum())

    if dedup_mode == "drop":
        df = df.drop_duplicates().reset_index(drop=True)

    education_before = df["Education Level"].value_counts(dropna=False)
    df["Education Level"] = df["Education Level"].apply(normalize_education)
    education_after = df["Education Level"].value_counts(dropna=False)

    salary = pd.to_numeric(df["Salary"], errors="raise")
    if (salary <= 0).any():
        raise ValueError("Salary must be positive to compute lnSalary.")

    age = pd.to_numeric(df["Age"], errors="raise")
    experience = pd.to_numeric(df["Years of Experience"], errors="raise")

    df["lnSalary"] = np.log(salary)
    df["Age2"] = age**2
    df["Exp_x_Bachelor"] = np.where(df["Education Level"].eq("Bachelor"), experience, 0.0)
    df["Exp_x_Master"] = np.where(df["Education Level"].eq("Master"), experience, 0.0)
    df["Exp_x_PhD"] = np.where(df["Education Level"].eq("PhD"), experience, 0.0)

    save_dataframe(df, output_path)

    print("=== PART 1 DATA CLEANING COMPLETED ===")
    print(f"Input file: {input_path}")
    print(f"Output file: {output_path}")
    print(f"Rows before cleaning: {original_rows}")
    print(f"Detected duplicate rows: {duplicate_rows}")
    print(f"Deduplication mode: {dedup_mode}")
    print(f"Rows after cleaning: {len(df)}")
    print()
    print("Education counts before standardization:")
    print(education_before.to_string())
    print()
    print("Education counts after standardization:")
    print(education_after.to_string())
    print()
    print("Added columns: lnSalary, Age2, Exp_x_Bachelor, Exp_x_Master, Exp_x_PhD")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Part 1 data cleaning workflow for salary dataset.")
    parser.add_argument(
        "--input",
        default="Group13_DSEB66A.xlsx",
        help="Input dataset path (.xlsx)",
    )
    parser.add_argument(
        "--output",
        default="Group13_DSEB66A_part1_cleaned.xlsx",
        help="Output dataset path (.xlsx or .csv)",
    )
    parser.add_argument(
        "--dedup",
        choices=["drop", "keep"],
        default="drop",
        help="Choose whether to drop duplicate rows.",
    )
    parser.add_argument(
        "--sheet",
        default=0,
        help="Excel sheet index/name to read (default: first sheet).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = Path(args.input).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    sheet_name: str | int = args.sheet
    if isinstance(sheet_name, str) and sheet_name.isdigit():
        sheet_name = int(sheet_name)

    run_cleaning(
        input_path=input_path,
        output_path=output_path,
        dedup_mode=args.dedup,
        sheet_name=sheet_name,
    )


if __name__ == "__main__":
    main()
