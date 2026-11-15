import hashlib
import json
import math
import secrets
import uuid
from copy import deepcopy
from datetime import datetime, timezone


PREARM_THETA_THRESHOLD = 0.82
DEMO_STRESS_ALERT_THRESHOLD_PCT = 76.0
MAX_VALIDATED_PHASE_SHIFT = 30.0
MAX_VALIDATED_SIGMA0_DB = 100.0


class SarEngineException(Exception):
    pass


class NisarValrixFusionEngine:
    """
    Scalar synthetic SAR demo calculator with local packet checksums.

    HDF5 granule inspection and raster previews are handled client-side; this
    engine does not decode or calibrate mission imagery.
    """

    def __init__(self):
        self.node_ledger = {}
        self.storage_fabric = {}
        self.nisar_catalog = {
            "sundarbans": {
                "scenario_id": "DEMO_SUNDARBANS",
                "band": "L-Band (1.25 GHz)",
                "wavelength_m": 0.24,
                "baseline_sigma0_db": -11.4,
                "coordinates": "21.9497 N, 89.1833 E",
            },
            "joshimath": {
                "scenario_id": "DEMO_JOSHIMATH",
                "band": "L-Band (1.25 GHz)",
                "wavelength_m": 0.24,
                "baseline_sigma0_db": -8.2,
                "coordinates": "30.5506 N, 79.5660 E",
            },
            "gangotri": {
                "scenario_id": "DEMO_GANGOTRI",
                "band": "L-Band (1.25 GHz)",
                "wavelength_m": 0.24,
                "baseline_sigma0_db": -6.5,
                "coordinates": "30.9250 N, 79.0800 E",
            },
            "california": {
                "scenario_id": "DEMO_SIERRA_FOREST",
                "band": "L-Band (1.25 GHz)",
                "wavelength_m": 0.24,
                "baseline_sigma0_db": -10.1,
                "coordinates": "37.8651 N, 119.5383 W",
            },
        }

    @staticmethod
    def _require_finite_number(value: float, name: str) -> float:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise SarEngineException(f"INVALID_INPUT: {name} must be a finite number")
        try:
            number = float(value)
        except (TypeError, ValueError, OverflowError) as exc:
            raise SarEngineException(f"INVALID_INPUT: {name} must be a finite number") from exc
        if not math.isfinite(number):
            raise SarEngineException(f"INVALID_INPUT: {name} must be a finite number")
        return number

    @staticmethod
    def _record_hash(record: dict) -> str:
        payload = json.dumps(
            record, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    @staticmethod
    def _linearize_db(value_db: float) -> float:
        return math.pow(10.0, value_db / 10.0)

    def _compute_change_signal(self, baseline_sigma0_db: float, observed_sigma0_db: float) -> dict:
        baseline_linear = self._linearize_db(baseline_sigma0_db)
        observed_linear = self._linearize_db(observed_sigma0_db)
        if baseline_linear <= 0.0 or observed_linear <= 0.0:
            raise SarEngineException("INVALID_INPUT: sigma0 values must remain above zero in linear power space")

        log_ratio = math.log(observed_linear / baseline_linear)
        delta_db = observed_sigma0_db - baseline_sigma0_db
        change_magnitude_proxy = max(0.0, min(1.0, abs(log_ratio) / 2.5))
        theta_score = max(
            0.0,
            min(1.0, 0.35 + 0.65 * (abs(delta_db) / 12.0) + 0.5 * change_magnitude_proxy),
        )
        return {
            "backscatter_delta_db": round(delta_db, 4),
            "log_ratio": round(log_ratio, 6),
            "change_magnitude_proxy": round(change_magnitude_proxy, 4),
            "theta_score": round(theta_score, 4),
        }

    def should_prearm_alert(self, theta_score: float) -> bool:
        """Check the prototype threshold only; this does not schedule or run a DAG."""
        theta_score = self._require_finite_number(theta_score, "theta_score")
        if not 0.0 <= theta_score <= 1.0:
            raise SarEngineException("INVALID_INPUT: theta_score must be between 0 and 1")
        return theta_score >= PREARM_THETA_THRESHOLD

    def should_raise_demo_stress_alert(self, stress_pct: float) -> bool:
        stress_pct = self._require_finite_number(stress_pct, "stress_pct")
        if not 10.0 <= stress_pct <= 100.0:
            raise SarEngineException("INVALID_INPUT: stress_pct must be between 10 and 100")
        return stress_pct >= DEMO_STRESS_ALERT_THRESHOLD_PCT

    def register_telemetry_node(self, station_name: str, sensor_id: str):
        if not isinstance(station_name, str) or not station_name.strip():
            raise SarEngineException("INVALID_INPUT: station_name must be a non-empty string")
        if not isinstance(sensor_id, str) or not sensor_id.strip():
            raise SarEngineException("INVALID_INPUT: sensor_id must be a non-empty string")
        station_name = station_name.strip()
        sensor_id = sensor_id.strip()
        token = str(uuid.uuid4())
        sig = hashlib.sha256(
            f"{station_name}:{sensor_id}:{token}:{secrets.token_hex(16)}".encode("utf-8")
        ).hexdigest()
        self.node_ledger[sensor_id] = {
            "station": station_name,
            "registration_hash": sig,
            "status": "REGISTERED",
        }
        return sig

    def compute_insar_deformation(
        self,
        aoi_key: str,
        phase_shift_rad: float,
        observed_sigma0_db: float,
        ionospheric_phase_rad: float = 0.0,
    ):
        if not isinstance(aoi_key, str) or aoi_key not in self.nisar_catalog:
            raise SarEngineException(f"UNKNOWN_AOI: {aoi_key}")

        phase_shift_rad = self._require_finite_number(phase_shift_rad, "phase_shift_rad")
        observed_sigma0_db = self._require_finite_number(observed_sigma0_db, "observed_sigma0_db")
        ionospheric_phase_rad = self._require_finite_number(
            ionospheric_phase_rad, "ionospheric_phase_rad"
        )
        if abs(observed_sigma0_db) > MAX_VALIDATED_SIGMA0_DB:
            raise SarEngineException(
                "INVALID_INPUT: observed_sigma0_db exceeds the supported local processing envelope"
            )
        if abs(phase_shift_rad) > MAX_VALIDATED_PHASE_SHIFT:
            raise SarEngineException(
                "INVALID_INPUT: phase_shift_rad exceeds the supported local processing envelope"
            )

        meta = self.nisar_catalog[aoi_key]
        wavelength = meta["wavelength_m"]
        corrected_phase_rad = phase_shift_rad - ionospheric_phase_rad
        los_displacement_cm = ((wavelength / (4.0 * math.pi)) * corrected_phase_rad) * 100.0

        baseline_sigma0_db = meta["baseline_sigma0_db"]
        change_signal = self._compute_change_signal(baseline_sigma0_db, observed_sigma0_db)
        backscatter_delta_db = change_signal["backscatter_delta_db"]

        if not math.isfinite(los_displacement_cm) or not math.isfinite(backscatter_delta_db):
            raise SarEngineException("INVALID_INPUT: computed values exceed the supported numeric range")

        severity = "NOMINAL_DEMO"
        if abs(los_displacement_cm) > 10.0 or abs(backscatter_delta_db) > 6.0:
            severity = "CRITICAL_ANOMALY_DEMO"
        elif abs(los_displacement_cm) > 4.0 or abs(backscatter_delta_db) > 3.0:
            severity = "ELEVATED_DRIFT_DEMO"

        prearm_ready = self.should_prearm_alert(change_signal["theta_score"])
        record = {
            "scenario_id": meta["scenario_id"],
            "coordinates": meta["coordinates"],
            "phase_difference_unwrapped_rad": phase_shift_rad,
            "ionospheric_phase_rad": ionospheric_phase_rad,
            "corrected_phase_rad": round(corrected_phase_rad, 6),
            "los_displacement_cm": round(los_displacement_cm, 2),
            "backscatter_delta_db": round(backscatter_delta_db, 2),
            "log_ratio": change_signal["log_ratio"],
            "change_magnitude_proxy": change_signal["change_magnitude_proxy"],
            "theta_score": change_signal["theta_score"],
            "prearm_ready": prearm_ready,
            "illustrative_status": severity,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        }

        self.storage_fabric[aoi_key] = {
            "block_a": deepcopy(record),
            "block_b": deepcopy(record),
            "record_sha256": self._record_hash(record),
        }
        return deepcopy(self.storage_fabric[aoi_key])

    def generate_demo_packet(self, aoi_key: str, wipe_pct: float, stress_pct: float):
        if not isinstance(aoi_key, str) or aoi_key not in self.nisar_catalog:
            raise SarEngineException(f"UNKNOWN_AOI: {aoi_key}")
        wipe_pct = self._require_finite_number(wipe_pct, "wipe_pct")
        stress_pct = self._require_finite_number(stress_pct, "stress_pct")
        if not 0.0 <= wipe_pct <= 100.0:
            raise SarEngineException("INVALID_INPUT: wipe_pct must be between 0 and 100")
        if not 10.0 <= stress_pct <= 100.0:
            raise SarEngineException("INVALID_INPUT: stress_pct must be between 10 and 100")

        meta = self.nisar_catalog[aoi_key]
        baseline = meta["baseline_sigma0_db"]
        factor = max(0.2, min(1.6, stress_pct / 68.0))
        delta_db = -(4.2 * factor)
        observed_sigma = baseline + delta_db
        phase = -((meta["baseline_sigma0_db"] - observed_sigma) * 1.4 + (wipe_pct / 100.0) * 5.0)
        los_cm = ((meta["wavelength_m"] / (4.0 * math.pi)) * phase) * 100.0
        gamma = max(0.12, 0.94 - 0.52 * factor)
        area_km2 = max(1.0, abs(delta_db) * 8.5)

        packet = {
            "A1_surface": {
                "aoi": aoi_key,
                "coordinates": meta["coordinates"],
                "wipe_pct": round(wipe_pct, 1),
                "stress_pct": round(stress_pct, 1),
            },
            "B1_backscatter": {
                "baseline_sigma0_db": round(baseline, 2),
                "observed_sigma0_db": round(observed_sigma, 2),
                "delta_sigma0_db": round(delta_db, 2),
            },
            "C1_sync": {
                "phase_rad": round(phase, 4),
                "los_displacement_cm": round(los_cm, 2),
                "coherence_proxy": round(gamma, 3),
                "area_km2": round(area_km2, 2),
                "theta": round(min(0.99, max(0.0, 0.35 + 0.65 * (abs(delta_db) / 12.0) + 0.5 * abs(math.log(max(0.01, gamma))))), 4),
                "demo_stress_alert": self.should_raise_demo_stress_alert(stress_pct),
            },
        }
        packet_payload = {
            key: packet[key] for key in ("A1_surface", "B1_backscatter", "C1_sync")
        }
        packet["seal"] = {
            "sha256": hashlib.sha256(
                json.dumps(packet_payload, sort_keys=True).encode("utf-8")
            ).hexdigest(),
            "status": "checksum-local-v1",
        }
        return packet

    def read_verified_record(self, aoi_key: str):
        if not isinstance(aoi_key, str):
            return None
        stored = self.storage_fabric.get(aoi_key)
        if not isinstance(stored, dict):
            return None
        expected_hash = stored.get("record_sha256")
        if not isinstance(expected_hash, str):
            return None
        for block_name in ("block_a", "block_b"):
            record = stored.get(block_name)
            if not isinstance(record, dict):
                continue
            try:
                valid = secrets.compare_digest(self._record_hash(record), expected_hash)
            except (TypeError, ValueError, RecursionError):
                valid = False
            if valid:
                return {"record": deepcopy(record), "source": block_name.upper()}
        return None

    def verify_integrity(self, aoi_key: str) -> bool:
        return self.read_verified_record(aoi_key) is not None


if __name__ == "__main__":
    engine = NisarValrixFusionEngine()
    sig = engine.register_telemetry_node("DEMO-GROUND-01", "SAR-NODE-DEMO-01")
    print(f"[LOCAL REGISTRATION] Node fingerprint: {sig[:16]}...")

    packet = engine.generate_demo_packet("joshimath", 52.0, 68.0)
    print(json.dumps(packet, indent=2))
    packet_payload = {
        key: packet[key] for key in ("A1_surface", "B1_backscatter", "C1_sync")
    }
    expected_hash = hashlib.sha256(
        json.dumps(packet_payload, sort_keys=True).encode("utf-8")
    ).hexdigest()
    checksum_valid = secrets.compare_digest(packet["seal"]["sha256"], expected_hash)
    print(f"Local packet checksum valid: {checksum_valid}")
