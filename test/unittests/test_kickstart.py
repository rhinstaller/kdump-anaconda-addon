from utils import KdumpTestCase
from unittest.mock import patch
from com_redhat_kdump.ks.kdump import KdumpData
from pykickstart.errors import KickstartParseError
import re


ALL_ARGS_RE = re.compile(
    r"[\s\n]*%addon\s+KdumpData\s+"
    r"(--enable|--disable|--enablefadump|--reverse-mb[=|\ ]['\"]?\d+['\"][Mm]?)*"
    r"\s+.*[\s\n]+%end[\s\n]*")

def new_ks_addon_data():
    return KdumpData("KdumpData")


def kdump_check_ks(test, addon_data, required_arguments):
    ks_str = str(addon_data)
    for arg in required_arguments:
        # Ensure rerquired argument is generated.
        arg_regex = re.compile(r"[\s\n]*%addon\s+KdumpData.*\s+" + arg + r"\s+.*[\s\n]+%end[\s\n]*")
        test.assertRegexpMatches(ks_str, arg_regex)
    # Ensure no invalid argument is generated.
    test.assertRegexpMatches(ks_str, ALL_ARGS_RE)


class KdumpKickstartTestCase(KdumpTestCase):
    def new_ks_addon_data_test(self):
        ks_addon_data = new_ks_addon_data()
        self.assertIsNotNone(ks_addon_data)

    def ks_default_to_str_test(self):
        ks_addon_data = new_ks_addon_data()
        kdump_check_ks(self, ks_addon_data, ["--disable"])

    def ks_enable_to_str_test(self):
        ks_addon_data = new_ks_addon_data()
        ks_addon_data.enabled = True
        kdump_check_ks(self, ks_addon_data, ["--enable"])

    def ks_disable_to_str_test(self):
        ks_addon_data = new_ks_addon_data()
        ks_addon_data.enabled = False
        kdump_check_ks(self, ks_addon_data, ["--disable"])

    def ks_parse_enable_to_str_test(self):
        ks_addon_data = new_ks_addon_data()
        ks_addon_data.handle_header(0, ["--enable"])
        kdump_check_ks(self, ks_addon_data, ["--enable"])

    def ks_parse_reserve_to_str_test(self):
        ks_addon_data = new_ks_addon_data()
        ks_addon_data.handle_header(0, ["--enable", "--reserve-mb=256"])
        kdump_check_ks(self, ks_addon_data, ["--enable", "--reserve-mb[=|\ ](\"256\"|'256'|256)[Mm]?"])

    def ks_parse_fadump_to_str_test(self):
        ks_addon_data = new_ks_addon_data()
        ks_addon_data.handle_header(0, ['--enablefadump'])
        kdump_check_ks(self, ks_addon_data, ["--enablefadump"])

    def ks_parse_invalid_reserve_size_test(self):
        with self.assertRaises(KickstartParseError) as error:
            ks_addon_data = new_ks_addon_data()
            ks_addon_data.handle_header(0, ['--reserve-mb='])
        with self.assertRaises(KickstartParseError) as error:
            ks_addon_data = new_ks_addon_data()
            ks_addon_data.handle_header(0, ['--reserve-mb=invalid'])
