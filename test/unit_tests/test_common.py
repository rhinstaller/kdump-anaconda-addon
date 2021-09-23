from unittest.case import TestCase
from unittest.mock import patch
from com_redhat_kdump import common
from .mock import MockBuiltinRead

SYS_CRASH_SIZE = '/sys/kernel/kexec_crash_size'
PROC_MEMINFO = '/proc/meminfo'
CRASHKERNEL_DEFAULT = '/usr/lib/modules/{}/crashkernel.default'

X86_INFO_FIXTURE = {
    SYS_CRASH_SIZE: "167772160",  # 160MB
    PROC_MEMINFO:"""MemTotal:        4030464 kB
"""  # 4GB - 160MB
}

AARCH64_INFO_FIXTURE = {
    SYS_CRASH_SIZE: "536870912",  # 512MB
    PROC_MEMINFO:"""MemTotal:       66584576 kB
"""  # 64GB - 512MB
}

PPC64_INFO_FIXTURE = {
    SYS_CRASH_SIZE: "1073741824",  # 1024MB
    PROC_MEMINFO:"""MemTotal:       66060288 kB
"""  # 64GB - 1GB
}


class KdumpCommonTestCase(TestCase):

    def setUp(self):
        # Clean up global variable that may cache test result of previous test case
        common._reservedMemory = None

    @patch("builtins.open", MockBuiltinRead(X86_INFO_FIXTURE))
    @patch("blivet.arch.get_arch", return_value="x86_64")
    def test_memory_bound_x86(self, _mock_read):
        self.assertEqual((160, 4 * 1024 - 512, 1), common.getMemoryBounds())

    @patch("builtins.open", MockBuiltinRead(AARCH64_INFO_FIXTURE))
    @patch("blivet.arch.get_arch", return_value="aarch64")
    def test_memory_bound_aarch64(self, _mock_read):
        self.assertEqual((512, 64 * 1024 - 512, 1), common.getMemoryBounds())

    @patch("builtins.open", MockBuiltinRead(PPC64_INFO_FIXTURE))
    @patch("blivet.arch.get_arch", return_value="ppc64")
    def test_memory_bound_ppc64(self, _mock_read):
        self.assertEqual((384, 64 * 1024 - 1024, 1), common.getMemoryBounds())
