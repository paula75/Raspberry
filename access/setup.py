
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



# Check WiFi connection
def CheckWiFi(void):
    print("Check wlan0 network")
