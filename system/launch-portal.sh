#!/bin/bash

# -vx

HERE=$(cd $(dirname $0) ; /bin/pwd)
. $HERE/config.sh

/sbin/ifconfig | grep -q $PORTAL_INTF && echo "access point already mounted, abort" && exit 0

echo "Mounting access point"

# add "access point" interface to wifi card
/sbin/iw phy $PORTAL_PHY interface add $PORTAL_INTF type __ap

# get mac address of main wlan, and generate another one (+1) to differentiate AP and main one
mac=$(/sbin/iw dev $PORTAL_INTF info|sed -n 's/.*addr \(.*\)/\1/p')
mac=$(echo $mac | cut -c 1-16)$(echo $mac | cut -c 17 | tr '0-9a-f' '1-9a-f0')
/sbin/ifconfig $PORTAL_INTF hw ether $mac
/sbin/ifconfig $PORTAL_INTF $PORTAL_IP up

#sleep 1
echo "Setting iptables rules"

# iptables rules to redirect everything to portal web server
#/sbin/iptables -t nat -I PREROUTING -i $PORTAL_INTF -p tcp --dport 80 -j DNAT --to-destination $PORTAL_IP:$PORTAL_PORT
#/sbin/iptables -t nat -I PREROUTING -i $PORTAL_INTF -p udp --dport 53 -j DNAT --to-destination $PORTAL_IP

echo "Done."

