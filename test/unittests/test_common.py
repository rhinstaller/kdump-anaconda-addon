from unittest.case import TestCase
from unittest.mock import patch, MagicMock
from com_redhat_kdump import common

SYS_CRASH_SIZE = '/sys/kernel/kexec_crash_size'
PROC_MEMINFO = '/proc/meminfo'

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


class MockFileRead(MagicMock):
    def __init__(self, file_read_map):
        MagicMock.__init__(self, name=open, spec=open)
        self.file_read_map = file_read_map

        handle = MagicMock()
        handle.__enter__.return_value = handle
        handle.read.return_value = None

        def reset_choose_file(filename, *args, **kwargs):
            handle.read.return_value = self.file_read_map[filename]
            return handle

        self.side_effect = reset_choose_file


class KdumpCommonTestCase(TestCase):

    def setUp(self):
        # Clean up global variable that may cache test result of previous test case
        common._reservedMemory = None

    @patch("builtins.open", MockFileRead(X86_INFO_FIXTURE))
    @patch("blivet.arch.get_arch", return_value="x86_64")
    def memory_bound_test_x86(self, _mock_read):
        self.assertEqual((160, 4 * 1024 - 512, 1), common.getMemoryBounds())

    @patch("builtins.open", MockFileRead(AARCH64_INFO_FIXTURE))
    @patch("blivet.arch.get_arch", return_value="aarch64")
    def memory_bound_test_aarch64(self, _mock_read):
        self.assertEqual((512, 64 * 1024 - 512, 1), common.getMemoryBounds())

    @patch("builtins.open", MockFileRead(PPC64_INFO_FIXTURE))
    @patch("blivet.arch.get_arch", return_value="ppc64")
    def memory_bound_test_ppc64(self, _mock_read):
        self.assertEqual((384, 64 * 1024 - 1024, 1), common.getMemoryBounds())
