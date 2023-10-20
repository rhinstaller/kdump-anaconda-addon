from unittest.case import TestCase
from unittest.mock import patch
from unittest.mock import Mock

from com_redhat_kdump import common
from com_redhat_kdump.constants import KDUMP
from com_redhat_kdump.service.kdump import KdumpService
from com_redhat_kdump.service.kdump_interface import KdumpInterface


class PropertiesChangedCallback(Mock):

    def __call__(self, interface, changed, invalid):
        changed = {k: v.unpack() for k, v in changed.items()}
        return super().__call__(interface, changed, invalid)


class KdumpInterfaceTestCase(TestCase):

    def setUp(self):
        # Show unlimited diff.
        self.maxDiff = None

        # Clean up global variable that may cache test result of previous test case
        common._reservedMemory = None

        # Create the Kdump service.
        self._service = KdumpService()
        self._interface = KdumpInterface(self._service)

        # Monitor the PropertiesChanged signal.
        self._callback = PropertiesChangedCallback()
        self._interface.PropertiesChanged.connect(self._callback)

    def _check_properties_changed(self, property_name, value):
        self._callback.assert_called_once_with(
            KDUMP.interface_name,
            {property_name: value},
            []
        )

    def test_kdump_enabled(self):
        self._interface.KdumpEnabled = True
        self._check_properties_changed("KdumpEnabled", True)
        self.assertEqual(self._interface.KdumpEnabled, True)

    def test_fadump_enabled(self):
        self._interface.FadumpEnabled = True
        self._check_properties_changed("FadumpEnabled", True)
        self.assertEqual(self._interface.FadumpEnabled, True)

    def test_reserved_memory(self):
        self._interface.ReservedMemory = "256"
        self._check_properties_changed("ReservedMemory", "256")
        self.assertEqual(self._interface.ReservedMemory, "256")

    @patch("com_redhat_kdump.service.kdump.getMemoryBounds", return_value = (500, 800, 1))
    def test_check_reserved_memory(self, mocker):
        service1 = KdumpService()
        for memory, reserved in [("900", "800"), ("400", "500"), ("600", "600")]:
            self.assertEqual(service1.check_reserved_memory(memory), reserved)
