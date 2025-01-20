#!/bin/bash

#    Copyright 2008-2025 Canonical Ltd.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License version 3,
#    as published by the Free Software Foundation.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

source "$TESTPATH/../testlib.sh"
sed -i 's/IPV6=no/IPV6=yes/' $TESTPATH/etc/default/ufw

# This isn't available everywhere, so we will test it later
sed -i "s/self.caps\['limit'\]\['6'\] = True/self.caps['limit']['6'] = False/" $TESTPATH/lib/python/ufw/backend.py

do_cmd "0" nostats disable
do_cmd "0" nostats enable

echo "TESTING LOG RULES WITH KERNEL_SYSLOG_LEVEL" >> $TESTTMP/result
sed -i 's/#KERNEL_SYSLOG_LEVEL=.*/KERNEL_SYSLOG_LEVEL="info"/' $TESTPATH/etc/default/ufw
from="2001:db8::/32"
to="2001:db8:3:4:5:6:7:8"
for i in allow deny limit reject ; do
    for j in log log-all ; do
        do_cmd "0" nostats $i $j 23
        do_cmd "0" nostats $i $j Samba
        do_cmd "0" nostats $i $j from $from to $to port smtp

        do_cmd "0" nostats disable
        do_cmd "0" nostats enable

        do_cmd "0" nostats delete $i $j 23
        do_cmd "0" nostats delete $i $j Samba
        do_cmd "0" nostats delete $i $j from $from to $to port smtp
    done
done

cleanup
exit 0
