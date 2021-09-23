import os
from unittest.case import TestCase
from unittest.mock import patch
from com_redhat_kdump.constants import FADUMP_CAPABLE_FILE, CRASHKERNEL_DEFAULT_FILE
from com_redhat_kdump.service.installation import KdumpBootloaderConfigurationTask, KdumpInstallationTask
from .mock import MockBuiltinRead, MockOsPathExists

SYSROOT = "/sysroot"
CRASHKERNEL_FIXTURE = {
    SYSROOT + CRASHKERNEL_DEFAULT_FILE % '5.13': "crashkernel=3G",
    SYSROOT + CRASHKERNEL_DEFAULT_FILE % '5.12': "crashkernel=2G",
    SYSROOT + CRASHKERNEL_DEFAULT_FILE % '5.11': "crashkernel=1G",
    CRASHKERNEL_DEFAULT_FILE % os.uname().release: "crashkernel=256M",
}

class KdumpInstallationTestCase(TestCase):

    @patch("com_redhat_kdump.common.STORAGE")
    @patch("com_redhat_kdump.service.installation.STORAGE")
    def test_configuration_kdump_disabled(self, mock_storage, partition_storage):
        bootloader_proxy = mock_storage.get_proxy.return_value
        bootloader_proxy.ExtraArguments = [
            "a=1", "b=2", "c=3", "crashkernel=128M"
        ]

        partition_proxy = partition_storage.get_proxy.return_value
        partition_proxy.CreatedPartitioning = []

        task = KdumpBootloaderConfigurationTask(
            kernels=[],
            sysroot="/",
            kdump_enabled=False,
            fadump_enabled=False,
            reserved_memory="256"
        )
        task.run()

        bootloader_proxy.SetExtraArguments.assert_called_once_with([
            "a=1", "b=2", "c=3"
        ])

    @patch("com_redhat_kdump.common.STORAGE")
    @patch("com_redhat_kdump.service.installation.STORAGE")
    def test_configuration_kdump_enabled(self, mock_storage, partition_storage):
        bootloader_proxy = mock_storage.get_proxy.return_value
        bootloader_proxy.ExtraArguments = [
            "a=1", "b=2", "c=3", "crashkernel=128M"
        ]

        partition_proxy = partition_storage.get_proxy.return_value
        partition_proxy.CreatedPartitioning = []

        task = KdumpBootloaderConfigurationTask(
            kernels=[],
            sysroot="/",
            kdump_enabled=True,
            fadump_enabled=False,
            reserved_memory="128"
        )
        task.run()

        bootloader_proxy.SetExtraArguments.assert_called_once_with([
            "a=1", "b=2", "c=3", "crashkernel=128M"
        ])

    @patch("com_redhat_kdump.common.STORAGE")
    @patch("com_redhat_kdump.service.installation.os")
    @patch("com_redhat_kdump.service.installation.STORAGE")
    def test_configuration_fadump_enabled(self, mock_storage, mock_os, partition_storage):
        bootloader_proxy = mock_storage.get_proxy.return_value
        bootloader_proxy.ExtraArguments = [
            "a=1", "b=2", "c=3", "crashkernel=256M"
        ]

        partition_proxy = partition_storage.get_proxy.return_value
        partition_proxy.CreatedPartitioning = []

        task = KdumpBootloaderConfigurationTask(
            kernels=[],
            sysroot="/",
            kdump_enabled=False,
            fadump_enabled=True,
            reserved_memory="256"
        )
        task.run()

        mock_os.path.exists.assert_called_once_with(FADUMP_CAPABLE_FILE)
        bootloader_proxy.SetExtraArguments.assert_called_once_with([
            "a=1", "b=2", "c=3", "fadump=on"
        ])

    @patch("com_redhat_kdump.common.STORAGE")
    @patch("builtins.open", MockBuiltinRead(CRASHKERNEL_FIXTURE))
    @patch("os.path.exists", MockOsPathExists(CRASHKERNEL_FIXTURE))
    @patch("com_redhat_kdump.service.installation.STORAGE")
    def test_configuration_kdump_crashkernel_auto(self, mock_storage, partition_storage):
        bootloader_proxy = mock_storage.get_proxy.return_value
        bootloader_proxy.ExtraArguments = [
            "a=1", "b=2", "c=3", "crashkernel=auto"
        ]

        partition_proxy = partition_storage.get_proxy.return_value
        partition_proxy.CreatedPartitioning = []

        task = KdumpBootloaderConfigurationTask(
            kernels=['5.13'],
            sysroot=SYSROOT,
            kdump_enabled=True,
            fadump_enabled=False,
            reserved_memory="auto"
        )
        task.run()

        bootloader_proxy.SetExtraArguments.assert_called_once_with([
            "a=1", "b=2", "c=3", "crashkernel=3G"
        ])

    @patch("com_redhat_kdump.common.STORAGE")
    @patch("builtins.open", MockBuiltinRead(CRASHKERNEL_FIXTURE))
    @patch("os.path.exists", MockOsPathExists(CRASHKERNEL_FIXTURE))
    @patch("com_redhat_kdump.service.installation.STORAGE")
    def test_configuration_kdump_crashkernel_auto_fallback(self, mock_storage, partition_storage):
        bootloader_proxy = mock_storage.get_proxy.return_value
        bootloader_proxy.ExtraArguments = [
            "a=1", "b=2", "c=3", "crashkernel=auto"
        ]

        partition_proxy = partition_storage.get_proxy.return_value
        partition_proxy.CreatedPartitioning = []

        task = KdumpBootloaderConfigurationTask(
            kernels=['non-exist'],
            sysroot=SYSROOT,
            kdump_enabled=True,
            fadump_enabled=False,
            reserved_memory="auto"
        )
        task.run()

        bootloader_proxy.SetExtraArguments.assert_called_once_with([
            "a=1", "b=2", "c=3", "crashkernel=256M"
        ])

    @patch("com_redhat_kdump.common.STORAGE")
    @patch("builtins.open", MockBuiltinRead({}))
    @patch("os.path.exists", MockOsPathExists({}))
    @patch("com_redhat_kdump.service.installation.STORAGE")
    def test_configuration_kdump_crashkernel_auto_fallback_legacy(self, mock_storage, partition_storage):
        bootloader_proxy = mock_storage.get_proxy.return_value
        bootloader_proxy.ExtraArguments = [
            "a=1", "b=2", "c=3", "crashkernel=auto"
        ]

        partition_proxy = partition_storage.get_proxy.return_value
        partition_proxy.CreatedPartitioning = []

        task = KdumpBootloaderConfigurationTask(
            kernels=['non-exist'],
            sysroot=SYSROOT,
            kdump_enabled=True,
            fadump_enabled=False,
            reserved_memory="auto"
        )
        task.run()

        bootloader_proxy.SetExtraArguments.assert_called_once_with([
            "a=1", "b=2", "c=3", "crashkernel=auto"
        ])

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
