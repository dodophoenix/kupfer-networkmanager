# vpn-nmcli

Plugin for the [Kupfer Launcher](https://github.com/kupferlauncher/kupfer) 
to connect and disconnect vpn-connections managed by network-manager.
It uses `nmcli`- command  to work.

Tested with nmcli 1.2.6

## install 
```
git clone https://github.com/dodophoenix/kupfer-networkmanager
cd kupfer-networkmanager
sudo install-plugin.sh
```
The file `vpn-nmcli.py` gets copied to the plugin directory of the launcher.
Restart the Laucher 
Activate VPN-NMCLI . 


## dev
use `link-plugin.sh` to link the `vpn-nmcli.py`
to the dir for development 
