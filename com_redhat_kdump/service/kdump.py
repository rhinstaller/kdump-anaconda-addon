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

from pyanaconda.core.configuration.anaconda import conf
from pyanaconda.core.dbus import DBus
from pyanaconda.core.signal import Signal
from pyanaconda.modules.common.base import KickstartService
from pyanaconda.modules.common.containers import TaskContainer
from pyanaconda.modules.common.structures.requirement import Requirement

from com_redhat_kdump.common import getMemoryBounds
from com_redhat_kdump.constants import KDUMP
from com_redhat_kdump.service.installation import KdumpConfigurationTask, KdumpInstallationTask
from com_redhat_kdump.service.kdump_interface import KdumpInterface
from com_redhat_kdump.service.kickstart import KdumpKickstartSpecification

log = logging.getLogger(__name__)

__all__ = ["KdumpService"]


class KdumpService(KickstartService):
    """The implementation of the Kdump service."""

    def __init__(self):
        """Create a service."""
        super().__init__()
        self._kdump_enabled = False
        self.kdump_enabled_changed = Signal()

        self._fadump_enabled = False
        self.fadump_enabled_changed = Signal()

        lower, upper, step = getMemoryBounds()
        self._reserved_memory = "%d" % lower
        self.reserved_memory_changed = Signal()

    def publish(self):
        """Publish the DBus objects."""
        TaskContainer.set_namespace(KDUMP.namespace)
        DBus.publish_object(KDUMP.object_path, KdumpInterface(self))
        DBus.register_service(KDUMP.service_name)

    @property
    def kdump_enabled(self):
        """Is kdump enabled?"""
        return self._kdump_enabled

    @kdump_enabled.setter
    def kdump_enabled(self, value):
        self._kdump_enabled = value
        self.kdump_enabled_changed.emit()
        log.debug("Kdump enabled is set to '%s'.", value)

    @property
    def fadump_enabled(self):
        """Is fadump enabled?"""
        return self._fadump_enabled

    @fadump_enabled.setter
    def fadump_enabled(self, value):
        self._fadump_enabled = value
        self.fadump_enabled_changed.emit()
        log.debug("Fadump enabled is set to '%s'.", value)

    @property
    def reserved_memory(self):
        """Amount of memory in MB to reserve for kdump."""
        return self._reserved_memory

    @reserved_memory.setter
    def reserved_memory(self, value):
        self._reserved_memory = value
        self.reserved_memory_changed.emit()
        log.debug("Reserved memory is set to '%s'.", value)

    @property
    def kickstart_specification(self):
        """Return the kickstart specification."""
        return KdumpKickstartSpecification

    def process_kickstart(self, data):
        """Process the kickstart data."""
        self.kdump_enabled = data.addons.com_redhat_kdump.enabled
        self.fadump_enabled = data.addons.com_redhat_kdump.enablefadump
        self.reserved_memory = data.addons.com_redhat_kdump.reserve_mb

    def setup_kickstart(self, data):
        """Set the given kickstart data."""
        data.addons.com_redhat_kdump.enabled = self.kdump_enabled
        data.addons.com_redhat_kdump.enablefadump = self.fadump_enabled
        data.addons.com_redhat_kdump.reserve_mb = self.reserved_memory

    def collect_requirements(self):
        """Return installation requirements.

        :return: a list of requirements
        """
        requirements = []

        if self.kdump_enabled:
            requirements.append(
                Requirement.for_package(
                    package_name="kexec-tools",
                    reason="Required by kdump add-on."
                )
            )

        return requirements

    def configure_with_tasks(self):
        """Return configuration tasks.

        :return: a list of tasks
        """
        return [
            KdumpConfigurationTask(
                kdump_enabled=self.kdump_enabled,
                fadump_enabled=self.fadump_enabled,
                reserved_memory=self.reserved_memory
            )
        ]

    def install_with_tasks(self):
        """Return installation tasks.

        :return: a list of tasks
        """
        return [
            KdumpInstallationTask(
                sysroot=conf.target.system_root,
                kdump_enabled=self.kdump_enabled,
            )
        ]
