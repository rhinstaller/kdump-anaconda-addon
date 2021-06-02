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

from pykickstart.errors import KickstartParseError
from pykickstart.options import KSOptionParser
from pykickstart.version import F27

from pyanaconda.core.kickstart import KickstartSpecification
from pyanaconda.core.kickstart.addon import AddonData

from com_redhat_kdump.i18n import _

log = logging.getLogger(__name__)

__all__ = ["KdumpKickstartSpecification"]


class KdumpKickstartData(AddonData):
    """The kickstart data for the com_redhat_kdump add-on."""

    def __init__(self):
        super().__init__()
        self.enabled = False
        self.reserve_mb = "auto"
        self.enablefadump = False

    def __str__(self):
        """Generate the kickstart representation."""
        addon_str = "%addon com_redhat_kdump"

        if self.enabled:
            addon_str += " --enable"
        else:
            addon_str += " --disable"

        if self.enabled and self.reserve_mb:
            addon_str += " --reserve-mb='%s'" % self.reserve_mb

        if self.enablefadump:
            addon_str += " --enablefadump"

        addon_str += "\n\n%end\n"
        return addon_str

    def handle_header(self, args, line_number=None):
        """Handle the arguments of the %addon line.

        :param args: a list of additional arguments
        :param line_number: a line number
        :raise: KickstartParseError for invalid arguments
        """
        op = KSOptionParser(
            prog="addon com_redhat_kdump", version=F27,
            description="Configure the Kdump Addon."
        )
        op.add_argument(
            "--enable", action="store_true", default=True,
            version=F27, dest="enabled", help="Enable kdump"
        )
        op.add_argument(
            "--enablefadump", action="store_true", default=False,
            version=F27, dest="enablefadump", help="Enable dump mode fadump"
        )
        op.add_argument(
            "--disable", action="store_false",
            version=F27, dest="enabled", help="Disable kdump"
        )
        op.add_argument(
            "--reserve-mb", type=str, dest="reserve_mb",
            version=F27, default="auto", help="Amount of memory in MB to reserve for kdump."
        )

        opts = op.parse_args(args=args, lineno=line_number)

        # Validate the reserve-mb argument
        # Allow a final 'M' for consistency with the crashkernel kernel
        # parameter. Strip it if found. And strip quotes.
        opts.reserve_mb = opts.reserve_mb.strip("'\"")

        if opts.reserve_mb and opts.reserve_mb[-1] == 'M':
            opts.reserve_mb = opts.reserve_mb[:-1]

        if opts.reserve_mb != "auto":
            try:
                _test = int(opts.reserve_mb)
            except ValueError:
                msg = _("Invalid value '%s' for --reserve-mb") % opts.reserve_mb
                raise KickstartParseError(msg, lineno=line_number)

        # Store the parsed arguments
        self.enabled = opts.enabled
        self.reserve_mb = opts.reserve_mb
        self.enablefadump = opts.enablefadump

    def handle_line(self, line, line_number=None):
        """Handle one line of the section.

        :param line: a line to parse
        :param line_number: a line number
        :raise: KickstartParseError for invalid lines
        """
        pass


class KdumpKickstartSpecification(KickstartSpecification):
    """The kickstart specification of the Kdump service."""

    addons = {
        "com_redhat_kdump": KdumpKickstartData
    }
