from NostalgiaForInfinityX7 import NostalgiaForInfinityX7

from test_x7_modules import (
  TestX7BtcInformativeCacheMixin,
  TestX7EntryLogicMixin,
  TestX7EntryLineProfilerMixin,
  TestX7EntryOptimizationMixin,
  TestX7IndicatorLogicMixin,
  TestX7InformativeCacheMixin,
  TestX7ParallelAnalyzeMixin,
  TestX7ProfilingMixin,
  recommended_indicator_cores,
)


class TestX7(
  TestX7ParallelAnalyzeMixin,
  TestX7EntryLineProfilerMixin,
  TestX7ProfilingMixin,
  TestX7InformativeCacheMixin,
  TestX7EntryOptimizationMixin,
  TestX7BtcInformativeCacheMixin,
  TestX7IndicatorLogicMixin,
  TestX7EntryLogicMixin,
  NostalgiaForInfinityX7,
):
  """Local Test X7 fork.

  Indicator/informative and entry logic are mechanically extracted from the
  current upstream X7 baseline. TestX7 adds modular profiling and conservative
  cache/entry optimizations so every performance change can be parity-checked
  against NostalgiaForInfinityX7.
  """

  num_cores_indicators_calc = recommended_indicator_cores()

  def version(self) -> str:
    return f"Test X7 based on {super().version()}"
