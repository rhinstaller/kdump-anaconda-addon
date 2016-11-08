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

import os.path
from pyanaconda.addons import AddonData
from pyanaconda import iutil
from pyanaconda.flags import flags

from pykickstart.options import KSOptionParser
from pykickstart.errors import KickstartParseError, formatErrorMsg
from com_redhat_kdump.common import getMemoryBounds
from com_redhat_kdump.i18n import _
from com_redhat_kdump.constants import FADUMP_CAPABLE_FILE

__all__ = ["KdumpData"]

class KdumpData(AddonData):
    """Addon data for the kdump configuration"""

    def __init__(self, name):
        AddonData.__init__(self, name)

        self.enabled = False
        lower, upper, step = getMemoryBounds()
        self.reserveMB = "%d" % lower
        self.enablefadump = False

    def __str__(self):
        addon_str = "%%addon %s" % self.name

        if self.enabled:
            addon_str += " --enable"
        else:
            addon_str += " --disable"

        if self.reserveMB:
            addon_str += " --reserve-mb='%s'" % self.reserveMB

        if self.enablefadump:
            addon_str += " --enablefadump"

        addon_str += "\n%s\n%%end\n" % self.content.strip()

        return addon_str

    def setup(self, storage, ksdata, instClass, payload):
        # the kdump addon should run only if requested
        if not flags.cmdline.getbool("kdump_addon", default=False):
            return

        # Clear any existing crashkernel bootloader arguments
        if ksdata.bootloader.appendLine:
            ksdata.bootloader.appendLine = ' '.join(
                    (arg for arg in ksdata.bootloader.appendLine.split() \
                            if not arg.startswith('crashkernel=')))

        # Copy our reserved amount to the bootloader arguments
        if self.enabled:
            # Ensure that the amount is an amount in MB
            if self.reserveMB[-1] != 'M':
                self.reserveMB += 'M'
            ksdata.bootloader.appendLine += ' crashkernel=%s' % self.reserveMB

        # Do the same thing with the storage.bootloader.boot_args set
        if storage.bootloader.boot_args:
            crashargs = [arg for arg in storage.bootloader.boot_args \
                    if arg.startswith('crashkernel=')]
            storage.bootloader.boot_args -= set(crashargs)

        if self.enabled:
            storage.bootloader.boot_args.add('crashkernel=%s' % self.reserveMB)
            ksdata.packages.packageList.append("kexec-tools")
        if self.enablefadump and os.path.exists(FADUMP_CAPABLE_FILE):
                storage.bootloader.boot_args.add('fadump=on')

    def handle_header(self, lineno, args):
        op = KSOptionParser()
        op.add_option("--enable", action="store_true", default=True,
                dest="enabled", help="Enable kdump")
        op.add_option("--enablefadump", action="store_true", default=False,
                dest="enablefadump", help="Enable dump mode fadump")
        op.add_option("--disable", action="store_false",
                dest="enabled", help="Disable kdump")
        op.add_option("--reserve-mb", type="string", dest="reserveMB",
                default="128", help="Amount of memory in MB to reserve for kdump.")

        (opts, extra) = op.parse_args(args=args, lineno=lineno)

        # Reject any additional arguments
        if extra:
            AddonData.handle_header(self, lineno, extra)

        # Validate the reserve-mb argument
        # Allow a final 'M' for consistency with the crashkernel kernel
        # parameter. Strip it if found.
        if opts.reserveMB and opts.reserveMB[-1] == 'M':
            opts.reserveMB = opts.reserveMB[:-1]

        try:
            _test = int(opts.reserveMB)
        except ValueError:
            msg = _("Invalid value %s for --reserve-mb") % opts.reserveMB
            if lineno != None:
                raise KickstartParseError(formatErrorMsg(lineno, msg=msg))
            else:
                raise KickstartParseError(msg)

        # Store the parsed arguments
        self.enabled = opts.enabled
        self.reserveMB =opts.reserveMB
        self.enablefadump = opts.enablefadump

    def execute(self, storage, ksdata, instClass, users, payload):
        # the KdumpSpoke should run only if requested
        if not flags.cmdline.getbool("kdump_addon", default=False):
            return

        if self.enabled:
            action = "enable"
        else:
            action = "disable"

        iutil.execWithRedirect("systemctl", [action, "kdump.service"], root=iutil.getSysroot())
