# Kdump anaconda configuration
#
# Copyright (C) 2013 Red Hat, Inc.
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

"""Kdump anaconda TUI configuration"""

import re

from pyanaconda.ui.categories.system import SystemCategory
from pyanaconda.ui.tui.spokes import EditTUISpoke
from pyanaconda.ui.tui.spokes import EditTUISpokeEntry as Entry

from com_redhat_kdump.i18n import N_, _
from com_redhat_kdump.constants import CONFIG_FILE

__all__ = ["KdumpSpoke"]

# Allow either "auto" or a string of digits optionally followed by 'M'
RESERVE_VALID = re.compile(r'^((auto)|(\d+M?))$')

class KdumpSpoke(EditTUISpoke):
    title = N_("Kdump")
    category = SystemCategory

    edit_fields = [
        Entry("Enable kdump", "enabled", EditTUISpoke.CHECK, True),
        Entry("Reserve amount", "reserveMB", RESERVE_VALID, lambda self,args: args.enabled)
        ]

    def __init__(self, app, data, storage, payload, instclass):
        EditTUISpoke.__init__(self, app, data, storage, payload, instclass)

        self.args = self.data.addons.com_redhat_kdump

        # Read the config file into data.content so that it will be written
        # to the system even though it is not editable
        try:
            with open(CONFIG_FILE, "r") as fobj:
                self.data.addons.com_redhat_kdump.content = fobj.read()
        except IOError:
            pass

    def apply(self):
        pass

    @property
    def completed(self):
        return True

    @property
    def status(self):
        if self.args.enabled:
            state = _("Kdump is enabled")
        else:
            state = _("Kdump is disabled")

        return state
