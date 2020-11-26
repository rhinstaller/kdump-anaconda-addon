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
from dasbus.server.interface import dbus_interface
from dasbus.server.property import emits_properties_changed
from dasbus.typing import *  # pylint: disable=wildcard-import

from pyanaconda.modules.common.base import KickstartModuleInterface
from com_redhat_kdump.constants import KDUMP

__all__ = ["KdumpInterface"]


@dbus_interface(KDUMP.interface_name)
class KdumpInterface(KickstartModuleInterface):
    """The DBus interface of the Kdump service."""

    def connect_signals(self):
        super().connect_signals()
        self.watch_property("KdumpEnabled", self.implementation.kdump_enabled_changed)
        self.watch_property("FadumpEnabled", self.implementation.fadump_enabled_changed)
        self.watch_property("ReservedMemory", self.implementation.reserved_memory_changed)

    @property
    def KdumpEnabled(self) -> Bool:
        """Is kdump enabled?

        :return: True or False
        """
        return self.implementation.kdump_enabled

    @KdumpEnabled.setter
    @emits_properties_changed
    def KdumpEnabled(self, value: Bool):
        self.implementation.kdump_enabled = value

    @property
    def FadumpEnabled(self) -> Bool:
        """Is fadump enabled?

        :return: True or False
        """
        return self.implementation.fadump_enabled

    @FadumpEnabled.setter
    @emits_properties_changed
    def FadumpEnabled(self, value: Bool):
        self.implementation.fadump_enabled = value

    @property
    def ReservedMemory(self) -> Str:
        """Amount of memory in MB to reserve for kdump.

        :return: a string with the number of MB
        """
        return self.implementation.reserved_memory

    @ReservedMemory.setter
    @emits_properties_changed
    def ReservedMemory(self, value: Str):
        self.implementation.reserved_memory = value
