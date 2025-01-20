#
# Copyright 2012-2023 Canonical Ltd.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3,
# as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# NOTE: most of this is tested via test_backend_iptables.py since we have to
#       have a backend defined to test backend.py

import unittest
import tests.unit.support
import ufw.backend
import ufw.backend_iptables
import ufw.common
import ufw.kernel_log_backend
import ufw.netfilter_log_backend


class BackendTestCase(unittest.TestCase):
    def setUp(self):
        ufw.common.do_checks = False
        # ufw.backend is an interface, so to test it we need to instantiate
        # an object that implements this interface
        self.backend = ufw.backend_iptables.UFWBackendIptables(dryrun=True)

    def tearDown(self):
        pass

    def test_installation_defaults(self):
        """Test installation defaults"""
        self.assertEqual(self.backend.defaults["default_input_policy"], "drop")
        self.assertEqual(self.backend.defaults["default_forward_policy"], "drop")
        self.assertEqual(self.backend.defaults["default_output_policy"], "accept")
        self.assertTrue("ipt_modules" not in self.backend.defaults)
        self.assertEqual(self.backend.defaults["loglevel"], "low")
        self.assertEqual(self.backend.defaults["manage_builtins"], "no")
        self.assertEqual(self.backend.defaults["enabled"], "no")
        self.assertEqual(self.backend.defaults["ipv6"], "yes")
        self.assertEqual(self.backend.defaults["default_application_policy"], "skip")
        self.assertEqual(self.backend.defaults["logging_backend"], "kernel")
        self.assertTrue("kernel_syslog_level" not in self.backend.defaults)

    def test_get_logging_backend(self):
        """Test get_logging_backend()"""
        be = ufw.backend_iptables.UFWBackendIptables(dryrun=True)

        be.defaults["logging_backend"] = "netfilter"
        obj = be.get_logging_backend()
        self.assertIsInstance(obj, ufw.netfilter_log_backend.UFWLogBackendNetfilter)
        self.assertEqual(obj.get_log_target(), "NFLOG")
        self.assertEqual(obj.get_logging_options(), ["--nflog-prefix"])

        be.defaults["logging_backend"] = "kernel"
        obj = be.get_logging_backend()
        self.assertIsInstance(obj, ufw.kernel_log_backend.UFWLogBackendKernel)
        self.assertEqual(obj.get_log_target(), "LOG")
        self.assertEqual(obj.get_logging_options(), ["--log-prefix"])

        # bad syslog level
        be.defaults["kernel_syslog_level"] = "bad"
        obj = be.get_logging_backend()
        self.assertIsInstance(obj, ufw.kernel_log_backend.UFWLogBackendKernel)
        self.assertEqual(obj.get_log_target(), "LOG")
        self.assertEqual(obj.get_logging_options(), ["--log-prefix"])

        # good syslog level
        for lvl in [
            "emerg",
            "alert",
            "crit",
            "error",
            "warning",
            "warn",
            "notice",
            "info",
            "debug"
        ]:
            be.defaults["kernel_syslog_level"] = lvl
            obj = be.get_logging_backend()
            self.assertIsInstance(obj, ufw.kernel_log_backend.UFWLogBackendKernel)
            self.assertEqual(obj.get_log_target(), "LOG")
            self.assertEqual(obj.get_logging_options(), ["--log-level", lvl, "--log-prefix"])

def test_main():  # used by runner.py
    tests.unit.support.run_unittest(BackendTestCase)


if __name__ == "__main__":  # used when standalone
    unittest.main()
