from unittest.case import TestCase
from unittest.mock import patch
from com_redhat_kdump.constants import FADUMP_CAPABLE_FILE
from com_redhat_kdump.service.installation import KdumpConfigurationTask, KdumpInstallationTask


class KdumpInstallationTestCase(TestCase):

    @patch("com_redhat_kdump.service.installation.STORAGE")
    def configuration_kdump_disabled_test(self, mock_storage):
        bootloader_proxy = mock_storage.get_proxy.return_value
        bootloader_proxy.ExtraArguments = [
            "a=1", "b=2", "c=3", "crashkernel=128M"
        ]

        task = KdumpConfigurationTask(
            kdump_enabled=False,
            fadump_enabled=False,
            reserved_memory="256"
        )
        task.run()

        bootloader_proxy.SetExtraArguments.assert_called_once_with([
            "a=1", "b=2", "c=3"
        ])

    @patch("com_redhat_kdump.service.installation.STORAGE")
    def configuration_kdump_enabled_test(self, mock_storage):
        bootloader_proxy = mock_storage.get_proxy.return_value
        bootloader_proxy.ExtraArguments = [
            "a=1", "b=2", "c=3", "crashkernel=128M"
        ]

        task = KdumpConfigurationTask(
            kdump_enabled=True,
            fadump_enabled=False,
            reserved_memory="256"
        )
        task.run()

        bootloader_proxy.SetExtraArguments.assert_called_once_with([
            "a=1", "b=2", "c=3", "crashkernel=256M"
        ])

    @patch("com_redhat_kdump.service.installation.os")
    @patch("com_redhat_kdump.service.installation.STORAGE")
    def configuration_fadump_enabled_test(self, mock_storage, mock_os):
        bootloader_proxy = mock_storage.get_proxy.return_value
        bootloader_proxy.ExtraArguments = [
            "a=1", "b=2", "c=3", "crashkernel=128M"
        ]

        task = KdumpConfigurationTask(
            kdump_enabled=False,
            fadump_enabled=True,
            reserved_memory="256"
        )
        task.run()

        mock_os.path.exists.assert_called_once_with(FADUMP_CAPABLE_FILE)
        bootloader_proxy.SetExtraArguments.assert_called_once_with([
            "a=1", "b=2", "c=3", "fadump=on"
        ])

    @patch("com_redhat_kdump.service.installation.util")
    def installation_kdump_disabled_test(self, mock_util):
        task = KdumpInstallationTask(
            sysroot="/mnt/sysroot",
            kdump_enabled=False
        )
        task.run()
        mock_util.execWithRedirect.assert_not_called()

    @patch("com_redhat_kdump.service.installation.util")
    def installation_kdump_enabled_test(self, mock_util):
        task = KdumpInstallationTask(
            sysroot="/mnt/sysroot",
            kdump_enabled=True
        )
        task.run()
        mock_util.execWithRedirect.assert_called_once_with(
            "systemctl",
            ["enable", "kdump.service"],
            root="/mnt/sysroot"
        )
