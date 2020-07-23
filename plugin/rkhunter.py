# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 Kees de Jong (keesdejong@fedoraproject.org)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Automatic updates of rkhunter property files after DNF transactions"""

from __future__ import absolute_import
import os.path
import re
import subprocess
import time

from dnfpluginsextras import logger
import dnf.cli
import dnf.util


class Rkhunter(dnf.Plugin):
    """DNF plugin for `rkhunter` command"""

    name = "rkhunter"

    def __init__(self, base, cli):
        super().__init__(base, cli)

        self.timestamp = time.time()
        self.base = base
        self.cli = cli
        self.auto_propupd = False
        self.custom_config = ""

    def config(self):
        """Read out the /etc/dnf/plugins/rkhunter.conf config"""

        cp = self.read_config(self.base.conf)

        self.auto_propupd = (
            cp.has_section("main")
            and cp.has_option("main", "auto_propupd")
            and cp.getboolean("main", "auto_propupd")
        )

        self.custom_config = (
            cp.has_section("main")
            and cp.has_option("main", "custom_config")
            and cp.get("main", "custom_config")
        )

    def transaction(self):
        """
        Call after successful transaction
        See https://dnf.readthedocs.io/en/latest/api_plugins.html
        """

        # Don't run rkhunter when preparing chroot for mock
        if self.base.conf.installroot != "/":
            return

        # Don't run rkhunter when "nothing to do"
        if not self.base.transaction:
            return

        # Only run rkhunter when auto_propupd is set to 1
        # in /etc/dnf/plugins/rkhunter.conf
        if self.auto_propupd:

            # Custom rkhunter config has precedence when defined
            # in /etc/dnf/plugins/rkhunter.conf
            # If no custom and no local rkhunter config file is used,
            # use the main one
            for config in [
                self.custom_config,
                "/etc/rkhunter.conf.local",
                "/etc/rkhunter.conf",
            ]:
                if config and os.path.exists(config):
                    logger.debug(
                        "{}: Found rkhunter config {}".format(
                            os.path.abspath(__file__), config
                        )
                    )
                    if parse_config(config):
                        try:
                            subprocess.run(
                                ["/usr/bin/rkhunter", "--propupd"], check=True
                            )
                        except subprocess.CalledProcessError as e:
                            logger.warning(
                                "{}: Error running rkhunter, {}".format(
                                    os.path.abspath(__file__), e
                                )
                            )
                        return

            logger.warning(
                "{}: No valid rkhunter config file found".format(
                    os.path.abspath(__file__)
                )
            )


def parse_config(config):
    """
    Only run rkhunter when the rkhunter config makes use of the hashes,
    attributes or properties
    """
    try:
        with open(config, "r") as f:
            rkhunter_conf = f.read()
            enable_tests = re.findall(
                r"^ENABLE_TESTS\s?=.*(?:all|ALL|properties|attributes|hashes)",
                rkhunter_conf,
                re.MULTILINE,
            )
            disable_tests = re.findall(
                r"^DISABLE_TESTS\s?=.*(?:all|ALL|properties|attributes|hashes)",
                rkhunter_conf,
                re.MULTILINE,
            )
    except IOError as e:
        logger.warning(
            "{}: Error reading rkhunter config file {}, {}".format(
                os.path.abspath(__file__), config, e
            )
        )
        return False

    return enable_tests and not disable_tests
