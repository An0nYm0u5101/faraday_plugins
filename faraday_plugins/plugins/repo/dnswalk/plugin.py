"""
Faraday Penetration Test IDE
Copyright (C) 2013  Infobyte LLC (http://www.infobytesec.com/)
See the file 'doc/LICENSE' for the license information

"""
import re
import os

from faraday_plugins.plugins.plugin import PluginBase
from faraday_plugins.plugins.plugins_utils import resolve_hostname

current_path = os.path.abspath(os.getcwd())

__author__ = "Francisco Amato"
__copyright__ = "Copyright (c) 2013, Infobyte LLC"
__credits__ = ["Francisco Amato"]
__license__ = ""
__version__ = "1.0.0"
__maintainer__ = "Francisco Amato"
__email__ = "famato@infobytesec.com"
__status__ = "Development"


class DnswalkParser:
    """
    The objective of this class is to parse an xml file generated
    by the dnswalk tool.

    TODO: Handle errors.
    TODO: Test dnswalk output version. Handle what happens if the parser
    doesn't support it.
    TODO: Test cases.

    @param dnswalk_filepath A proper simple report generated by dnswalk
    """

    def __init__(self, output):

        lists = output.split("\n")
        self.items = []

        for line in lists:
            mregex = re.search("WARN: ([\w\.]+) ([\w]+) ([\w\.]+):", line)
            if mregex is not None:

                item = {
                    'host': mregex.group(1),
                    'ip': mregex.group(3),
                    'type': mregex.group(2)}

                self.items.append(item)

            mregex = re.search(
                "Getting zone transfer of ([\w\.]+) from ([\w\.]+)\.\.\.done\.",
                line)

            if mregex is not None:
                ip = resolve_hostname(mregex.group(2))
                item = {
                    'host': mregex.group(1),
                    'ip': ip,
                    'type': 'info'}
                self.items.append(item)



class DnswalkPlugin(PluginBase):
    """
    Example plugin to parse dnswalk output.
    """

    def __init__(self):
        super().__init__()
        self.id = "Dnswalk"
        self.name = "Dnswalk XML Output Plugin"
        self.plugin_version = "0.0.1"
        self.version = "2.0.2"
        self.options = None
        self._current_output = None
        self._current_path = None
        self._command_regex = re.compile(
            r'^(sudo dnswalk |dnswalk |\.\/dnswalk ).*?')

        global current_path

    def canParseCommandString(self, current_input):
        if self._command_regex.match(current_input.strip()):
            return True
        else:
            return False

    def parseOutputString(self, output, debug=False):
        """
        output is the shell output of command Dnswalk.
        """
        parser = DnswalkParser(output)

        for item in parser.items:

            if item['type'] == "A":

                h_id = self.createAndAddHost(item['ip'])
                i_id = self.createAndAddInterface(
                    h_id,
                    item['ip'],
                    ipv4_address=item['ip'],
                    hostname_resolution=[item['host']])

            elif item['type'] == "info":

                h_id = self.createAndAddHost(item['ip'])

                i_id = self.createAndAddInterface(
                    h_id,
                    item['ip'],
                    ipv4_address=item['ip'],
                    hostname_resolution=[item['host']])

                s_id = self.createAndAddServiceToInterface(
                    h_id,
                    i_id,
                    "domain",
                    "tcp",
                    ports=['53'])

                self.createAndAddVulnToService(
                    h_id,
                    s_id,
                    "Zone transfer",
                    desc="A Dns server allows unrestricted zone transfers",
                    ref=["CVE-1999-0532"])

        return True


def createPlugin():
    return DnswalkPlugin()

# I'm Py3
