from textwrap import dedent
from unittest.case import TestCase
from com_redhat_kdump import common
from com_redhat_kdump.service.kdump import KdumpService


class KdumpKickstartTestCase(TestCase):

    def setUp(self):
        # Show unlimited diff.
        self.maxDiff = None

        # Clean up global variable that may cache test result of previous test case
        common._reservedMemory = None

        # Create the Kdump service.
        self._service = KdumpService()

    def _check_ks_input(self, ks_in, errors=None, warnings=None):
        report = self._service.read_kickstart(ks_in)
        self.assertEqual([i.message for i in report.error_messages], errors or [])
        self.assertEqual([i.message for i in report.warning_messages], warnings or [])

    def _check_ks_output(self, ks_out):
        output = self._service.generate_kickstart()
        self.assertEqual(output.strip(), dedent(ks_out).strip())

    def test_ks_default(self):
        self.assertEqual(self._service.kdump_enabled, False)
        self.assertEqual(self._service.fadump_enabled, False)
        self.assertEqual(self._service.reserved_memory, "auto")

        self._check_ks_output("""
        %addon com_redhat_kdump --disable

        %end
        """)

    def test_ks_enable(self):
        self._check_ks_input("""
        %addon com_redhat_kdump --enable
        %end
        """)

        self.assertEqual(self._service.kdump_enabled, True)
        self.assertEqual(self._service.fadump_enabled, False)
        self.assertEqual(self._service.reserved_memory, "auto")

        self._check_ks_output("""
        %addon com_redhat_kdump --enable --reserve-mb='auto'

        %end
        """)

    def test_ks_disable(self):
        self._check_ks_input("""
        %addon com_redhat_kdump --disable
        %end
        """)

        self.assertEqual(self._service.kdump_enabled, False)
        self.assertEqual(self._service.fadump_enabled, False)
        self.assertEqual(self._service.reserved_memory, "auto")

        self._check_ks_output("""
        %addon com_redhat_kdump --disable

        %end
        """)

    def test_ks_reserve_mb(self):
        self._check_ks_input("""
        %addon com_redhat_kdump --enable --reserve-mb=256
        %end
        """)

        self.assertEqual(self._service.kdump_enabled, True)
        self.assertEqual(self._service.fadump_enabled, False)
        self.assertEqual(self._service.reserved_memory, "256")

        self._check_ks_output("""
        %addon com_redhat_kdump --enable --reserve-mb='256'

        %end
        """)

    def test_ks_reserve_auto(self):
        self._check_ks_input("""
        %addon com_redhat_kdump --enable --reserve-mb=auto
        %end
        """)

        self.assertEqual(self._service.kdump_enabled, True)
        self.assertEqual(self._service.fadump_enabled, False)
        self.assertEqual(self._service.reserved_memory, "auto")

        self._check_ks_output("""
        %addon com_redhat_kdump --enable --reserve-mb='auto'

        %end
        """)

    def test_ks_reserve_mb_invalid(self):
        ks_in = """
        %addon com_redhat_kdump --reserve-mb=
        %end
        """
        ks_err = "Invalid value '' for --reserve-mb"
        self._check_ks_input(ks_in, [ks_err])

        ks_in = """
        %addon com_redhat_kdump --reserve-mb=invalid
        %end
        """
        ks_err = "Invalid value 'invalid' for --reserve-mb"
        self._check_ks_input(ks_in, [ks_err])

    def test_ks_enablefadump(self):
        self._check_ks_input("""
        %addon com_redhat_kdump --disable --enablefadump
        %end
        """)

        self.assertEqual(self._service.kdump_enabled, False)
        self.assertEqual(self._service.fadump_enabled, True)
        self.assertEqual(self._service.reserved_memory, "auto")

        self._check_ks_output("""
        %addon com_redhat_kdump --disable --enablefadump

        %end
        """)
