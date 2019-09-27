from subprocess import Popen, PIPE
import random
import socket
import os


def execute(args):
    '''
    Execute a command. Pass the args as an array if there is more than one
    '''
    retval = {'status': 255}
    try:
        proc = Popen(args, shell=True, stdout=PIPE, stderr=PIPE, stdin=PIPE,
                     close_fds=True)
        retval['stdout'] = proc.stdout.read().decode("utf-8")
        retval['stderr'] = proc.stderr.read().decode("utf-8")
        retval['status'] = proc.wait()
    except Exception as E:
        print(args)
        print(E)
    return retval

def _addVirtualInterface(ip, dev, name):
    '''
    add a virtual interface with the specified IP address
    Args:
        ip (str): The ip address to add
        dev (str): The dev to add the virtual interface to

    Returns:
        dict: the label of the new interface
    '''
    name = name[:4].lower()
    # Generate a label for the virtual interface
    label = "{}:{}{}".format(dev, name, random.randint(1, 1000))
    while label in _getInterfaceLabels(dev):
        label = "{}:{}{}".format(dev, name, random.randint(1, 1000))
    netmask = os.environ.get("INTERFACE_NAME", "/20") # TODO: I dont think this matters but it might not haha
    # Add the interface
    command = "ip addr add {}{} brd + dev {} label {}"
    command = command.format(ip, netmask, dev, label)
    res = execute(command)
    if res.get('status', 255) != 0:
        raise ValueError("Cannot add interface: {}\n{}".format(
            res.get('stderr', ''), command))
    return label

def _getInterfaceLabels(dev):
    '''
    return the labels of all virtual interfaces for a dev
    '''
    # The command to list all the labels assigned to an interface
    command = "".join(("ip a show dev {0} | grep -Eo '{0}:[a-zA-Z0-9:]+'",
                       " | cut -d':' -f2-"))
    # command = "ip a show dev {0}"
    command = command.format(dev)
    res = execute(command)
    try:
        labels = res['stdout'].strip().split()
        return labels
    except Exception:
        raise Exception("Cannot get labels: {}".format(res.get('stderr', '')))

def _delVirtualInterface(ip, dev):
    '''
    delete a virtual interface with the specified IP address
    Args:
        ip (str): The ip address of the virtual interface
        dev (str, optional): the dev name
    '''
    res = execute("ip addr del {} dev {}".format(ip, dev))
    if res.get('status', 255) != 0:
        raise Exception("Cannot delete interface: {}".format(
                        res.get('stderr', '')))
    return True

def _delAllInterfaces(device, label=""):
    res = execute("ip a | grep {}:{} | awk '{{print $2}}'".format(device, label)).get('stdout', '')
    ips = res.split("\n")
    for ip in ips:
        if ip:
            print("Deleting", ip)
            _delVirtualInterface(ip, device)


def _getIp(host="1.1.1.1"):
    """Get the ip address that would be used to connect to this host

    Args:
        host (str): the host to connect to, default to an external host
    """
    soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    soc.connect((host,1))
    ip = soc.getsockname()[0]
    soc.close()
    return ip


def _getSubnetMaskFromIp(ip):
    """Get the subnet mask for the given IP

    Args:
        ip (str): the ip address
    Returns:
        str: the subnet mask
    """
    res = execute("ip addr | grep -oE '{}/[^ ]+'".format(ip))  # Get three lines of output
    if res.get('status', 255) != 0:
        raise Exception("Cannot find default interface: {}".format(res.get('stderr', '')))
    mask = res['stdout'].split("/")[-1].strip()
    return "/" + mask


def _getInterfaceNameFromIp(ip):
    """Given an IP address, return the interface name the is associated with it

    Args:
        ip (str): the ip address
    Returns:
        str: the interface name
    """
    res = execute("ip addr | grep '{}' -B2".format(ip))  # Get three lines of output
    if res.get('status', 255) != 0:
        raise Exception("Cannot find default interface: {}".format(res.get('stderr', '')))
    dev = res['stdout'].split()[-1].strip()
    if dev == "dynamic":
        dev = res['stdout'].split("\n")[0].split()[1].strip(":")
    return dev