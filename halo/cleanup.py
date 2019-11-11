import os
from netassign import _getIp, _getInterfaceNameFromIp, _getSubnetMaskFromIp, _delAllInterfaces

device = os.environ.get("INTERFACE_NAME", "")
if not device:
    # In this situation, we get the IP address that the target IP would be connected with
    # not the default gateway
    # I realize this function will error if there are no IPs, but that _shouldnt_ happen
    ip = _getIp()
    device = _getInterfaceNameFromIp(ip)
    netmask = _getSubnetMaskFromIp(ip)
    print("[+] Detected interface: {}: {}{}".format(device, ip, netmask))
else:
    netmask = os.environ.get("INTERFACE_MASK", "/24")

# Delete any interfaces using the IP address
print("[*] Deleting old interfaces....")
_delAllInterfaces(device, label="ark")