
import os
import subprocess

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

def append_text(out):
    cells = []
    for line in out.split(" "):
        cells.append(line)
    return cells


def checkWiFi():
    proc = subprocess.Popen(["iwconfig"],
            stdout=subprocess.PIPE, universal_newlines=True)
    out, err = proc.communicate()
    state = matching_line(append_text(out), "ESSID:")
    if state == "off/any":
        return False
    else:
        return True

# Set access point
def hotspot_up(void):
    print("configuration WiFi host")
    # stop processes
    os.system('sudo systemctl stop dnsmasq')
    os.system('sudo systemctl stop hostapd')

    print("Modifing files")
    # Set up ipv4 forwarding
    os.system('sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE')
    os.system('sudo iptables -A FORWARD -i eth0 -o wlan0 -m state --state RELATED,ESTABLISHED -j ACCEPT')
    os.system('sudo iptables -A FORWARD -i wlan0 -o eth0 -j ACCEPT')

    #Restart dhcpcd daemon
    os.system('service dhcpcd restart')

    # Set up wlan0 configuration
    os.system('sudo ifdown wlan0')
    os.system('sudo ifup wlan0')


def hostspot_down(void):
    return True


def movefile(initpath, endpath):
    return os.system('sudo mv ' + initpath + ' ' + endpath)

def copyfile(initpath, endpath):
    return os.system('sudo cp ' + initpath + ' ' + endpath)

def configure_files():

    movefile('/etc/dhcpcd.conf', './hostapd/oldfiles')
    copyfile('./hostapd/etc/dhcpcd.conf', '/etc/')

    movefile('/etc/network/interfaces', './hostapd/oldfiles')
    copyfile('./hostapd/etc/network/interfaces', '/etc/network/')

    movefile('/etc/dnsmasq.conf', './hostapd/oldfiles')
    copyfile('./hostapd/etc/dnsmasq.conf', '/etc/')

    copyfile('./hostapd/etc/hostapd/hostapd.conf', '/etc/hostapd/')

    movefile('/etc/default/hostapd', './hostapd/oldfiles')
    copyfile('./hostapd/etc/default/hostapd', '/etc/default/')

    movefile('/etc/sysctl.conf', './hostapd/oldfiles')
    copyfile('./hostapd/etc/sysctl.conf', '/etc/')


print("Welcome to hostapd application\n")
if checkWiFi():
    print("There is a WiFi connection\n")
else:
    print("There is not WiFi connection\n")
