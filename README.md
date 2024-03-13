# vpn-nmcli

Plugin for the [Kupfer Launcher](https://github.com/kupferlauncher/kupfer) 
to connect and disconnect vpn-connections managed by network-manager.
It uses `nmcli`- command  to work.

Tested with nmcli 
* 1.2.6
* nmcli 1.20.4-1.kupfer v319
* nmcli 1.46.0-2 kupfer v325-1


## install 
```
git clone https://github.com/dodophoenix/kupfer-networkmanager
cd kupfer-networkmanager
sudo install-plugin.sh
```
The file `vpn-nmcli.py` gets copied to the plugin directory of the launcher.
Restart the Laucher 
Activate VPN-NMCLI . 


### Hint
This plugin requires the network manager command line interface. 
In order to use it one must install the network manager 
and use it.

Ubuntu/Debian: `apt-get install network-manager`\
Arch: `pacman -S networkmanager`

## dev
use `link-plugin.sh` to link the `vpn-nmcli.py`
to the dir for development 
