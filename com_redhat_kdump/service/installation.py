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
from pyanaconda.modules.common.constants.services import STORAGE
from pyanaconda.modules.common.task import Task

from com_redhat_kdump.constants import FADUMP_CAPABLE_FILE

log = logging.getLogger(__name__)

__all__ = ["KdumpConfigurationTask", "KdumpInstallationTask"]


class KdumpConfigurationTask(Task):
    """The installation task for configuration of the runtime environment."""

    def __init__(self, kdump_enabled, fadump_enabled, reserved_memory):
        """Create a task."""
        super().__init__()
        self._kdump_enabled = kdump_enabled
        self._fadump_enabled = fadump_enabled
        self._reserved_memory = reserved_memory

    @property
    def name(self):
        return "Configure kdump and fadump"

    def run(self):
        """Run the task."""
        # Update the bootloader arguments.
        bootloader_proxy = STORAGE.get_proxy(BOOTLOADER)

        # Clear any existing crashkernel bootloader arguments.
        args = [
            arg for arg in bootloader_proxy.ExtraArguments
            if not arg.startswith('crashkernel=')
        ]

        # Copy our reserved amount to the bootloader arguments.
        if self._kdump_enabled:
            # Ensure that the amount is an amount in MB.
            if self._reserved_memory[-1] != 'M':
                self._reserved_memory += 'M'

            args.append('crashkernel=%s' % self._reserved_memory)

        # Enable fadump.
        if self._fadump_enabled and os.path.exists(FADUMP_CAPABLE_FILE):
            args.append('fadump=on')

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
