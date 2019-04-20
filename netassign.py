from subprocess import Popen, PIPE
import random
import __main__ 

LABEL="tmp"
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

def _addVirtualInterface(ip, dev):
    '''
    add a virtual interface with the specified IP address
    Args:
        ip (str): The ip address to add
        dev (str): The dev to add the virtual interface to
    
    Returns:
        dict: the label of the new interface
    '''
    # Generate a label for the virtual interface
    label = "{}:{}{}".format(dev, LABEL, random.randint(1, 1000))
    while label in _getInterfaceLabels(dev):
        label = "{}:{}{}".format(dev, LABEL, random.randint(1, 1000))
    netmask = "/16"
    # Add the interface
    command = "ip addr add {}{} brd + dev {} label {}"
    command = command.format(ip, netmask, dev, label)
    res = execute(command)
    if res.get('status', 255) != 0:
        raise Exception("Cannot add interface: {}\n{}".format(
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

def _delAllInterfaces():
    res = execute("ip a | grep {}:{} | awk '{{print $2}}'".format(__main__.DEVICE, LABEL)).get('stdout', '')
    ips = res.split("\n")
    for ip in ips:
        if ip:
            print("Deleting", ip)
            _delVirtualInterface(ip, __main__.DEVICE)
