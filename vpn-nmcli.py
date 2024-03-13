"""
Start/Stop connections of NetworkManager via nmclia
"""
__kupfer_name__ = _("VPN - NMCLI")
__kupfer_sources__ = ("ConnectionSource",)
__kupfer_actions__ = ("Connect", "Disconnect",)
__description__ = _("Connects and Disconnects vpn Connections using nmcli command")
__version__ = ""
__author__ = "Benjamin Jacob <benni.jacob@gmail.com>"

from kupfer.obj import Action, Source, Leaf, TextLeaf
from kupfer.obj.apps import ApplicationSource
from kupfer import icons
from kupfer import utils
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

# display only VPN connections
vpnonly = True
# if vpnonly is set to true only valid_types are listed as available connections
# types compared against output of type field in `nmcli -t -f uuid,name,type connection show`
valid_types = ["vpn", "wireguard"]

# print debugging output
verbose = False

class Connect(Action):
    def __init__(self, ranked=50):
        Action.__init__(self, _("Connect"))
        self.rank_adjust = ranked

    def activate(self, leaf):
        run_cmd(connectUUid + leaf.uuid, True)
        leaf.active = True

    def get_description(self):
        return _("connects a vpn connection")

    def get_icon_name(self):
        return action_connect

    def get_gicon(self):
        return icons.ComposedIcon(source_icon, action_connect)


class Disconnect(Action):
    def __init__(self, ranked=50):
        Action.__init__(self, _("Disconnect"))
        self.rank_adjust = ranked

    def activate(self, leaf):
        run_cmd(disconnectUUid + leaf.uuid, True)
        leaf.active = False

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

    def __init__(self, name=_("VPN - NMCLI")):
        super().__init__(name)
        self.connections = []
        self.active_ids = []

        # dont query connection - state in short intervals < 10 secs
        self.last_update_con_state = 0
        self.max_age_con_state_secs = 10

        # available connections don't change often
        self.last_update_connections = 0
        self.max_age_connections_secs = 120

        Source.__init__(self, _("VPN - Connections"))

    def update_connection_states(self):
        self.active_ids = []
        if verbose:
            print("query connection state")
        (stdout, exitcode) = run_cmd(activeUuids)
        lines = stdout.split("\n")
        for activeUuid in lines:
            if not activeUuid:
                continue
            self.active_ids.append(activeUuid)

        for con in self.connections:
            con.active = con.uuid in self.active_ids
            if verbose:
                print("connection "+con.name+" is active:"+str(con.uuid in self.active_ids))

    def update_available_connections(self):
        if verbose:
            print("query overall available connections")
        (stdout, exitcode) = run_cmd(listConnections, False)
        lines = stdout.split("\n")
        for connStr in lines:
            if not connStr:
                continue
            parts = connStr.split(":")
            con_type = parts[2]

            if vpnonly and con_type not in valid_types:
                continue

            uuid = parts[0]
            name = parts[1]
            active = False
            if verbose:
                print("connection "+name+" is active " + str(active))
            self.connections.append(Connection(uuid, name, active))

    def initialize(self):
        now = time.time()
        if now - self.max_age_connections_secs > self.last_update_connections:
            self.update_available_connections()
            self.last_update_connections = now

        if now - self.max_age_con_state_secs > self.last_update_con_state:
            self.update_connection_states()
            self.last_update_con_state = now

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
        if self.active:
            yield Disconnect(99)
            yield Connect(70)
        else:
            yield Connect(99)
            yield Disconnect(70)

    def repr_key(self):
        # the Note URI is unique&persistent for each note
        return self.uuid

    def get_description(self):
        # TODO: how to translate this ?
        connected = _("established")
        if not self.active:
            connected =_("closed")
        return _("The connection") + " "+str(self.name) + " " + _("is") + " " + connected

    def get_icon_name(self):
        return connection_icon

    def get_gicon(self):
        if self.active:
            return icons.ComposedIcon(source_icon, action_connect)
        else:
            return icons.ComposedIcon(source_icon, action_disconnect)


def run_cmd(cmd, call_async=False):
    if verbose:
        print("exec cmd: " + cmd)
    process = subprocess.Popen(cmd,
                               shell=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT,
                               universal_newlines=True,
                               preexec_fn=os.setpgrp)
    try:
        stdoutdata, errs = process.communicate(timeout=15)
    except subprocess.TimeoutExpired:
        process.kill()
        stdoutdata, errs = process.communicate()
    return [stdoutdata, process.returncode]

