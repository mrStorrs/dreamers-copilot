import unittest

from tests.test_dreamers_stats_checkpoint import DreamersStatsCheckpointTests
from tests.test_dreamers_stats_hooks_install import DreamersStatsHookInstallTests
from tests.test_dreamers_stats_record import DreamersStatsRecordTests
from tests.test_dreamers_stats_reports import DreamersStatsReportTests


__all__ = [
    "DreamersStatsCheckpointTests",
    "DreamersStatsHookInstallTests",
    "DreamersStatsRecordTests",
    "DreamersStatsReportTests",
]


if __name__ == "__main__":
    unittest.main()
