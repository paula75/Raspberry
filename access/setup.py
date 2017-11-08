
import os

# Set access point
def AdHocNetwork(void):
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

def movefile(initpath, endpath):
    return os.system('sudo mv ' + initpath + ' ' + endpath)

def copyfile(initpath, endpath):
    return os.system('sudo cp ' + initpath + ' ' + endpath)

# Check WiFi connection
def CheckWiFi(void):
    print("Check wlan0 network")


print("Welcome to hostapd application\n")

print("Move dhcpcd file")
movefile('/etc/dhcpcd.conf', './hostapd/oldfiles')
copyfile('./hostapd/etc/dhcpcd.conf', '/etc/')

print("Move interface file")
movefile('/etc/network/interfaces', './hostapd/oldfiles')
copyfile('./hostapd/etc/network/interfaces', '/etc/network/')

print("Move dnsmasq file")
movefile('/etc/dnsmasq.conf', './hostapd/oldfiles')
copyfile('./hostapd/etc/dnsmasq.conf', '/etc/')

print("copy hostapd file")
copyfile('./hostapd/etc/hostapd/hostapd.conf', '/etc/hostapd/')

print("Move hostapd default file")
movefile('/etc/default/hostapd', './hostapd/oldfiles')
copyfile('./hostapd/etc/default/hostapd', '/etc/default/')

print("Move systemctl file")
movefile('/etc/sysctl.conf', './hostapd/oldfiles')
copyfile('./hostapd/etc/sysctl.conf', '/etc/')
