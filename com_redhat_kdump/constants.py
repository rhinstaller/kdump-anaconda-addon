# Kdump configuration constants
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
from dasbus.identifier import DBusServiceIdentifier

from pyanaconda.core.dbus import DBus
from pyanaconda.modules.common.constants.namespaces import ADDONS_NAMESPACE

# The constants
FADUMP_CAPABLE_FILE = "/proc/device-tree/rtas/ibm,configure-kernel-dump"
CRASHKERNEL_DEFAULT_FILE = "/usr/lib/modules/%s/crashkernel.default"

# DBus constants
KDUMP_NAMESPACE = (
    *ADDONS_NAMESPACE,
    "Kdump"
)

KDUMP = DBusServiceIdentifier(
    namespace=KDUMP_NAMESPACE,
    message_bus=DBus
)

# To mark ENCRYPTION_WARNING as translatable
_ = lambda x: x
ENCRYPTION_WARNING = _('Encrypted storage is in use, using an encrypted device as dump target for kdump might fail. Please verify if kdump is working properly after the installation finished. For more details see the "Notes on encrypted dump target" section in /usr/share/doc/kexec-tools/kexec-kdump-howto.txt.')
