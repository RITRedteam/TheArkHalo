import os
import yaml
from jinja2 import Template

from arkclient import ArkClient, ArkApiError
from netassign import _addVirtualInterface, _delAllInterfaces, _getIp, _getInterfaceNameFromIp


def getArkAddrs(name=None, server=None, user=None, passwd=None, register=None, count=None, **_):
    # TODO: Validate the values here
    client = ArkClient(server)
    try:
        client.login(user, passwd)
    except:
        raise Exception("Couldn't log in to the Ark...")

    # Register the new halo if it doesnt exist already
    register = register.lower().strip() in ["true", "yes", "1", "t"]
    if register and name.lower() not in [x.lower() for x in client.getHalos()]:
        print("Registering {} with The Ark".format(name))
        print("Collecting {} addresses for {}".format(count, name))
        try:
            addrs = client.registerHalo(name, count)
        except ArkApiError:
            addrs = client.getAddresses(name)
    else:
        print("Halo is not registered, getting IPs")
        addrs = client.getAddresses(name)
        print(addrs)
    return addrs


def allocateIPs(data):
    valid_ips = []
    device = os.environ.get("INTERFACE_NAME", "")
    if not device:
        device = _getInterfaceNameFromIp(_getIp())
    # Delete any interfaces using the IP address
    _delAllInterfaces(device, label=data.get('name', ''))

    for i in data['addresses']:
        try:
            print("Adding virtual IP", i)
            _addVirtualInterface(i, device, data['name'])
            valid_ips.append(i)
        except ValueError as E:
            print("Cannot add virtual IP", i, type(E), E)
    return valid_ips


def buildServer(data):
    valid_ips = allocateIPs(data)
    if not valid_ips:
        raise ValueError("ERROR: No virtual IP aliases could be added. Shutting down")

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
        config['server'] = os.environ.get("THEARK_SERVER", "http://0.0.0.0:5000")
        config['name'] = os.environ.get("HALO_NAME", "")
        config['register'] = os.environ.get('THEARK_REGISTER', "False")
        count = os.environ.get('HALO_ADDR_COUNT', "15")
        try:
            count = int(count)
        except ValueError:
            count = 15
        config['count'] = count
        config['addresses'] = getArkAddrs(**config)
        ark = True
    # Use the config file if we dont have Ark
    if not addrs:
        config_path = os.environ.get("HALO_CONFIG", "config.yml")
        if os.path.exists(config_path):
            with open(config_path) as fil:
                config = yaml.safe_load(fil)
            if not isinstance(config['addresses'], list):
                raise ValueError("Invalid addresses in {}. Must be an array".format(config_path))

    # Validate that we have some IP addresses
    if not config.get("addresses", []):
        raise ValueError("ERROR: Config file not specified or Ark credentials not supplied")

    buildServer(config)
    if ark:
        print("In order to view the IP addresses assigned to {}, navigate to {}".format(
            config['name'], os.environ.get("THEARK_SERVER", "http://0.0.0.0:5000")))


if __name__ == "__main__":
    main()