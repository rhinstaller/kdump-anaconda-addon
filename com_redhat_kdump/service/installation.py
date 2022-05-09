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

from com_redhat_kdump.constants import FADUMP_CAPABLE_FILE
from com_redhat_kdump.common import getLuksDevices

log = logging.getLogger(__name__)

__all__ = ["KdumpBootloaderConfigurationTask", "KdumpInstallationTask"]


class KdumpBootloaderConfigurationTask(Task):
    """The bootloader configuration task for kdump and fadump"""

    def __init__(self, sysroot, kdump_enabled, fadump_enabled, reserved_memory):
        """Create a task."""
        super().__init__()
        self._sysroot = sysroot
        self._kdump_enabled = kdump_enabled
        self._fadump_enabled = fadump_enabled
        self._reserved_memory = reserved_memory

    @property
    def name(self):
        return "Configure kernel parameters for kdump and fadump"

    def get_default_crashkernel(self, fadump_enabled):
        dump_mode = 'kdump'
        if fadump_enabled:
            dump_mode = 'fadump'

        args = {'command': 'kdumpctl',
                'argv': ['get-default-crashkernel', dump_mode],
                'root': self._sysroot,
                'filter_stderr': True}

        ck_val = None
        try:
            ck_val = util.execWithCapture(**args)
        except FileNotFoundError:
            log.warning("Can't retrieve the default crashkernel value from "
                        "the installed kexec-tools, try to retrieve it from "
                        "the installer kexec-tools")

        if not ck_val:
            del args['root']
            # If the installer doesn't have kdumpctl, the target system's
            # kdumpctl i.e. /mnt/sysimage/bin/kdumpctl would be used again. To
            # prevent this, exeplicty ask for the installer's kdumpctl
            args['command'] = '/usr/bin/kdumpctl'
            try:
                ck_val = util.execWithCapture(**args)
            except FileNotFoundError:
                log.warning("Can't retrieve the default crashkernel value "
                            "from installer kexec-tools either because it's "
                            "not installed")
                pass

        if ck_val:
            # remove the trailing newline otherwise installing bootloader would
            # fail
            return ck_val.rstrip()

        return None

    def run(self):
        """Run the task."""
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
            if self._reserved_memory == 'auto':
                ck_arg = None
                ck_val = self.get_default_crashkernel(self._fadump_enabled)
                if ck_val:
                    ck_arg = 'crashkernel=%s' % ck_val
                else:
                    log.error("Can't retrieve the default crashkernel, will set crashkernel=auto.")
                    ck_arg = 'crashkernel=auto'

            else:
                # Ensure that the amount is an amount in MB.
                if self._reserved_memory[-1] != 'M':
                    self._reserved_memory += 'M'
                ck_arg = 'crashkernel=%s' % self._reserved_memory

            args.append(ck_arg)

        bootloader_proxy.ExtraArguments = args


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
