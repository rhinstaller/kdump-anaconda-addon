# Kdump anaconda configuration
#
# Copyright (C) 2014 Red Hat, Inc.
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
# Red Hat Author(s): David Shea <dshea@redhat.com>
#

"""Kdump anaconda GUI configuration"""

import os.path
from gi.repository import Gtk

from pyanaconda.flags import flags
from pyanaconda.modules.common.constants.services import STORAGE
from pyanaconda.modules.common.util import is_module_available
from pyanaconda.ui.categories.system import SystemCategory
from pyanaconda.ui.gui.spokes import NormalSpoke
from pyanaconda.ui.gui.utils import fancy_set_sensitive
from pyanaconda.ui.communication import hubQ

from com_redhat_kdump.i18n import _, N_
from com_redhat_kdump.constants import FADUMP_CAPABLE_FILE, KDUMP, ENCRYPTION_WARNING
from com_redhat_kdump.common import getTotalMemory, getMemoryBounds, getLuksDevices

__all__ = ["KdumpSpoke"]


class KdumpSpoke(NormalSpoke):
    """Kdump configuration spoke"""

    builderObjects = ["KdumpWindow", "advancedConfigBuffer"]
    mainWidgetName = "KdumpWindow"
    uiFile = "kdump.glade"
    translationDomain = "kdump-anaconda-addon"

    icon = "kdump"
    title = N_("_KDUMP")
    category = SystemCategory

    @staticmethod
    def get_screen_id():
        """Return a unique id of this UI screen."""
        return "kdump-configuration"

    @classmethod
    def should_run(cls, environment, data):
        return is_module_available(KDUMP)

    def __init__(self, *args):
        NormalSpoke.__init__(self, *args)
        self._reserveMem = 0
        self._proxy = KDUMP.get_proxy()
        self._ready = True
        self._luks_devs = []
        self._checked_luks_devs = []

    def initialize(self):
        NormalSpoke.initialize(self)
        self._enableButton = self.builder.get_object("enableKdumpCheck")
        self._reservationTypeLabel = self.builder.get_object("reservationTypeLabel")
        self._autoButton = self.builder.get_object("autoButton")
        self._manualButton = self.builder.get_object("manualButton")
        self._fadumpButton = self.builder.get_object("fadumpCheck")
        self._toBeReservedSpin = self.builder.get_object("toBeReservedSpin")
        self._totalMemMB = self.builder.get_object("totalMemMB")
        self._usableMemMB = self.builder.get_object("usableMemMB")
        self._autoWarn = self.builder.get_object("autoReservationWarning")
        self._reserveTypeGrid = self.builder.get_object("kdumpReserveTypeGrid")
        self._reserveMemoryGrid = self.builder.get_object("kdumpReserveMemoryGrid")

        if os.path.exists(FADUMP_CAPABLE_FILE):
            self._fadumpButton.show()
        else:
            self._fadumpButton.hide()

        # Set an initial value and adjustment on the spin button
        lower, upper, step = getMemoryBounds()
        adjustment = Gtk.Adjustment(lower, lower, upper, step, step, 0)
        self._toBeReservedSpin.set_adjustment(adjustment)
        self._toBeReservedSpin.set_value(lower)

        # Connect a callback to the PropertiesChanged signal.
        storage = STORAGE.get_proxy()
        storage.PropertiesChanged.connect(self._check_storage_change)

    def refresh(self):
        # If a reserve amount is requested, set it in the spin button
        # Strip the trailing 'M'
        reserveMB = self._proxy.ReservedMemory
        if reserveMB != "auto":
            if reserveMB and reserveMB[-1] == 'M':
                reserveMB = reserveMB[:-1]
            if reserveMB:
                self._toBeReservedSpin.set_value(int(reserveMB))

        # Set the various labels. Use the spin button signal handler to set the
        # usable memory label once the other two have been set.
        self._totalMemMB.set_text("%d" % getTotalMemory())
        self._toBeReservedSpin.emit("value-changed")

        # Set the states on the toggle buttons and let the signal handlers set
        # the sensitivities on the related widgets. Set the radio button first,
        # since the radio buttons' bailiwick is a subset of that of the
        # enable/disable checkbox.
        if self._proxy.KdumpEnabled:
            self._enableButton.set_active(True)
            if reserveMB == "auto":
                self._autoButton.set_active(True)
                self._manualButton.set_active(False)
            else:
                self._autoButton.set_active(False)
                self._manualButton.set_active(True)
        else:
            self._enableButton.set_active(False)

        _fadump = self._proxy.FadumpEnabled
        self._fadumpButton.set_active(_fadump)
        # Force a toggled signal on the button in case it's state has not changed
        self._enableButton.emit("toggled")

        self.clear_info()
        if self._luks_devs:
            self.set_warning(_(ENCRYPTION_WARNING))

    def apply(self):
        # Copy the GUI state into the AddonData object
        self._proxy.KdumpEnabled = self._enableButton.get_active()
        if self._autoButton.get_active():
            self._proxy.ReservedMemory = "auto"
        else:
            self._proxy.ReservedMemory = "%dM" % self._toBeReservedSpin.get_value_as_int()
        self._proxy.FadumpEnabled = self._fadumpButton.get_active()

        # This hub have been visited, use should now be aware of the crypted devices issue
        self._checked_luks_devs = self._luks_devs

    def _check_storage_change(self, interface, changed, invalid):
        self._ready = False
        # pylint: disable=no-member
        hubQ.send_not_ready(self.__class__.__name__)

        partition = changed.get("AppliedPartitioning")
        if partition:
            self._luks_devs = getLuksDevices(partition.unpack())

        self._ready = True
        # pylint: disable=no-member
        hubQ.send_ready(self.__class__.__name__)

    @property
    def ready(self):
        return self._ready

    @property
    def completed(self):
        """ Make sure user have checked the warning about crypted devices """
        if self._luks_devs and self._checked_luks_devs != self._luks_devs and not flags.automatedInstall:
            return False
        return True

    @property
    def mandatory(self):
        if self._proxy.KdumpEnabled:
            return True
        return False

    @property
    def status(self):
        if not self._proxy.KdumpEnabled:
            return _("Kdump is disabled")
        if not self._ready:
            return _("Checking storage...")
        if self._luks_devs:
            return _("Kdump may require extra setup for encrypted devices.")
        return _("Kdump is enabled")

    # SIGNAL HANDLERS
    def on_enable_kdump_toggled(self, checkbutton, user_data=None):
        status = checkbutton.get_active()
        # If disabling, hide everything. Otherwise, set the radio
        # button and currently reserved widgets to sensitive and then fake a
        # toggle event on the radio button to set the state on the reserve
        # amount spin button and total/usable mem display.
        self._fadumpButton.set_sensitive(status)
        if status:
            self._autoButton.emit("toggled")
            self._reserveTypeGrid.show()
        else:
            self._autoWarn.hide()
            self._reserveMemoryGrid.hide()
            self._reserveTypeGrid.hide()
            self._fadumpButton.set_active(False)

    def on_reservation_toggled(self, radiobutton, user_data=None):
        status = self._manualButton.get_active()

        # If setting to auto, hide the manual config spinner and
        # the total/usable memory labels
        if status:
            self._autoWarn.hide()
            self._reserveMemoryGrid.show()
            fancy_set_sensitive(self._toBeReservedSpin, status)
        else:
            self._autoWarn.show()
            self._reserveMemoryGrid.hide()

    def on_enable_fadump_toggled(self, checkbutton, user_data=None):
        if self._enableButton.get_active():
            self.enablefadump = self._fadumpButton.get_active()
        else:
            self._fadumpButton.set_active(False)

    def on_reserved_value_changed(self, spinbutton, user_data=None):
        reserveMem = spinbutton.get_value_as_int()
        totalMemText = self._totalMemMB.get_text()

        # If no total memory is available yet, do nothing
        if totalMemText:
            totalMem = int(self._totalMemMB.get_text())
            self._usableMemMB.set_text("%d" % (totalMem - reserveMem))
