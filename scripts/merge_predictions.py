#!/usr/bin/env python

import argparse
import pandas as pd


def normalize_synth(df):
    columns = list(df.columns)
    if columns[:3] == ["id", "CLscore", "bagging"]:
        return df.rename(columns={"id": "mof_id"})
    if columns[:3] == ["crystal_id", "CLscore", "bagging"]:
        return df.rename(columns={"crystal_id": "mof_id"})
    if columns[:3] == ["crystal_id", "CLscore"]:
        return df.rename(columns={"crystal_id": "mof_id"})
    return df


def normalize_thermal(df):
    if "name" in df.columns and "mof_id" not in df.columns:
        return df.rename(columns={"name": "mof_id"})
    return df


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--synth-csv", required=True)
    parser.add_argument("--thermal-csv", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    synth = normalize_synth(pd.read_csv(args.synth_csv))
    thermal = normalize_thermal(pd.read_csv(args.thermal_csv))
    merged = synth.merge(thermal, on="mof_id", how="outer")
    merged.to_csv(args.output, index=False)
    print(f"Saved merged predictions to: {args.output}")


if __name__ == "__main__":
    main()
