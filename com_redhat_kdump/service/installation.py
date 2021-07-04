#
# Copyright (C) 2020 Red Hat, Inc.
#
# This copyrighted material is made available to anyone wishing to use,
# modify, copy, or redistribute it subject to the terms and conditions of
# the GNU General Public License v.2, or (at your option) any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY expressed or implied, including the implied warranties of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License for more details.  You should have received a copy of the
# GNU General Public License along with this program; if not, write to the
# Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.  Any Red Hat trademarks that are incorporated in the
# source code or documentation are not subject to the GNU General Public
# License and may only be used or replicated with the express permission of
# Red Hat, Inc.
#
import logging
import os

from pyanaconda.core import util
from pyanaconda.modules.common.constants.objects import BOOTLOADER
from pyanaconda.modules.common.constants.services import STORAGE, PAYLOADS
from pyanaconda.modules.common.task import Task
from pyanaconda.modules.payloads.payload.dnf.utils import get_kernel_version_list

from com_redhat_kdump.constants import FADUMP_CAPABLE_FILE, CRASHKERNEL_DEFAULT_FILE, ENCRYPTION_WARNING
from com_redhat_kdump.common import getLuksDevices

log = logging.getLogger(__name__)

__all__ = ["KdumpBootloaderConfigurationTask", "KdumpInstallationTask"]


class KdumpBootloaderConfigurationTask(Task):
    """The bootloader configuration task for kdump and fadump"""

    def __init__(self, kernels, sysroot, kdump_enabled, fadump_enabled, reserved_memory):
        """Create a task."""
        super().__init__()
        self._kernels = kernels
        self._sysroot = sysroot
        self._kdump_enabled = kdump_enabled
        self._fadump_enabled = fadump_enabled
        self._reserved_memory = reserved_memory

    @property
    def name(self):
        return "Configure kernel parameters for kdump and fadump"

    def run(self):
        """Run the task."""
        if getLuksDevices():
            log.warning(ENCRYPTION_WARNING)

        # Update the bootloader arguments.
        bootloader_proxy = STORAGE.get_proxy(BOOTLOADER)

        # Clear any existing crashkernel bootloader arguments.
        args = [
            arg for arg in bootloader_proxy.ExtraArguments
            if not arg.startswith('crashkernel=')
        ]

        # Enable fadump.
        if self._fadump_enabled and os.path.exists(FADUMP_CAPABLE_FILE):
            args.append('fadump=on')

        # Set crashkernel argument
        if self._kdump_enabled:
            ck_arg = None

            if self._reserved_memory == 'auto':
                # Try to get crashkernel arg from crashkernel.con
                if len(self._kernels) > 1:
                    log.warning("crashkernel=auto specified, and multiple kernels installed, "
                                "will use crashkernel.default value from latest installed kernel.")

                for k in self._kernels:
                    ck_conf_file = "%s/%s" % (self._sysroot, CRASHKERNEL_DEFAULT_FILE % k)
                    if os.path.exists(ck_conf_file):
                        with open(ck_conf_file, 'r') as ck_conf:
                            ck_arg = ck_conf.read().rstrip()
                            log.debug("Using default crashkernel cmdline ('%s') from '%s'",
                                      ck_arg, ck_conf_file)
                            break

                if ck_arg is None:
                    log.warning("Can't find a valid crashkernel.default from the installation, "
                                "falling back to use installer kernel's crashkernel.default")
                    ck_conf_file = CRASHKERNEL_DEFAULT_FILE % os.uname().release
                    if os.path.exists(ck_conf_file):
                        with open(ck_conf_file, 'r') as ck_conf:
                            ck_arg = ck_conf.read().rstrip()
                            log.debug("Using default crashkernel cmdline ('%s') from '%s'",
                                      ck_arg, ck_conf_file)

                if ck_arg is None:
                    log.error("Can't find a valid crashkernel.default, will set crashkernel=auto.")
                    ck_arg = 'crashkernel=auto'

            else:
                # Ensure that the amount is an amount in MB.
                if self._reserved_memory[-1] != 'M':
                    self._reserved_memory += 'M'
                ck_arg = 'crashkernel=%s' % self._reserved_memory

            args.append(ck_arg)

        bootloader_proxy.SetExtraArguments(args)


class KdumpInstallationTask(Task):
    """The installation task for installation of kdump."""

    def __init__(self, sysroot, kdump_enabled):
        """Create a task."""
        super().__init__()
        self._sysroot = sysroot
        self._kdump_enabled = kdump_enabled

    @property
    def name(self):
        return "Enable the kdump.service"

    def run(self):
        """Run the task."""
        if not self._kdump_enabled:
            log.debug("Kdump is disabled. Skipping.")
            return

        util.execWithRedirect(
            "systemctl",
            ["enable", "kdump.service"],
            root=self._sysroot
        )
