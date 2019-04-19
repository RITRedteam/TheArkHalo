from netassign import _addVirtualInterface, _delAllInterfaces
DEVICE = "ens160"
"""
def main(ips):
    for ip in ips:
        _addVirtualInterface(ip, "ens160")

main(["10.4.2.50", "10.4.3.245"])
"""
_delAllInterfaces()
