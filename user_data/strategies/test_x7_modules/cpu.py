"""CPU sizing helpers for TestX7 local optimization experiments."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path


@dataclass(frozen=True)
class CpuTopology:
  logical_cpus: int
  physical_cores: int
  affinity_cpus: int
  recommended_workers: int


def _positive_int(value: str | None) -> int | None:
  if value is None:
    return None
  try:
    parsed = int(value)
  except ValueError:
    return None
  return parsed if parsed > 0 else None


def _affinity_count() -> int:
  try:
    return len(os.sched_getaffinity(0))
  except (AttributeError, OSError):
    return os.cpu_count() or 1


def _physical_core_count() -> int:
  cpuinfo = Path("/proc/cpuinfo")
  if not cpuinfo.exists():
    return 0

  physical_ids: set[tuple[str, str]] = set()
  current_physical: str | None = None
  current_core: str | None = None

  for raw_line in cpuinfo.read_text(encoding="utf-8", errors="ignore").splitlines():
    line = raw_line.strip()
    if not line:
      if current_physical is not None and current_core is not None:
        physical_ids.add((current_physical, current_core))
      current_physical = None
      current_core = None
      continue

    if line.startswith("physical id"):
      current_physical = line.split(":", 1)[1].strip()
    elif line.startswith("core id"):
      current_core = line.split(":", 1)[1].strip()

  if current_physical is not None and current_core is not None:
    physical_ids.add((current_physical, current_core))

  return len(physical_ids)


def choose_worker_count(logical_cpus: int, physical_cores: int) -> int:
  """Return a conservative worker count that leaves room for Freqtrade itself."""
  logical_cpus = max(1, logical_cpus)
  physical_cores = max(0, physical_cores)

  if logical_cpus <= 2:
    return 1

  baseline = physical_cores if physical_cores > 0 else max(1, logical_cpus // 2)
  return max(1, min(baseline, logical_cpus - 1))


def detect_cpu_topology() -> CpuTopology:
  affinity_cpus = _affinity_count()
  logical_cpus = min(os.cpu_count() or affinity_cpus or 1, affinity_cpus or 1)
  physical_cores = _physical_core_count()
  return CpuTopology(
    logical_cpus=logical_cpus,
    physical_cores=physical_cores,
    affinity_cpus=affinity_cpus,
    recommended_workers=choose_worker_count(logical_cpus, physical_cores),
  )


def recommended_indicator_cores(env_var: str = "TEST_X7_WORKERS") -> int:
  explicit = _positive_int(os.getenv(env_var))
  if explicit is not None:
    topology = detect_cpu_topology()
    return min(explicit, max(1, topology.logical_cpus))
  return detect_cpu_topology().recommended_workers


def recommended_process_workers(env_var: str = "TEST_X7_PROCESS_WORKERS") -> int:
  explicit = _positive_int(os.getenv(env_var))
  topology = detect_cpu_topology()
  if explicit is not None:
    return min(explicit, max(1, topology.logical_cpus))
  return topology.recommended_workers


def recommended_stable_process_workers(env_var: str = "TEST_X7_STABLE_PROCESS_WORKERS") -> int:
  explicit = _positive_int(os.getenv(env_var))
  topology = detect_cpu_topology()
  if explicit is not None:
    return min(explicit, max(1, topology.logical_cpus))
  return max(1, topology.logical_cpus)
