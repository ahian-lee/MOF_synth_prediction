#!/usr/bin/env python
"""
Batch thermal-stability prediction for MOFs using an existing MOFSimplify setup.
"""

import argparse
import os
import shutil
import subprocess
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"


RACS = [
    "D_func-I-0-all", "D_func-I-1-all", "D_func-I-2-all", "D_func-I-3-all",
    "D_func-S-0-all", "D_func-S-1-all", "D_func-S-2-all", "D_func-S-3-all",
    "D_func-T-0-all", "D_func-T-1-all", "D_func-T-2-all", "D_func-T-3-all",
    "D_func-Z-0-all", "D_func-Z-1-all", "D_func-Z-2-all", "D_func-Z-3-all",
    "D_func-chi-0-all", "D_func-chi-1-all", "D_func-chi-2-all", "D_func-chi-3-all",
    "D_lc-I-0-all", "D_lc-I-1-all", "D_lc-I-2-all", "D_lc-I-3-all",
    "D_lc-S-0-all", "D_lc-S-1-all", "D_lc-S-2-all", "D_lc-S-3-all",
    "D_lc-T-0-all", "D_lc-T-1-all", "D_lc-T-2-all", "D_lc-T-3-all",
    "D_lc-Z-0-all", "D_lc-Z-1-all", "D_lc-Z-2-all", "D_lc-Z-3-all",
    "D_lc-chi-0-all", "D_lc-chi-1-all", "D_lc-chi-2-all", "D_lc-chi-3-all",
    "D_mc-I-0-all", "D_mc-I-1-all", "D_mc-I-2-all", "D_mc-I-3-all",
    "D_mc-S-0-all", "D_mc-S-1-all", "D_mc-S-2-all", "D_mc-S-3-all",
    "D_mc-T-0-all", "D_mc-T-1-all", "D_mc-T-2-all", "D_mc-T-3-all",
    "D_mc-Z-0-all", "D_mc-Z-1-all", "D_mc-Z-2-all", "D_mc-Z-3-all",
    "D_mc-chi-0-all", "D_mc-chi-1-all", "D_mc-chi-2-all", "D_mc-chi-3-all",
    "f-I-0-all", "f-I-1-all", "f-I-2-all", "f-I-3-all",
    "f-S-0-all", "f-S-1-all", "f-S-2-all", "f-S-3-all",
    "f-T-0-all", "f-T-1-all", "f-T-2-all", "f-T-3-all",
    "f-Z-0-all", "f-Z-1-all", "f-Z-2-all", "f-Z-3-all",
    "f-chi-0-all", "f-chi-1-all", "f-chi-2-all", "f-chi-3-all",
    "f-lig-I-0", "f-lig-I-1", "f-lig-I-2", "f-lig-I-3",
    "f-lig-S-0", "f-lig-S-1", "f-lig-S-2", "f-lig-S-3",
    "f-lig-T-0", "f-lig-T-1", "f-lig-T-2", "f-lig-T-3",
    "f-lig-Z-0", "f-lig-Z-1", "f-lig-Z-2", "f-lig-Z-3",
    "f-lig-chi-0", "f-lig-chi-1", "f-lig-chi-2", "f-lig-chi-3",
    "func-I-0-all", "func-I-1-all", "func-I-2-all", "func-I-3-all",
    "func-S-0-all", "func-S-1-all", "func-S-2-all", "func-S-3-all",
    "func-T-0-all", "func-T-1-all", "func-T-2-all", "func-T-3-all",
    "func-Z-0-all", "func-Z-1-all", "func-Z-2-all", "func-Z-3-all",
    "func-chi-0-all", "func-chi-1-all", "func-chi-2-all", "func-chi-3-all",
    "lc-I-0-all", "lc-I-1-all", "lc-I-2-all", "lc-I-3-all",
    "lc-S-0-all", "lc-S-1-all", "lc-S-2-all", "lc-S-3-all",
    "lc-T-0-all", "lc-T-1-all", "lc-T-2-all", "lc-T-3-all",
    "lc-Z-0-all", "lc-Z-1-all", "lc-Z-2-all", "lc-Z-3-all",
    "lc-chi-0-all", "lc-chi-1-all", "lc-chi-2-all", "lc-chi-3-all",
    "mc-I-0-all", "mc-I-1-all", "mc-I-2-all", "mc-I-3-all",
    "mc-S-0-all", "mc-S-1-all", "mc-S-2-all", "mc-S-3-all",
    "mc-T-0-all", "mc-T-1-all", "mc-T-2-all", "mc-T-3-all",
    "mc-Z-0-all", "mc-Z-1-all", "mc-Z-2-all", "mc-Z-3-all",
    "mc-chi-0-all", "mc-chi-1-all", "mc-chi-2-all", "mc-chi-3-all",
]

GEO = [
    "Df", "Di", "Dif", "GPOAV", "GPONAV", "GPOV", "GSA", "POAV",
    "POAV_vol_frac", "PONAV", "PONAV_vol_frac", "VPOV", "VSA", "cell_v",
]


def create_feature_mapping():
    mapping = {}

    for prefix in ["lc", "func", "D_lc", "D_func"]:
        for prop in ["chi", "Z", "I", "T", "S", "alpha"]:
            for depth in range(4):
                mapping[f"{prefix}-{prop}-{depth}"] = f"{prefix}-{prop}-{depth}-all"

    for prop in ["chi", "Z", "I", "T", "S"]:
        for depth in range(4):
            mapping[f"f-sbu-{prop}-{depth}"] = f"f-{prop}-{depth}-all"

    for prefix in ["mc", "D_mc"]:
        for prop in ["chi", "Z", "I", "T", "S"]:
            for depth in range(4):
                mapping[f"{prefix}-{prop}-{depth}"] = f"{prefix}-{prop}-{depth}-all"

    for prop in ["chi", "Z", "I", "T", "S"]:
        for depth in range(4):
            mapping[f"f-link-{prop}-{depth}"] = f"f-lig-{prop}-{depth}"

    return mapping


class BatchThermalPredictor:
    def __init__(self, mofsimplify_root, output_dir):
        self.mofsimplify_root = Path(mofsimplify_root).resolve()
        self.output_dir = Path(output_dir).resolve()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.feature_mapping = create_feature_mapping()
        self._init_runtime()
        self._load_model()

    def _init_runtime(self):
        sys.path.insert(0, str(self.mofsimplify_root))
        from molSimplify.Informatics.MOF.MOF_descriptors import get_MOF_descriptors
        import tensorflow as tf

        self.get_MOF_descriptors = get_MOF_descriptors
        self.tf = tf
        self.zeo_exe = self.mofsimplify_root / "zeo++-0.3" / "network"
        self.ann_dir = self.mofsimplify_root / "model" / "thermal" / "ANN"

        required = [
            self.zeo_exe,
            self.ann_dir / "final_model_T_few_epochs.h5",
            self.ann_dir / "train.csv",
        ]
        missing = [str(path) for path in required if not path.exists()]
        if missing:
            raise FileNotFoundError("Missing MOFSimplify thermal assets:\n" + "\n".join(missing))

    def _load_model(self):
        self.model = self.tf.keras.models.load_model(
            str(self.ann_dir / "final_model_T_few_epochs.h5"),
            compile=False,
        )
        self.df_train = pd.read_csv(self.ann_dir / "train.csv")
        all_features = RACS + GEO
        filtered = self.df_train.loc[:, (self.df_train != self.df_train.iloc[0]).any()]
        self.feature_cols = [col for col in filtered.columns if col in all_features]
        self.x_scaler = StandardScaler().fit(self.df_train[self.feature_cols].values)
        self.y_scaler = StandardScaler().fit(self.df_train["T"].values.reshape(-1, 1))
        self.feature_means = {
            col: float(self.df_train[col].mean())
            for col in self.feature_cols
        }

    def _run_zeopp(self, cif_path, temp_dir, name):
        geo_data = {}
        pd_file = temp_dir / f"{name}_pd.txt"
        sa_file = temp_dir / f"{name}_sa.txt"
        pov_file = temp_dir / f"{name}_pov.txt"

        commands = [
            [str(self.zeo_exe), "-ha", "-res", str(pd_file), str(cif_path)],
            [str(self.zeo_exe), "-sa", "1.86", "1.86", "10000", str(sa_file), str(cif_path)],
            [str(self.zeo_exe), "-volpo", "1.86", "1.86", "10000", str(pov_file), str(cif_path)],
        ]
        for cmd in commands:
            try:
                subprocess.run(cmd, capture_output=True, timeout=120, check=False)
            except Exception:
                pass

        try:
            if pd_file.exists():
                parts = pd_file.read_text().strip().split()
                if len(parts) >= 3:
                    geo_data["Di"] = float(parts[-3])
                    geo_data["Df"] = float(parts[-2])
                    geo_data["Dif"] = float(parts[-1])

            if pov_file.exists():
                content = pov_file.read_text()
                density = 1.0
                if "Density:" in content:
                    density = float(content.split("Density:")[1].split()[0])
                if "Unitcell_volume:" in content:
                    geo_data["cell_v"] = float(content.split("Unitcell_volume:")[1].split()[0])
                if "POAV_A^3:" in content:
                    geo_data["POAV"] = float(content.split("POAV_A^3:")[1].split()[0])
                if "PONAV_A^3:" in content:
                    geo_data["PONAV"] = float(content.split("PONAV_A^3:")[1].split()[0])
                if "POAV_cm^3/g:" in content:
                    geo_data["GPOAV"] = float(content.split("POAV_cm^3/g:")[1].split()[0])
                if "PONAV_cm^3/g:" in content:
                    geo_data["GPONAV"] = float(content.split("PONAV_cm^3/g:")[1].split()[0])
                if "POAV_Volume_fraction:" in content:
                    geo_data["POAV_vol_frac"] = float(content.split("POAV_Volume_fraction:")[1].split()[0])
                if "PONAV_Volume_fraction:" in content:
                    geo_data["PONAV_vol_frac"] = float(content.split("PONAV_Volume_fraction:")[1].split()[0])
                    vpov = geo_data.get("POAV_vol_frac", 0.0) + geo_data.get("PONAV_vol_frac", 0.0)
                    geo_data["VPOV"] = vpov
                    geo_data["GPOV"] = vpov / density if density else 0.0

            if sa_file.exists():
                content = sa_file.read_text()
                if "ASA_m^2/cm^3:" in content:
                    geo_data["VSA"] = float(content.split("ASA_m^2/cm^3:")[1].split()[0])
                if "ASA_m^2/g:" in content:
                    geo_data["GSA"] = float(content.split("ASA_m^2/g:")[1].split()[0])
        except Exception:
            pass

        return geo_data

    def _generate_rac_features(self, cif_path, temp_dir, name):
        xyz_path = temp_dir / f"{name}.xyz"
        try:
            names, _ = self.get_MOF_descriptors(
                data=str(cif_path),
                depth=3,
                path=str(temp_dir) + "/",
                xyz_path=str(xyz_path),
            )
            if len(names) <= 1:
                return False, "empty RAC descriptor output"
            return True, None
        except Exception as exc:
            return False, str(exc)

    def _build_feature_dict(self, temp_dir, geo_data):
        lc_df = pd.read_csv(temp_dir / "lc_descriptors.csv").select_dtypes(include=[np.number])
        sbu_df = pd.read_csv(temp_dir / "sbu_descriptors.csv").select_dtypes(include=[np.number])
        linker_df = pd.read_csv(temp_dir / "linker_descriptors.csv").select_dtypes(include=[np.number])

        feature_dict = dict(geo_data)
        for frame in [lc_df, sbu_df, linker_df]:
            for col in frame.columns:
                mapped = self.feature_mapping.get(col, col)
                if mapped not in feature_dict:
                    feature_dict[mapped] = float(frame[col].mean())
        return feature_dict

    def _predict(self, feature_dict):
        x = np.zeros((1, len(self.feature_cols)))
        matched = 0
        for i, col in enumerate(self.feature_cols):
            value = feature_dict.get(col, self.feature_means[col])
            if value is not None and not np.isnan(value):
                x[0, i] = value
                if col in feature_dict:
                    matched += 1
            else:
                x[0, i] = self.feature_means[col]
        x_scaled = self.x_scaler.transform(x)
        pred_scaled = self.model.predict(x_scaled.astype(np.float32), verbose=0)
        pred = float(self.y_scaler.inverse_transform(pred_scaled)[0][0])
        return round(pred, 1), matched

    def predict_single(self, cif_path, cleanup=True):
        cif_path = Path(cif_path).resolve()
        name = cif_path.stem
        temp_dir = self.output_dir / f"temp_{name}"
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        temp_dir.mkdir(parents=True)

        cif_copy = temp_dir / f"{name}.cif"
        shutil.copy(cif_path, cif_copy)

        geo_data = self._run_zeopp(cif_copy, temp_dir, name)
        success, error = self._generate_rac_features(cif_copy, temp_dir, name)
        if not success:
            return {"name": name, "status": "FAILED", "reason": f"rac: {error}"}

        try:
            feature_dict = self._build_feature_dict(temp_dir, geo_data)
            prediction, matched = self._predict(feature_dict)
        except Exception as exc:
            return {"name": name, "status": "FAILED", "reason": str(exc)}
        finally:
            if cleanup and temp_dir.exists():
                shutil.rmtree(temp_dir)

        return {
            "name": name,
            "status": "SUCCESS",
            "thermal_stability_C": prediction,
            "matched_features": matched,
        }

    def predict_batch(self, cif_folder, output_csv):
        cif_folder = Path(cif_folder).resolve()
        cif_files = sorted(cif_folder.glob("*.cif"))
        results = [self.predict_single(cif_path) for cif_path in cif_files]
        df = pd.DataFrame(results)
        output_path = self.output_dir / output_csv
        df.to_csv(output_path, index=False)
        return output_path, df


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mofsimplify-root", required=True, help="Path to an existing upstream MOFSimplify checkout")
    parser.add_argument("--cif-folder", required=True, help="Directory containing input CIF files")
    parser.add_argument("--output-dir", required=True, help="Directory for temporary files and final CSV")
    parser.add_argument("--output-csv", default="thermal_predictions.csv", help="Output CSV filename")
    return parser.parse_args()


def main():
    args = parse_args()
    predictor = BatchThermalPredictor(args.mofsimplify_root, args.output_dir)
    output_path, df = predictor.predict_batch(args.cif_folder, args.output_csv)
    success = int((df["status"] == "SUCCESS").sum()) if "status" in df else 0
    print(f"Processed {len(df)} CIFs")
    print(f"Successful predictions: {success}")
    print(f"Saved results to: {output_path}")


if __name__ == "__main__":
    main()
