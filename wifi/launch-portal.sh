#!/bin/bash

HERE=$(cd $(dirname $0) ; /bin/pwd)
. $HERE/config.sh

echo "Mounting access point"

# add "access point" interface to wifi card
iw phy $PHY interface add $INT_IF type __ap

# get mac address of main wlan, and generate another one (+1) to differentiate AP and main one
mac=$(iw dev $INT_IF info|sed -n 's/.*addr \(.*\)/\1/p')
mac=$(echo $mac | cut -c 1-16)$(echo $mac | cut -c 17 | tr '0-9a-f' '1-9a-f0')
ifconfig $INT_IF hw ether $mac
ifconfig $INT_IF $IP_CAPTIVE_PORTAL up

#sleep 1
echo "Setting iptables rules"

# iptables rules to redirect everything to portal web server
#/sbin/iptables -t nat -I PREROUTING -i $INT_IF -p tcp --dport 80 -j DNAT --to-destination $IP_CAPTIVE_PORTAL:$PORT_CAPTIVE_PORTAL
#/sbin/iptables -t nat -I PREROUTING -i $INT_IF -p udp --dport 53 -j DNAT --to-destination $IP_CAPTIVE_PORTAL

echo "Done."

