"""New generated-trace adapter; legacy wrapper signatures/behaviour unchanged.

CGEM custom() emits two formats using the same numeric layout. Unchanged
flags and the next ordered second identify periodic rows; changed flags
identify millisecond transition rows, including events before one second.
"""

import hashlib
import math
import subprocess
import tempfile
import threading
from itertools import pairwise
from pathlib import Path

from cgem_ext.api.schemas import CGEMRunData, CGEMRunResponse, PilotConfigRequest

from .schemas import Physiology

_PROCESS_SLOTS = threading.BoundedSemaphore(2)


def trace_to_ramps(times_s: list[float], gz: list[float]) -> list[tuple[float, int]]:
    if len(times_s) != len(gz) or len(times_s) < 2:
        raise ValueError("A trace needs matching time and G arrays with at least two samples.")
    if not all(math.isfinite(v) for v in [*times_s, *gz]):
        raise ValueError("Trace values must be finite.")
    if times_s[0] != 0 or abs(gz[0] - 1.0) > 1e-8:
        raise ValueError("CGEM generated traces must start at t=0 with Gnorm=1 G.")
    if times_s[-1] > 120 or max(abs(g) for g in gz) > 15:
        raise ValueError("Generated trace exceeds the 120 s / ±15 G adapter resource envelope.")
    ms = [round(t * 1000) for t in times_s]
    if any(abs(t * 1000 - m) > 1e-7 for t, m in zip(times_s, ms, strict=True)):
        raise ValueError("CGEM trace times must be exact integer milliseconds.")
    if any(b <= a for a, b in pairwise(ms)):
        raise ValueError("Trace times must be strictly increasing.")
    return [
        ((gz[i + 1] - gz[i]) * 1000 / (ms[i + 1] - ms[i]), ms[i + 1] - ms[i])
        for i in range(len(ms) - 1)
    ]


def parse_output(path: Path, scenario: str, pilot_label: str, duration_s: float) -> CGEMRunResponse:
    next_periodic = 1
    previous_flags: tuple[int, ...] = (0, 0, 0)
    last_time = -1.0
    samples: dict[float, tuple[list[float], tuple[int, ...]]] = {}
    event_times: list[float | None] = [None, None, None]
    if path.stat().st_size > 8_000_000:
        raise ValueError("CGEM output exceeds the bounded adapter output size.")
    for line in path.read_text().splitlines():
        parts = line.split()
        if len(parts) != 12:
            continue
        try:
            values = [float(v) for v in parts]
        except ValueError:
            # Ignore text headers; numeric rows containing overflow are invalid.
            try:
                float(parts[0])
            except ValueError:
                continue
            raise ValueError("CGEM produced a non-numeric/overflow physiology row.") from None
        if not all(math.isfinite(v) for v in values):
            raise ValueError("CGEM produced non-finite physiology.")
        flags = tuple(int(v) for v in values[9:])
        if any(v not in (0, 1, 2) for v in flags) or any(v != int(v) for v in values[9:]):
            raise ValueError("CGEM produced unsupported state flags.")
        raw = values[0]
        if raw != int(raw):
            raise ValueError("CGEM timestamp must be an integer.")
        if flags == previous_flags and raw == next_periodic:
            # The Fortran increments totalt, prints old physiology, then integrates.
            t = round(raw - 0.001, 3)
            next_periodic += 1
        elif flags != previous_flags:
            t = raw / 1000.0
            if t > next_periodic:
                raise ValueError("CGEM output skipped a required periodic sample.")
        else:
            raise ValueError(
                "Cannot disambiguate CGEM timestamp from ordered cadence and flag transitions."
            )
        if t < last_time - 1e-9 or t < 0 or t > duration_s + 1e-9:
            raise ValueError("CGEM output has an out-of-order or out-of-range timestamp.")
        for i, (old, new) in enumerate(zip(previous_flags, flags, strict=True)):
            if new == 1 and old != 1 and event_times[i] is None:
                event_times[i] = t
        # Periodic samples can repeat a transition at .999. Keep the earlier
        # transition unless a later transition at the same time supersedes it.
        if t not in samples or flags != previous_flags:
            samples[t] = (values, flags)
        previous_flags = flags
        last_time = t
    if next_periodic != math.floor(duration_s) + 1:
        raise ValueError("CGEM output is missing the final expected periodic sample.")
    if not samples:
        raise ValueError(
            "CGEM produced no usable native physiology samples; short traces may end before its first 1 s output."
        )
    rows = list(samples.values())

    def col(index: int) -> list[float]:
        return [v[index] for v, _ in rows]

    data = CGEMRunData.model_validate(
        dict(
            Time_s=list(samples),
            G=col(1),
            G_eff=col(2),
            c_bank_s=col(3),
            F_con_dl_per_min=col(4),
            F_vis_dl_per_min=col(5),
            F_bo_dl_per_min=col(6),
            bo_bank_s=col(7),
            HLAP_mmHg=col(8),
            Conscious=[f[0] for _, f in rows],
            Greyout=[f[1] for _, f in rows],
            Blackout=[f[2] for _, f in rows],
        )
    )
    return CGEMRunResponse(
        maneuver=scenario,
        pilot_profile=pilot_label,
        duration_s=duration_s,
        time_to_gloc_s=event_times[0],
        time_to_greyout_s=event_times[1],
        time_to_blackout_s=event_times[2],
        data=data,
    )


def run_trace(
    times_s: list[float], gz: list[float], pilot: PilotConfigRequest, scenario: str
) -> Physiology:
    binary_sha = None
    try:
        from cgem_wrapper import PilotConfig, _prepare_gloc_inp, _resolve_cgem_executable

        ramps = trace_to_ramps(times_s, gz)
        exe = _resolve_cgem_executable()
        binary_sha = hashlib.sha256(exe.read_bytes()).hexdigest()
        kwargs = pilot.model_dump(exclude={"countermeasures_label"})
        cfg = PilotConfig(**kwargs)
        # Concurrency is bounded and the generated experiment is <=120000 iterations.
        # Wrapper resolution/preparation reused; this generated-trace path applies
        # its own 15-second timeout, process capacity and output-size controls.
        if not _PROCESS_SLOTS.acquire(timeout=20):
            raise TimeoutError("CGEM process capacity is busy; retry the simulation.")
        try:
            with tempfile.TemporaryDirectory(prefix="cgem_flight_") as directory:
                root = Path(directory)
                _prepare_gloc_inp(root, egp_name="flight.egp", out_name="flight.out", config=cfg)
                # Wrapper template Gnorm must match the exact initial Gz contract.
                lines = (root / "gloc_inp.dat").read_text().splitlines()
                if abs(float(lines[0].split(",")[0]) - 1.0) > 1e-8:
                    raise ValueError(
                        "CGEM template Gnorm is not 1 G; generated-trace initialization would disagree."
                    )
                (root / "flight.egp").write_text(
                    str(len(ramps)) + "\n" + "".join(f"{rate:.12g}, {ms}\n" for rate, ms in ramps)
                )
                subprocess.run(
                    [str(exe)],
                    cwd=root,
                    check=True,
                    timeout=15,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                result = parse_output(
                    root / "flight.out",
                    scenario,
                    f"who_profile={pilot.who_profile}"
                    if pilot.who_profile is not None
                    else "custom",
                    times_s[-1],
                )
        finally:
            _PROCESS_SLOTS.release()
        return Physiology(status="available", binary_sha256=binary_sha, result=result)
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
        return Physiology(
            status="unavailable",
            binary_sha256=binary_sha,
            reason=f"Native CGEM physiology unavailable: {type(exc).__name__}: {exc}",
        )
