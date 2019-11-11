import os
from jinja2 import Template

from arkclient import ArkClient, ArkApiError
from netassign import _addVirtualInterface, _delAllInterfaces, _getIp, _getInterfaceNameFromIp, _getSubnetMaskFromIp


def getArkAddrs(name=None, server=None, user=None, passwd=None, register=None, count=None, **_):
    # TODO: Validate the values here
    client = ArkClient(server)
    try:
        client.login(user, passwd)
    except:
        raise Exception("Couldn't log in to the Ark...")

    # Register the new halo if it doesnt exist already
    register = register.lower().strip() in ["true", "yes", "1", "t"]
    halos = [x.lower() for x in client.getHalos()['halos']]
    exists = name.lower() in halos
    if not register and not exists:
        print("[!] No Halo with the name {} exists and the Halo is not authorized to register with the Ark".format(name))
        print("    set THEARK_REGISTER=True to automatically register the Halo")
        quit(1)
    if not exists:
        print("[*] Registering {} with The Ark".format(name))
        print("[*] Collecting {} addresses for {}...".format(count, name))
        try:
            addrs = client.registerHalo(name, count)
        except ArkApiError:
            addrs = client.getAddresses(name)
    else:
        addrs = client.getAddresses(name)
        print("[*] {} addresses assigned to {}".format(len(addrs), name))
    return addrs


def allocateIPs(data):
    valid_ips = []
    device = os.environ.get("INTERFACE_NAME", "")
    if not device:
        # In this situation, we get the IP address that the target IP would be connected with
        # not the default gateway
        # I realize this function will error if there are no IPs, but that _shouldnt_ happen
        ip = _getIp(data['addresses'][0])
        device = _getInterfaceNameFromIp(ip)
        netmask = _getSubnetMaskFromIp(ip)
        print("[+] Detected interface: {}: {}{}".format(device, ip, netmask))
    else:
        netmask = os.environ.get("INTERFACE_MASK", "/24")

    # Delete any interfaces using the IP address
    print("[*] Deleting old interfaces....")
    _delAllInterfaces(device, label="ark")
    print("[*] Adding new interfaces")
    for i in data['addresses']:
        try:
            _addVirtualInterface(i, device, netmask, data['name'])
            valid_ips.append(i)
        except ValueError as E:
            print("[!] Cannot add virtual IP", i, type(E), E)
    return valid_ips


def buildServer(data):
    valid_ips = allocateIPs(data)
    if not valid_ips:
        raise ValueError("ERROR: No virtual IP aliases could be added. Shutting down")
    
    if len(valid_ips) < len(data.get("addresses", [])):
        print("WARNING: Not all IP addresses have been allocated")

    data['addresses'] = valid_ips

    with open('nginx.conf') as fil:
        template = Template(fil.read())

    nginx_conf = template.render(config=data)

    print(nginx_conf)
    with open("/etc/nginx/nginx.conf", "w+") as fil:
        fil.write(nginx_conf)


def main():
    # Figure out if we are using a configuration file for addresses or getting them from the Ark

    config = {}
    config['upstream'] = os.environ.get("HALO_UPSTREAM", "")
    addrs = None
    ark = False
    if os.environ.get("THEARK_USER") and os.environ.get("THEARK_PASS"):
        config['user'] = os.environ.get("THEARK_USER")
        config['passwd'] = os.environ.get("THEARK_PASS")
        config['server'] = os.environ.get("THEARK_SERVER")
        config['name'] = os.environ.get("HALO_NAME", "")
        config['register'] = os.environ.get('THEARK_REGISTER', "True")
        count = os.environ.get('HALO_ADDR_COUNT', "15")
        try:
            count = int(count)
        except ValueError:
            count = 15
        config['count'] = count
        config['addresses'] = getArkAddrs(**config).get("addresses", [])
        ark = True
    # Use the config file if we dont have Ark
    """
    if not addrs:
        config_path = os.environ.get("HALO_CONFIG", "config.yml")
        if os.path.exists(config_path):
            with open(config_path) as fil:
                config = yaml.safe_load(fil)
            if not isinstance(config['addresses'], list):
                raise ValueError("Invalid addresses in {}. Must be an array".format(config_path))
    """
    # Validate that we have some IP addresses
    if not config.get("addresses", []):
        raise ValueError("ERROR: Config file not specified or Ark credentials not supplied")

    buildServer(config)
    if ark:
        print("In order to view the IP addresses assigned to {}, navigate to {}".format(
            config['name'], os.environ.get("THEARK_SERVER")))


if __name__ == "__main__":
    main()
