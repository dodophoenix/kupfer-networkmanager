"""
It *should* be possible to support Tomboy and Gnote equally since
they support the same DBus protocol. This plugin takes this assumption.
"""
__kupfer_name__ = _("VPN - NMCLI")
__kupfer_sources__ = ("ConnectionSource",)
__kupfer_actions__ = ("Connect", "Disconnect",)
__description__ = _("Connects and Disconnects vpn Connections using nmcli command")
__version__ = ""
__author__ = "Benjamin Jacob <benni.jacob@gmail.com>"

from kupfer.objects import Action, Source, Leaf, TextLeaf
from kupfer.obj.apps import ApplicationSource
from kupfer import icons
import subprocess
import os
import time

# icons
connection_icon = "security-high"
source_icon = "network-vpn"
action_connect = "network-connect"
action_disconnect = "network-disconnect"

# cli - commands
listConnections = "nmcli -t -f uuid,name,type connection show"
activeUuids = "nmcli -t -f uuid connection show --active"
connectUUid = "nmcli connection up "
disconnectUUid = "nmcli connection down "


class Connect(Action):
    def __init__(self):
        Action.__init__(self, _("Connect"))

    def activate(self, leaf):
        """thingy"""
        run_cmd(connectUUid + leaf.uuid, True)
        leaf.active=True

    def get_description(self):
        return _("connects a vpn connection")

    def get_icon_name(self):
        return action_connect

    def get_gicon(self):
        return icons.ComposedIcon(source_icon, action_connect)


class Disconnect(Action):
    def __init__(self):
        Action.__init__(self, _("Disconnect"))

    def activate(self, leaf):
        """thingy"""
        run_cmd(disconnectUUid + leaf.uuid, True)
        leaf.active=False

    def get_description(self):
        return _("disconnects a vpn connection")

    def get_icon_name(self):
        return action_disconnect

    def get_gicon(self):
        return icons.ComposedIcon(source_icon, action_disconnect)


class ConnectionSource(ApplicationSource):
    source_user_reloadable = False
    appleaf_content_id = "vpn-nmcli"
    source_use_cache = False

    def is_dynamic(self):
        """
        Whether to recompute contents each time it is accessed
        """
        return True

    def __init__(self):
        self.connections = []
        Source.__init__(self, _("VPN - Connections"))

    def initialize(self):
        active_ids = []
        (stdout, exitcode) = run_cmd(activeUuids)
        lines = stdout.split("\n")
        for activeUuid in lines:
            if not activeUuid:
                continue
            active_ids.append(activeUuid)

        (stdout, exitcode) = run_cmd(listConnections)
        lines = stdout.split("\n")
        for connStr in lines:
            if not connStr:
                continue
            parts = connStr.split(":")
            uuid = parts[0]
            name = parts[1]
            type = parts[2]

            if type != "vpn":
                continue
            active = False
            if uuid in active_ids:
                active = True
            self.connections.append(Connection(uuid, name, active))

    def get_items(self):
        """thing"""
        self.initialize()
        for connection in self.connections:
            yield connection

    def get_icon_name(self):
        return source_icon

    def provides(self):
        yield Connection


class Connection(Leaf):
    """The Note Leaf's represented object is the Note URI"""

    def __init__(self, uuid, name, active):
        self.uuid = uuid
        self.name = name
        self.active = active
        Leaf.__init__(self, self.uuid, name)

    def get_actions(self):
        if not self.active:
            yield Connect()
            yield Disconnect()
        else:
            yield Disconnect()
            yield Connect()

    def repr_key(self):
        # the Note URI is unique&persistent for each note
        return self.uuid

    def get_description(self):

        connected = "Verbunden"
        if not self.active:
            connected = "Getrennt"
        return "Die Verbindung " + str(self.name) + " ist " + connected

    def get_icon_name(self):
        return connection_icon

    def get_gicon(self):
       if self.active:
           return icons.ComposedIcon(source_icon, action_connect)
       else:
           return icons.ComposedIcon(source_icon, action_disconnect)


def run_cmd(cmd, async=False):
    process = subprocess.Popen(cmd,
                               shell=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT,
                               universal_newlines=True,
                               preexec_fn=os.setpgrp)
    if (async):
        return
    # collect stdout & stderr
    stdoutdata = ""
    for line in iter(process.stdout.readline, b''):
        stdoutdata = stdoutdata + line

    result = None
    cntGate = 0
    while result is None:
        result = process.poll()
        cntGate += 1
        if cntGate > 50:
            break
        time.sleep(0.2)
    return [stdoutdata, process.returncode]
