import unittest

from unittest.mock import patch
from com_redhat_kdump import common

def enable_kdump_addon_in_anaconda():
    return patch('pyanaconda.kernel.kernel_arguments.is_enabled', return_value=True)

class KdumpTestCase(unittest.TestCase):
    def setUp(self):
        # Clean up global variable that may cache test result of previous test case
        common._reservedMemory = None
