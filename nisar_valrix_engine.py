import hashlib
import json
import math
import uuid
from datetime import datetime, timezone


class SarEngineException(Exception):
    pass


class NisarValrixFusionEngine:
    """
    Merges Valrix Dual-Block State Verification & Anomaly Auditor (from V1.1 valrix_debugged_code.py)
    with ATMOS GOD Non-Visual Wave/Phase Inversion for NASA-ISRO NISAR SAR Telemetry.
    """

    def __init__(self):
        self.node_ledger = {}
        self.storage_fabric = {}
        self.nisar_catalog = {
            "sundarbans": {
                "granule_id": "NISAR_L2_GCOV_SUNDARBANS_2026",
                "band": "L-Band (1.25 GHz)",
                "wavelength_m": 0.24,
                "baseline_sigma0_db": -11.4,
                "coordinates": "21.9497 N, 89.1833 E",
            },
            "joshimath": {
                "granule_id": "NISAR_L1_RIFG_HIMALAYA_2026",
                "band": "L-Band (1.25 GHz)",
                "wavelength_m": 0.24,
                "baseline_sigma0_db": -8.2,
                "coordinates": "30.5506 N, 79.5660 E",
            },
            "gangotri": {
                "granule_id": "NISAR_L2_GOFF_CRYOSPHERE_2026",
                "band": "L-Band (1.25 GHz)",
                "wavelength_m": 0.24,
                "baseline_sigma0_db": -6.5,
                "coordinates": "30.9250 N, 79.0800 E",
            },
        }

    def register_telemetry_node(self, station_name: str, sensor_id: str):
        token = str(uuid.uuid4())
        sig = hashlib.sha256(f"{station_name}:{sensor_id}:{token}".encode()).hexdigest()
        self.node_ledger[sensor_id] = {
            "station": station_name,
            "secure_sig": sig,
            "status": "ACTIVE",
        }
        return sig

    def compute_insar_deformation(self, aoi_key: str, phase_shift_rad: float, observed_sigma0_db: float):
        if aoi_key not in self.nisar_catalog:
            raise SarEngineException(f"UNKNOWN_AOI: {aoi_key}")

        meta = self.nisar_catalog[aoi_key]
        wavelength = meta["wavelength_m"]

        # DInSAR Line-of-Sight Displacement: delta_R = (lambda / 4*pi) * delta_phi
        los_displacement_cm = ((wavelength / (4.0 * math.pi)) * phase_shift_rad) * 100.0
        backscatter_delta_db = observed_sigma0_db - meta["baseline_sigma0_db"]

        severity = "NOMINAL"
        if abs(los_displacement_cm) > 10.0 or abs(backscatter_delta_db) > 6.0:
            severity = "CRITICAL_ANOMALY"
        elif abs(los_displacement_cm) > 4.0 or abs(backscatter_delta_db) > 3.0:
            severity = "ELEVATED_DRIFT"

        record = {
            "granule_id": meta["granule_id"],
            "coordinates": meta["coordinates"],
            "los_displacement_cm": round(los_displacement_cm, 2),
            "backscatter_delta_db": round(backscatter_delta_db, 2),
            "risk_status": severity,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        }

        # Valrix Dual-Block Tamper-Proof Storage
        payload_str = json.dumps(record, sort_keys=True)
        self.storage_fabric[aoi_key] = {
            "block_a": record,
            "block_b_hash": hashlib.sha256(payload_str.encode()).hexdigest(),
        }
        return self.storage_fabric[aoi_key]


if __name__ == "__main__":
    engine = NisarValrixFusionEngine()
    sig = engine.register_telemetry_node("ISRO-NASA-NISAR-GROUND-01", "SAR-NODE-IN-01")
    print(f"[VALRIX AUTH] Node Registered: {sig[:16]}...")

    result = engine.compute_insar_deformation(
        aoi_key="joshimath",
        phase_shift_rad=-7.4,
        observed_sigma0_db=-14.8,
    )
    print(json.dumps(result, indent=2))
