# G-Effects Model Manual

## Table of Contents

1. [Overview](#overview)
2. [HRV Integration for G-LOC Prediction](#hrv-integration-for-g-loc-prediction)
3. [Polar H10 Implementation Guide](#polar-h10-implementation-guide)
4. [API Reference](#api-reference)
5. [Validation Protocols](#validation-protocols)

---

## Overview

This manual provides detailed technical guidance for extending the CGEM-based G-LOC prediction model with Heart Rate Variability (HRV) monitoring capabilities. The goal is to enable real-time, individualized prediction of G-induced loss of consciousness using wearable sensors in operational aviation environments.

---

## HRV Integration for G-LOC Prediction

### Physiological Rationale

The autonomic nervous system (ANS) plays a critical role in cardiovascular responses to +Gz acceleration:

1. **Baroreflex Response**: Under +Gz, blood pools in lower extremities, reducing venous return. The baroreflex detects decreased arterial pressure and triggers sympathetic activation.

2. **Heart Rate Dynamics**: Initial HR increase is mediated by vagal withdrawal (parasympathetic inhibition), followed by sympathetic augmentation. This sequence is detectable in HRV metrics.

3. **Pre-Syncopal Signature**: Before syncope, characteristic HRV changes occur:
   - Decreased RMSSD (vagal withdrawal exhausted)
   - Increased LF/HF ratio (sympathetic dominance)
   - Reduced sample entropy (loss of complexity)
   - Altered DFA scaling (breakdown of fractal dynamics)

4. **Individual Thresholds**: G-tolerance varies significantly between individuals. HRV baselines and response patterns provide personalization data that population-averaged models cannot capture.

### HRV Metrics for G-LOC Prediction

#### Time-Domain Metrics

| Metric | Formula | Interpretation | G-LOC Relevance |
|--------|---------|----------------|-----------------|
| Mean RR | `Σ(RRi) / N` | Average interval (ms) | Decreases under +Gz |
| SDNN | `√(Σ(RRi - mean)² / (N-1))` | Overall variability | Decreases before LOC |
| RMSSD | `√(Σ(RRi+1 - RRi)² / (N-1))` | Vagal tone marker | Sharp drop pre-LOC |
| pNN50 | `100 × (count(|ΔRR| > 50ms) / N)` | Parasympathetic index | Approaches zero pre-LOC |
| SDSD | `SD of successive differences` | Short-term variability | Sensitive to G-onset |

**Implementation Note**: Compute on 30-second sliding windows with 5-second updates for balance between responsiveness and stability.

#### Frequency-Domain Metrics

| Band | Frequency Range | Primary Driver | G-LOC Indicator |
|------|-----------------|----------------|-----------------|
| VLF | 0.003–0.04 Hz | Thermoregulation, RAAS | Limited use in short segments |
| LF | 0.04–0.15 Hz | Baroreflex, sympathetic | Increases with G-stress |
| HF | 0.15–0.4 Hz | Respiratory sinus arrhythmia | Decreases with sympathetic activation |
| LF/HF | Ratio | Sympathovagal balance | >3.5 associated with impending LOC |

**Implementation Note**: Use Welch's method with Hanning window for spectral estimation. Minimum 2-minute window for reliable VLF; 30 seconds sufficient for LF/HF.

#### Nonlinear Metrics

| Metric | Description | Calculation | G-LOC Signature |
|--------|-------------|-------------|-----------------|
| SD1 | Poincaré plot short-axis | Beat-to-beat variability | Decreases pre-LOC |
| SD2 | Poincaré plot long-axis | Longer-term variability | Indicates ANS exhaustion |
| SD1/SD2 | Ratio | Vagal/overall balance | Approaches 1.0 before LOC |
| SampEn | Sample Entropy | Signal unpredictability | Drops before syncope |
| ApEn | Approximate Entropy | Pattern regularity | Loss of complexity |
| DFA α1 | Short-term scaling (4–16 beats) | Fractal correlation | Shifts from ~1.0 |
| DFA α2 | Long-term scaling (16–64 beats) | Longer correlations | Less sensitive |

**Implementation Note**: SampEn parameters typically m=2, r=0.2×SDNN. DFA requires minimum 256 beats for reliable α2.

### Machine Learning Approach

#### Feature Vector Design

For each 30-second analysis window, construct feature vector:

```python
features = [
    # Time domain
    mean_rr_ms,
    sdnn_ms,
    rmssd_ms,
    pnn50_pct,
    sdsd_ms,

    # Frequency domain
    lf_power_ms2,
    hf_power_ms2,
    lf_hf_ratio,
    total_power_ms2,
    lf_norm,      # LF / (LF + HF)
    hf_norm,      # HF / (LF + HF)

    # Nonlinear
    sd1_ms,
    sd2_ms,
    sd1_sd2_ratio,
    sample_entropy,
    dfa_alpha1,

    # Context
    current_gz,
    gz_onset_rate,
    cumulative_gz_dose,
    time_since_gz_onset_s,

    # Individual baseline deltas
    rmssd_delta_from_baseline,
    lf_hf_delta_from_baseline,
    entropy_delta_from_baseline,
]
```

#### Model Architecture Options

1. **Random Forest / XGBoost**: Robust, interpretable, handles mixed feature types
   - Recommended for initial deployment
   - Feature importance provides physiological insights

2. **LSTM / Temporal CNN**: Captures temporal patterns in HRV sequences
   - Input: Sequence of feature vectors (e.g., last 60 seconds)
   - Superior for detecting pre-LOC trajectories

3. **Hybrid Ensemble**: Combine instantaneous (RF) and temporal (LSTM) predictions
   - Weighted average or learned fusion layer
   - Best accuracy but higher computational cost

#### Training Protocol

1. **Data Collection**: Synchronized recording of:
   - Polar H10 RR intervals (1000 Hz internal, 1 Hz broadcast)
   - CGEM model inputs (G-profile, pilot config)
   - Ground truth labels (visual symptoms, LOC events)

2. **Label Definition**:
   - `0`: Normal operation (no symptoms within 30 seconds)
   - `1`: Pre-symptomatic (symptoms within 30 seconds)
   - `2`: Symptomatic (greyout/blackout occurring)
   - `3`: LOC occurring

3. **Class Weighting**: Apply inverse frequency weighting or SMOTE for class imbalance

4. **Cross-Validation**: Leave-one-subject-out for generalization assessment

5. **Threshold Tuning**: Optimize for high sensitivity (>95% true positive for LOC) while limiting false alarm rate (<10%)

---

## Polar H10 Implementation Guide

### Hardware Setup

#### Requirements

- Polar H10 sensor with Pro Strap (improved conductivity)
- Compatible receiver: smartphone, dedicated gateway, or custom hardware
- Bluetooth Low Energy (BLE) or ANT+ connectivity

#### Strap Positioning

For optimal ECG quality in high-G environment:

1. Position sensor slightly left of sternum (standard)
2. Secure strap firmly but not restrictively
3. Moisten electrode contact areas
4. Route strap under flight suit with sensor accessible

### Software Interface

#### Python BLE Connection (using bleak)

```python
"""
Polar H10 HRV Data Collection Module

Connects to Polar H10 via Bluetooth LE and streams RR intervals
for real-time HRV analysis.

Requirements:
    pip install bleak numpy

Hardware:
    - Polar H10 chest strap
    - Bluetooth LE capable computer/gateway

References:
    - Polar H10 BLE specifications
    - Gilgen-Ammann et al. (2019) DOI:10.3390/s19173794
"""

from __future__ import annotations

import asyncio
import struct
from collections import deque
from dataclasses import dataclass, field
from typing import Callable, Deque, List, Optional

from bleak import BleakClient, BleakScanner
from bleak.backends.characteristic import BleakGATTCharacteristic

# Polar H10 UUIDs
HEART_RATE_SERVICE_UUID = "0000180d-0000-1000-8000-00805f9b34fb"
HEART_RATE_MEASUREMENT_UUID = "00002a37-0000-1000-8000-00805f9b34fb"
PMD_SERVICE_UUID = "fb005c80-02e7-f387-1cad-8acd2d8df0c8"
PMD_CONTROL_UUID = "fb005c81-02e7-f387-1cad-8acd2d8df0c8"
PMD_DATA_UUID = "fb005c82-02e7-f387-1cad-8acd2d8df0c8"

# RR interval buffer settings
MAX_RR_BUFFER_SIZE: int = 300  # ~5 minutes at 60 bpm
MIN_RR_INTERVAL_MS: int = 300  # Physiological minimum (~200 bpm)
MAX_RR_INTERVAL_MS: int = 2000  # Physiological maximum (~30 bpm)


@dataclass
class HRMeasurement:
    """Parsed heart rate measurement from Polar H10."""
    timestamp_ns: int
    heart_rate_bpm: int
    rr_intervals_ms: List[int]
    sensor_contact: bool
    energy_expended: Optional[int] = None


@dataclass
class PolarH10Client:
    """Async client for Polar H10 HRV data streaming."""
    device_name: str = "Polar H10"
    rr_buffer: Deque[int] = field(default_factory=lambda: deque(maxlen=MAX_RR_BUFFER_SIZE))
    _client: Optional[BleakClient] = None
    _connected: bool = False
    _callbacks: List[Callable[[HRMeasurement], None]] = field(default_factory=list)

    async def scan_and_connect(self, timeout_s: float = 30.0) -> bool:
        """Scan for Polar H10 and establish connection."""
        print(f"Scanning for {self.device_name}...")

        device = await BleakScanner.find_device_by_name(
            self.device_name,
            timeout=timeout_s
        )

        if device is None:
            print(f"Device '{self.device_name}' not found")
            return False

        print(f"Found device: {device.name} ({device.address})")

        self._client = BleakClient(device.address)
        await self._client.connect()
        self._connected = self._client.is_connected

        if self._connected:
            print("Connected successfully")
            await self._start_hr_notification()

        return self._connected

    async def _start_hr_notification(self) -> None:
        """Subscribe to heart rate measurement notifications."""
        if self._client is None:
            return

        await self._client.start_notify(
            HEART_RATE_MEASUREMENT_UUID,
            self._hr_notification_handler
        )
        print("HR notification started")

    def _hr_notification_handler(
        self,
        sender: BleakGATTCharacteristic,
        data: bytearray
    ) -> None:
        """Parse heart rate measurement packet."""
        timestamp_ns = asyncio.get_event_loop().time() * 1e9

        # Parse flags byte
        flags = data[0]
        hr_format_16bit = bool(flags & 0x01)
        sensor_contact_supported = bool(flags & 0x02)
        sensor_contact_detected = bool(flags & 0x04)
        energy_expended_present = bool(flags & 0x08)
        rr_interval_present = bool(flags & 0x10)

        idx = 1

        # Parse heart rate value
        if hr_format_16bit:
            hr_bpm = struct.unpack_from("<H", data, idx)[0]
            idx += 2
        else:
            hr_bpm = data[idx]
            idx += 1

        # Parse energy expended if present
        energy = None
        if energy_expended_present:
            energy = struct.unpack_from("<H", data, idx)[0]
            idx += 2

        # Parse RR intervals if present
        rr_intervals: List[int] = []
        if rr_interval_present:
            while idx + 1 < len(data):
                # RR interval in 1/1024 seconds, convert to ms
                rr_raw = struct.unpack_from("<H", data, idx)[0]
                rr_ms = int(rr_raw * 1000 / 1024)
                idx += 2

                # Validate physiological range
                if MIN_RR_INTERVAL_MS <= rr_ms <= MAX_RR_INTERVAL_MS:
                    rr_intervals.append(rr_ms)
                    self.rr_buffer.append(rr_ms)

        measurement = HRMeasurement(
            timestamp_ns=int(timestamp_ns),
            heart_rate_bpm=hr_bpm,
            rr_intervals_ms=rr_intervals,
            sensor_contact=sensor_contact_detected if sensor_contact_supported else True,
            energy_expended=energy
        )

        # Invoke registered callbacks
        for callback in self._callbacks:
            callback(measurement)

    def register_callback(self, callback: Callable[[HRMeasurement], None]) -> None:
        """Register callback for new HR measurements."""
        self._callbacks.append(callback)

    def get_rr_intervals(self, count: Optional[int] = None) -> List[int]:
        """Get recent RR intervals from buffer."""
        if count is None:
            return list(self.rr_buffer)
        return list(self.rr_buffer)[-count:]

    async def disconnect(self) -> None:
        """Disconnect from device."""
        if self._client is not None and self._connected:
            await self._client.disconnect()
            self._connected = False
            print("Disconnected from Polar H10")

    @property
    def is_connected(self) -> bool:
        """Check connection status."""
        return self._connected and self._client is not None and self._client.is_connected


async def example_usage() -> None:
    """Example: Connect to Polar H10 and print RR intervals."""
    client = PolarH10Client()

    def on_hr(measurement: HRMeasurement) -> None:
        print(f"HR: {measurement.heart_rate_bpm} bpm, "
              f"RR: {measurement.rr_intervals_ms} ms, "
              f"Contact: {measurement.sensor_contact}")

    client.register_callback(on_hr)

    connected = await client.scan_and_connect(timeout_s=30.0)
    if not connected:
        return

    try:
        # Stream for 60 seconds
        await asyncio.sleep(60)
    finally:
        await client.disconnect()

    # Analyze collected RR intervals
    rr_intervals = client.get_rr_intervals()
    print(f"\nCollected {len(rr_intervals)} RR intervals")


if __name__ == "__main__":
    asyncio.run(example_usage())
```

### HRV Metric Calculator

```python
"""
Real-time HRV Metrics Calculator

Computes time-domain, frequency-domain, and nonlinear HRV metrics
from RR interval streams for G-LOC prediction.

Requirements:
    pip install numpy scipy

References:
    - Shaffer & Ginsberg (2017) DOI:10.3389/fpubh.2017.00258
    - Billman (2011) DOI:10.3389/fphys.2011.00086
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

import numpy as np
from numpy.typing import NDArray
from scipy import signal
from scipy import interpolate


@dataclass(frozen=True)
class HRVMetrics:
    """Computed HRV metrics from RR interval series."""
    # Time domain
    mean_rr_ms: float
    sdnn_ms: float
    rmssd_ms: float
    pnn50_pct: float
    sdsd_ms: float
    mean_hr_bpm: float

    # Frequency domain
    vlf_power_ms2: float  # 0.003-0.04 Hz
    lf_power_ms2: float   # 0.04-0.15 Hz
    hf_power_ms2: float   # 0.15-0.4 Hz
    total_power_ms2: float
    lf_hf_ratio: float
    lf_nu: float  # Normalized units
    hf_nu: float

    # Nonlinear
    sd1_ms: float
    sd2_ms: float
    sd1_sd2_ratio: float
    sample_entropy: float
    dfa_alpha1: float

    # Quality
    signal_quality: float  # 0.0-1.0
    artifact_pct: float
    n_beats: int


def compute_time_domain(rr_ms: NDArray[np.float64]) -> Tuple[float, ...]:
    """Compute time-domain HRV metrics."""
    if len(rr_ms) < 2:
        nan = float("nan")
        return (nan,) * 6

    mean_rr = float(np.mean(rr_ms))
    sdnn = float(np.std(rr_ms, ddof=1))

    # Successive differences
    diff_rr = np.diff(rr_ms)
    rmssd = float(np.sqrt(np.mean(diff_rr ** 2)))
    sdsd = float(np.std(diff_rr, ddof=1))

    # pNN50: percentage of successive differences > 50 ms
    pnn50 = float(100.0 * np.sum(np.abs(diff_rr) > 50) / len(diff_rr))

    mean_hr = float(60000.0 / mean_rr) if mean_rr > 0 else float("nan")

    return mean_rr, sdnn, rmssd, pnn50, sdsd, mean_hr


def compute_frequency_domain(
    rr_ms: NDArray[np.float64],
    fs_resample: float = 4.0
) -> Tuple[float, ...]:
    """Compute frequency-domain HRV metrics using Welch's method."""
    if len(rr_ms) < 30:
        nan = float("nan")
        return (nan,) * 7

    # Create time axis (cumulative sum of RR intervals)
    time_s = np.cumsum(rr_ms) / 1000.0
    time_s = time_s - time_s[0]

    # Interpolate to uniform sampling for FFT
    duration_s = time_s[-1]
    n_samples = int(duration_s * fs_resample)
    if n_samples < 32:
        nan = float("nan")
        return (nan,) * 7

    time_uniform = np.linspace(0, duration_s, n_samples)
    interp_func = interpolate.interp1d(
        time_s, rr_ms, kind="cubic", fill_value="extrapolate"
    )
    rr_resampled = interp_func(time_uniform)

    # Remove mean (detrend)
    rr_detrended = rr_resampled - np.mean(rr_resampled)

    # Welch PSD estimation
    nperseg = min(256, len(rr_detrended) // 2)
    freqs, psd = signal.welch(
        rr_detrended,
        fs=fs_resample,
        nperseg=nperseg,
        noverlap=nperseg // 2,
        window="hann"
    )

    # Integrate power in frequency bands
    def band_power(f_low: float, f_high: float) -> float:
        mask = (freqs >= f_low) & (freqs < f_high)
        return float(np.trapz(psd[mask], freqs[mask])) if np.any(mask) else 0.0

    vlf = band_power(0.003, 0.04)
    lf = band_power(0.04, 0.15)
    hf = band_power(0.15, 0.4)
    total = vlf + lf + hf

    lf_hf_ratio = lf / hf if hf > 0 else float("nan")
    lf_nu = 100.0 * lf / (lf + hf) if (lf + hf) > 0 else float("nan")
    hf_nu = 100.0 * hf / (lf + hf) if (lf + hf) > 0 else float("nan")

    return vlf, lf, hf, total, lf_hf_ratio, lf_nu, hf_nu


def compute_poincare(rr_ms: NDArray[np.float64]) -> Tuple[float, float, float]:
    """Compute Poincaré plot descriptors (SD1, SD2)."""
    if len(rr_ms) < 3:
        nan = float("nan")
        return nan, nan, nan

    rr_n = rr_ms[:-1]
    rr_n1 = rr_ms[1:]

    sd1 = float(np.std(rr_n1 - rr_n, ddof=1) / np.sqrt(2))
    sd2 = float(np.std(rr_n1 + rr_n, ddof=1) / np.sqrt(2))
    ratio = sd1 / sd2 if sd2 > 0 else float("nan")

    return sd1, sd2, ratio


def compute_sample_entropy(
    rr_ms: NDArray[np.float64],
    m: int = 2,
    r_factor: float = 0.2
) -> float:
    """Compute Sample Entropy of RR series."""
    n = len(rr_ms)
    if n < m + 2:
        return float("nan")

    r = r_factor * np.std(rr_ms)
    if r == 0:
        return float("nan")

    def count_matches(template_len: int) -> int:
        count = 0
        for i in range(n - template_len):
            for j in range(i + 1, n - template_len):
                if np.max(np.abs(rr_ms[i:i+template_len] - rr_ms[j:j+template_len])) < r:
                    count += 1
        return count

    a = count_matches(m + 1)
    b = count_matches(m)

    if b == 0 or a == 0:
        return float("nan")

    return float(-np.log(a / b))


def compute_dfa_alpha1(rr_ms: NDArray[np.float64]) -> float:
    """Compute short-term DFA scaling exponent (alpha1, 4-16 beats)."""
    n = len(rr_ms)
    if n < 16:
        return float("nan")

    # Integrate RR series
    y = np.cumsum(rr_ms - np.mean(rr_ms))

    # Box sizes for alpha1
    box_sizes = [4, 6, 8, 10, 12, 14, 16]
    box_sizes = [s for s in box_sizes if s <= n // 4]

    if len(box_sizes) < 2:
        return float("nan")

    fluctuations = []
    for box_size in box_sizes:
        n_boxes = n // box_size
        if n_boxes == 0:
            continue

        rms_values = []
        for i in range(n_boxes):
            segment = y[i * box_size : (i + 1) * box_size]
            x = np.arange(box_size)
            coeffs = np.polyfit(x, segment, 1)
            trend = np.polyval(coeffs, x)
            rms = np.sqrt(np.mean((segment - trend) ** 2))
            rms_values.append(rms)

        fluctuations.append(np.mean(rms_values))

    if len(fluctuations) < 2:
        return float("nan")

    # Log-log regression
    log_n = np.log(box_sizes[:len(fluctuations)])
    log_f = np.log(fluctuations)
    alpha, _ = np.polyfit(log_n, log_f, 1)

    return float(alpha)


def detect_artifacts(rr_ms: NDArray[np.float64], threshold: float = 0.2) -> NDArray[np.bool_]:
    """Detect artifacts in RR series using percentage threshold."""
    if len(rr_ms) < 3:
        return np.zeros(len(rr_ms), dtype=bool)

    # Local median filter
    median_rr = np.median(rr_ms)
    artifacts = np.abs(rr_ms - median_rr) / median_rr > threshold

    # Also flag based on successive differences
    diff_rr = np.abs(np.diff(rr_ms))
    median_diff = np.median(diff_rr)
    diff_artifacts = np.concatenate([[False], diff_rr > 3 * median_diff])

    return artifacts | diff_artifacts


def calculate_hrv_metrics(
    rr_intervals_ms: List[int],
    artifact_threshold: float = 0.2
) -> HRVMetrics:
    """Calculate comprehensive HRV metrics from RR intervals."""
    rr = np.array(rr_intervals_ms, dtype=np.float64)

    # Detect and handle artifacts
    artifacts = detect_artifacts(rr, artifact_threshold)
    artifact_pct = float(100.0 * np.sum(artifacts) / len(rr)) if len(rr) > 0 else 100.0

    # Remove artifacts for analysis
    rr_clean = rr[~artifacts]

    if len(rr_clean) < 10:
        # Insufficient clean data
        nan = float("nan")
        return HRVMetrics(
            mean_rr_ms=nan, sdnn_ms=nan, rmssd_ms=nan, pnn50_pct=nan,
            sdsd_ms=nan, mean_hr_bpm=nan, vlf_power_ms2=nan,
            lf_power_ms2=nan, hf_power_ms2=nan, total_power_ms2=nan,
            lf_hf_ratio=nan, lf_nu=nan, hf_nu=nan, sd1_ms=nan,
            sd2_ms=nan, sd1_sd2_ratio=nan, sample_entropy=nan,
            dfa_alpha1=nan, signal_quality=0.0, artifact_pct=artifact_pct,
            n_beats=len(rr)
        )

    # Time domain
    mean_rr, sdnn, rmssd, pnn50, sdsd, mean_hr = compute_time_domain(rr_clean)

    # Frequency domain
    vlf, lf, hf, total, lf_hf, lf_nu, hf_nu = compute_frequency_domain(rr_clean)

    # Nonlinear
    sd1, sd2, sd_ratio = compute_poincare(rr_clean)
    samp_en = compute_sample_entropy(rr_clean)
    dfa_a1 = compute_dfa_alpha1(rr_clean)

    # Signal quality heuristic
    signal_quality = max(0.0, 1.0 - artifact_pct / 100.0)
    if np.isnan(rmssd) or np.isnan(lf_hf):
        signal_quality *= 0.5

    return HRVMetrics(
        mean_rr_ms=mean_rr,
        sdnn_ms=sdnn,
        rmssd_ms=rmssd,
        pnn50_pct=pnn50,
        sdsd_ms=sdsd,
        mean_hr_bpm=mean_hr,
        vlf_power_ms2=vlf,
        lf_power_ms2=lf,
        hf_power_ms2=hf,
        total_power_ms2=total,
        lf_hf_ratio=lf_hf,
        lf_nu=lf_nu,
        hf_nu=hf_nu,
        sd1_ms=sd1,
        sd2_ms=sd2,
        sd1_sd2_ratio=sd_ratio,
        sample_entropy=samp_en,
        dfa_alpha1=dfa_a1,
        signal_quality=signal_quality,
        artifact_pct=artifact_pct,
        n_beats=len(rr)
    )
```

---

## API Reference

### Extended PilotConfig

The proposed `EnhancedPilotConfig` extends the existing `PilotConfig` with HRV-related fields:

```python
@dataclass(frozen=True)
class EnhancedPilotConfig:
    # === Existing CGEM parameters ===
    who_profile: Optional[int] = 2
    male: Optional[int] = 1
    height_cm: Optional[float] = 179.0
    baseline_systolic_bp: Optional[float] = 120.0
    baseline_diastolic_bp: Optional[float] = 80.0
    max_systolic_bp: Optional[float] = 177.0
    max_diastolic_bp: Optional[float] = 80.0
    g_tolerance_multiplier: Optional[float] = 1.0
    heart_response_tau_s: Optional[float] = 2.5
    conbank_s: Optional[float] = 7.1
    lifebank_s: Optional[float] = 180.0
    gsuit_max_psi: float = 0.0
    gsuit_coverage_fraction: float = 0.0
    agsm_effectiveness: float = 0.0
    pbg_max_mmhg: float = 0.0
    pretest_other_strain_mmhg: float = 0.0
    non_agsm_tensing_limit_mmhg: float = 0.0
    seat_tilt_deg: float = 10.0
    drug_delay_s: float = 0.0
    dehydration_level: float = 0.0

    # === NEW: HRV Baseline (pre-flight measurement) ===
    baseline_rmssd_ms: Optional[float] = None
    baseline_sdnn_ms: Optional[float] = None
    baseline_lf_hf_ratio: Optional[float] = None
    baseline_sample_entropy: Optional[float] = None
    baseline_dfa_alpha1: Optional[float] = None
    baseline_mean_hr_bpm: Optional[float] = None

    # === NEW: Real-time HRV input ===
    current_hrv_metrics: Optional[HRVMetrics] = None

    # === NEW: Individual G-LOC history ===
    prior_gloc_events: int = 0
    avg_gloc_threshold_gz: Optional[float] = None
    last_centrifuge_date: Optional[str] = None  # ISO format
```

### Prediction API

```python
def run_cgem_with_hrv(
    profile_id: str,
    config: EnhancedPilotConfig,
    hrv_stream: Optional[List[HRVMetrics]] = None,
    fusion_weight: float = 0.5,  # 0=CGEM only, 1=HRV only
) -> EnhancedCGEMResult:
    """
    Run CGEM model with HRV-based risk fusion.

    Args:
        profile_id: Maneuver identifier (e.g., 'hammerhead')
        config: Extended pilot configuration with HRV baseline
        hrv_stream: Optional list of recent HRV metrics (30s windows)
        fusion_weight: Balance between CGEM and HRV predictions

    Returns:
        EnhancedCGEMResult with fused risk assessment
    """
    pass
```

---

## Validation Protocols

### Centrifuge Study Design

#### Inclusion Criteria
- Active duty military pilots or student pilots
- Age 18-45 years
- Current Class I or II flight physical
- No cardiac arrhythmias or autonomic disorders

#### Exclusion Criteria
- Beta-blocker or other cardiac medications
- Recent G-LOC event (<30 days)
- Sleep deprivation (<6 hours prior night)
- Alcohol within 24 hours

#### Protocol
1. **Baseline Collection (T-15 min)**
   - 10-minute supine rest with Polar H10
   - Record baseline HRV metrics
   - Measure resting BP and HR

2. **Orthostatic Challenge (T-5 min)**
   - 5-minute standing
   - Assess HRV response to postural change

3. **Centrifuge Exposure (T0)**
   - Progressive G-onset: 1 G/s to +5 Gz
   - Hold at +5 Gz for 10 seconds
   - Step increase to +7 Gz (or tolerance limit)
   - Hold until visual symptoms or LOC
   - Immediate G-offset

4. **Recovery (T+5 min)**
   - Continue HRV recording through recovery
   - Document symptom timeline

5. **Repeat Trials**
   - Minimum 3 trials per subject with 30-minute rest intervals

#### Data Synchronization
- Centrifuge G-profile: 100 Hz logging
- Polar H10 RR intervals: 1000 Hz internal, extracted per-beat
- Video recording: 30 fps for symptom verification
- NIRS cerebral oximetry: 10 Hz (if available)

### Machine Learning Validation

#### Dataset Split
- Training: 60% of subjects
- Validation: 20% of subjects
- Test: 20% of subjects (held out until final evaluation)

#### Metrics
- **Sensitivity**: True positive rate for LOC prediction (target >95%)
- **Specificity**: True negative rate (target >85%)
- **Precision**: Positive predictive value
- **Lead Time**: Seconds between warning and actual LOC (target >10s)
- **False Alarm Rate**: False positives per hour of flight time (target <0.5)

#### Cross-Validation
- Leave-one-subject-out for generalization assessment
- Stratified k-fold within subjects for hyperparameter tuning

---

## Future Directions

1. **Multi-sensor Fusion**: Integrate NIRS cerebral oxygenation with HRV for enhanced prediction

2. **Adaptive Thresholds**: Continuously update individual risk thresholds based on flight history

3. **Cockpit Integration**: Develop avionics interface for real-time pilot alerting

4. **Training Applications**: Use HRV feedback for AGSM training optimization

5. **Fatigue Monitoring**: Extend HRV analysis to pre-flight fitness-for-duty assessment

---

*Last updated: December 2024*
