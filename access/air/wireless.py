# iwlistparse.py
# Hugo Chargois - 17 jan. 2010 - v.0.1
# Parses the output of iwlist scan into a table

import sys
import subprocess

import logging
logging.basicConfig(format='%(levelname)s - %(message)s')
logging = logging.getLogger('wireless')

# You can add or change the functions to parse the properties of each AP (cell)
# below. They take one argument, the bunch of text describing one cell in iwlist
# scan and return a property of that cell.


def get_name(cell):
    return matching_line(cell, "ESSID:")[1:-1]


def get_quality(cell):
    quality = matching_line(cell, "Quality=").split()[0].split('/')
    return str(int(round(float(quality[0]) / float(quality[1]) * 100))).rjust(3) + " %"


def get_channel(cell):
    return matching_line(cell, "Channel:")


def get_signal_level(cell):
    # Signal level is on same line as Quality data so a bit of ugly
    # hacking needed...
    return matching_line(cell, "Quality=").split("Signal level=")[1]


def get_encryption(cell):
    enc = ""
    if matching_line(cell, "Encryption key:") == "off":
        enc = "Open"
    else:
        for line in cell:
            matching = match(line, "IE:")
            if matching is not None:
                wpa = match(matching, "WPA Version ")
                if wpa is not None:
                    enc = "WPA v." + wpa
        if enc == "":
            enc = "WEP"
    return enc


def get_address(cell):
    return matching_line(cell, "Address: ")


# Here's a dictionary of rules that will be applied to the description of each
# cell. The key will be the name of the column in the table. The value is a
# function defined above.

rules = {"Name": get_name,
         "Quality": get_quality,
         "Channel": get_channel,
         "Encryption": get_encryption,
         "Address": get_address,
         "Signal": get_signal_level
         }

# Here you can choose the way of sorting the table. sortby should be a key of
# the dictionary rules.


def sort_cells(cells):
    sortby = "Quality"
    reverse = True
    cells.sort(None, lambda el: el[sortby], reverse)


# You can choose which columns to display here, and most importantly in what order. Of
# course, they must exist as keys in the dict rules.

columns = ["Name", "Address", "Quality", "Signal", "Channel", "Encryption"]


# Below here goes the boring stuff. You shouldn't have to edit anything below
# this point
def matching_line(lines, keyword):
    """Returns the first matching line in a list of lines. See match()"""
    for line in lines:
        matching = match(line, keyword)
        if matching is not None:
            return matching
    return None


def match(line, keyword):
    """If the first part of line (modulo blanks) matches keyword,
    returns the end of that line. Otherwise returns None"""
    line = line.lstrip()
    length = len(keyword)
    if line[:length] == keyword:
        return line[length:]
    else:
        return None




def print_table(table):
    # functional magic
    widths = map(max, map(lambda l: map(len, l), zip(*table)))

    justified_table = []
    for line in table:
        justified_line = []
        for i, el in enumerate(line):
            justified_line.append(el.ljust(widths[i] + 2))
        justified_table.append(justified_line)

    for line in justified_table:
        for el in line:
            print el,
        print


def print_cells(cells):
    table = [columns]
    for cell in cells:
        cell_properties = []
        for column in columns:
            cell_properties.append(cell[column])
        table.append(cell_properties)
    print_table(table)


def scan(iface):
    """Parse the output of iwlist scan into a table"""

    cells = [[]]
    parsed_cells = []

    proc = subprocess.Popen(["sudo", "iwlist", iface, "scan"],
                            stdout=subprocess.PIPE, universal_newlines=True)
    out, err = proc.communicate()

    for line in out.split("\n"):
        cell_line = match(line, "Cell ")
        if cell_line is not None:
            cells.append([])
            line = cell_line[-27:]
        cells[-1].append(line.rstrip())

    cells = cells[1:]

    for cell in cells:
        parsed_cells.append(parse_cell(cell))

    sort_cells(parsed_cells)

    # Remove duplicate cells
    filtered_cells = []
    for cell in parsed_cells:
        if not any(c for c in filtered_cells if c['Name'] == cell['Name']):
            filtered_cells.append(cell)

    return filtered_cells


def wpa_supplicant(iface, driver='nl80211', config='/etc/wpa_supplicant/wpa_supplicant.conf'):
    proc = subprocess.Popen(["wpa_supplicant", "-B", "-i%s" % iface, "-D%s" %
                             driver, "-c%s" % config], stdout=subprocess.PIPE, universal_newlines=True)
    out, err = proc.communicate()

    if err:
        logging.warning(err)
        return False

    return True


def dhclient(iface):
    proc = subprocess.Popen(["dhclient", iface],
                            stdout=subprocess.PIPE, universal_newlines=True)
    out, err = proc.communicate()

    if not err:
        return out.rstrip()

    # Log the error if it occurs
    logging.warning(err)
    return False


def wpa_cli(iface, *args):
    proc = subprocess.Popen(["wpa_cli", "-i%s" % iface] + list(args),
                            stdout=subprocess.PIPE, universal_newlines=True)
    out, err = proc.communicate()

    if not err:
        return out.rstrip()

    # Log the error if it occurs
    logging.warning(err)
    return False

def wpa_cli_fail(iface, *args):
    return wpa_cli(iface, *args) == 'FAIL'


def join(iface, ssid, passwd=None):
    network = None
    if not get_network(iface, '0'):
        network = wpa_cli(iface, 'add_network')
    else:
        network = '0'

    if not network:
        logging.warning('Could not add new network')
        return False

    # Set SSID
    if wpa_cli_fail(iface, 'set_network', network, 'ssid', '"%s"' % ssid):
        logging.warning('Could not set network ssid to %s' % ssid)
        return False

    # Set password
    if not passwd and wpa_cli_fail(iface, 'set_network', network, 'key_mgmt', 'NONE'):
        logging.warning('Could not set key_mgmt to none')
        return False
    elif passwd and (wpa_cli_fail(iface, 'set_network', network, 'key_mgmt', 'WPA-PSK') or wpa_cli_fail(iface, 'set_network', network, 'psk', '"%s"' % passwd)):
        logging.warning('Could not set passwd')
        return False

    # Enable network
    if wpa_cli_fail(iface, 'enable_network', network):
        logging.warning('Could not enable network')
        return False

    # Connect
    #if wpa_cli_fail(iface, 'reconnect'):
    #    logging.warning('Could not connect to network')
    #    return False

    # Renew address

    return network

# Check if there is a network saved
def get_network(iface, network):
    ssid = wpa_cli(iface, 'get_network', network, 'ssid')
    if ssid == 'FAIL':
        logging.warning(
            'Could not find ssid information for network %s' % network)
        return False
