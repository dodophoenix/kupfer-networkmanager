#!/bin/bash
BASE=`dirname "$(readlink -f "$0")"`
ln -s "${BASE}/vpn-nmcli.py" /usr/share/kupfer/kupfer/plugin/vpn-nmcli.py