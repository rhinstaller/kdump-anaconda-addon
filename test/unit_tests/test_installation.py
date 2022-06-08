from unittest.case import TestCase
from unittest.mock import patch
from com_redhat_kdump.constants import FADUMP_CAPABLE_FILE
from com_redhat_kdump.service.installation import KdumpBootloaderConfigurationTask, KdumpInstallationTask

SYSROOT = "/sysroot"

class KdumpInstallationTestCase(TestCase):

    @patch("pyanaconda.core.util.execWithCapture")
    @patch("com_redhat_kdump.service.installation.STORAGE")
    def test_configuration_kdump_disabled(self, mock_storage, mock_exec):
        bootloader_proxy = mock_storage.get_proxy.return_value
        bootloader_proxy.ExtraArguments = [
            "a=1", "b=2", "c=3", "crashkernel=128M"
        ]

        task = KdumpBootloaderConfigurationTask(
            sysroot="/",
            kdump_enabled=False,
            fadump_enabled=False,
            reserved_memory="256"
        )
        task.run()

        assert bootloader_proxy.ExtraArguments == [
            "a=1", "b=2", "c=3"
        ]
        mock_exec.assert_not_called()

    @patch("pyanaconda.core.util.execWithCapture")
    @patch("com_redhat_kdump.service.installation.STORAGE")
    def test_configuration_kdump_enabled(self, mock_storage, mock_exec):
        bootloader_proxy = mock_storage.get_proxy.return_value
        bootloader_proxy.ExtraArguments = [
            "a=1", "b=2", "c=3", "crashkernel=128M"
        ]

        task = KdumpBootloaderConfigurationTask(
            sysroot="/",
            kdump_enabled=True,
            fadump_enabled=False,
            reserved_memory="128"
        )
        task.run()

        assert bootloader_proxy.ExtraArguments == [
            "a=1", "b=2", "c=3", "crashkernel=128M"
        ]
        mock_exec.assert_not_called()

    @patch("pyanaconda.core.util.execWithCapture")
    def test_configuration_get_default_crashkernel_file_not_found(self, mock_exec):
        mock_exec.side_effect = [None, FileNotFoundError]
        task = KdumpBootloaderConfigurationTask(
            sysroot="/",
            kdump_enabled=False,
            fadump_enabled=True,
            reserved_memory="auto"
        )
        res = task.get_default_crashkernel('kdump')
        assert mock_exec.call_count == 2
        assert res is None

    @patch("pyanaconda.core.util.execWithCapture")
    def test_configuration_get_default_crashkernel_empty(self, mock_exec):
        mock_exec.return_value = None
        task = KdumpBootloaderConfigurationTask(
            sysroot="/",
            kdump_enabled=False,
            fadump_enabled=True,
            reserved_memory="auto"
        )
        res = task.get_default_crashkernel('kdump')
        assert mock_exec.call_count == 2
        assert res is None

    @patch("pyanaconda.core.util.execWithCapture")
    def test_configuration_get_default_crashkernel(self, mock_exec):
        mock_exec.return_value = '256M'
        task = KdumpBootloaderConfigurationTask(
            sysroot="/",
            kdump_enabled=False,
            fadump_enabled=True,
            reserved_memory="auto"
        )
        res = task.get_default_crashkernel('fadump')
        mock_exec.assert_called_once()
        assert res is '256M'

    @patch("pyanaconda.core.util.execWithCapture")
    @patch("com_redhat_kdump.service.installation.os")
    @patch("com_redhat_kdump.service.installation.STORAGE")
    def test_configuration_fadump_enabled(self, mock_storage, mock_os, mock_exec):
        bootloader_proxy = mock_storage.get_proxy.return_value
        bootloader_proxy.ExtraArguments = [
            "a=1", "b=2", "c=3", "crashkernel=256M"
        ]

        task = KdumpBootloaderConfigurationTask(
            sysroot="/",
            kdump_enabled=False,
            fadump_enabled=True,
            reserved_memory="256"
        )
        task.run()

        mock_os.path.exists.assert_called_once_with(FADUMP_CAPABLE_FILE)
        assert bootloader_proxy.ExtraArguments == [
            "a=1", "b=2", "c=3", "fadump=on"
        ]
        mock_exec.assert_not_called()

    @patch("pyanaconda.core.util.execWithCapture")
    @patch("com_redhat_kdump.service.installation.STORAGE")
    def test_configuration_kdump_crashkernel_auto(self, mock_storage, mock_exec):
        mock_exec.return_value = '3G'
        bootloader_proxy = mock_storage.get_proxy.return_value
        bootloader_proxy.ExtraArguments = [
            "a=1", "b=2", "c=3", "crashkernel=auto"
        ]

        task = KdumpBootloaderConfigurationTask(
            sysroot=SYSROOT,
            kdump_enabled=True,
            fadump_enabled=False,
            reserved_memory="auto"
        )
        task.run()

        assert bootloader_proxy.ExtraArguments == [
            "a=1", "b=2", "c=3", "crashkernel=3G"
        ]

        mock_exec.assert_called_once()

    @patch("pyanaconda.core.util.execWithCapture")
    @patch("com_redhat_kdump.service.installation.STORAGE")
    def test_configuration_kdump_crashkernel_auto_fallback(self, mock_storage, mock_exec):
        mock_exec.return_value = '256M'
        mock_exec.side_effect = [None, '333M']
        bootloader_proxy = mock_storage.get_proxy.return_value
        bootloader_proxy.ExtraArguments = [
            "a=1", "b=2", "c=3", "crashkernel=auto"
        ]

        task = KdumpBootloaderConfigurationTask(
            sysroot=SYSROOT,
            kdump_enabled=True,
            fadump_enabled=False,
            reserved_memory="auto"
        )
        task.run()

        assert bootloader_proxy.ExtraArguments == [
            "a=1", "b=2", "c=3", "crashkernel=333M"
        ]

        assert mock_exec.call_count == 2

    @patch("pyanaconda.core.util.execWithCapture")
    @patch("com_redhat_kdump.service.installation.STORAGE")
    def test_configuration_kdump_crashkernel_auto_fallback_legacy(self, mock_storage, mock_exec):
        mock_exec.return_value = None
        bootloader_proxy = mock_storage.get_proxy.return_value
        bootloader_proxy.ExtraArguments = [
            "a=1", "b=2", "c=3", "crashkernel=auto"
        ]

        task = KdumpBootloaderConfigurationTask(
            sysroot=SYSROOT,
            kdump_enabled=True,
            fadump_enabled=False,
            reserved_memory="auto"
        )
        task.run()

        assert bootloader_proxy.ExtraArguments == [
            "a=1", "b=2", "c=3", "crashkernel=auto"
        ]
        assert mock_exec.call_count == 2

    @patch("com_redhat_kdump.service.installation.util")
    def test_installation_kdump_disabled(self, mock_util):
        task = KdumpInstallationTask(
            sysroot="/mnt/sysroot",
            kdump_enabled=False
        )
        task.run()
        mock_util.execWithRedirect.assert_not_called()

    @patch("com_redhat_kdump.service.installation.util")
    def test_installation_kdump_enabled(self, mock_util):
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
