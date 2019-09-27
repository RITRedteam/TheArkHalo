from arkclient import ArkClient
import os
from netassign import _addVirtualInterface, _delAllInterfaces

DEVICE='ens160'

def allocateIPs(ips):
    valid_ips = []
    print("IPS: " + str(ips))
    for i in ips:
        try:
            print("Adding virtual IP", i)
            _addVirtualInterface(i, DEVICE)
            valid_ips.append(i)
        except Exception as E:
            print("Cannot add virtual IP", i, type(E), E)
            pass
    return valid_ips

def addServers(data):
    srv_temp = "worker_processes 5;\nevents {\n    worker_connections 4096;\n}\
            \n\nhttp {\n    server {\n"
    valid_ips = allocateIPs(data['addresses'])
    print(valid_ips)
    for ip in valid_ips:
        listen_str = "    listen    " + ip + ":80;\n"
        srv_temp += listen_str
    loc_str = "\n    location / {\n        proxy_pass    " + data['upstreamip'] + ";\n"
    if os.environ.get("PROXY_HOST", ""):
        loc_str += "        proxy_set_header Host {};\n".format(os.environ.get("PROXY_HOST"))
    loc_str += "    }\n}\n}"
    srv_temp += loc_str

    print(srv_temp)
    with open("/etc/nginx/nginx.conf", "w+") as f:
        f.write(srv_temp)
    return srv_temp

def main():
    client = ArkClient(os.environ.get("THEARK_SERVER", "http://0.0.0.0:5000"))
    arkuser = os.environ.get("THEARK_USER", "admin")
    arkpass = os.environ.get("THEARK_PASS", "letmein")
    arktype = os.environ.get("HALO_NAME", "")
    arkupst = os.environ.get("HALO_UPSTREAM", "")
    register = os.environ.get('THEARK_REGISTER', "False")
    count = os.environ.get('HALO_ADDR_COUNT', "15")
    try:
        count = int(count)
    except ValueError:
        count = 15

    try:
        client.login(arkuser, arkpass)
    except:
        raise Exception("Couldn't log in...")
    

    # Register the new halo if it doesnt exist already
    register = register.lower().strip() in ["true", "yes", "1", "t"]
    if register and arktype.lower() not in [x.lower() for x in client.getHalos()]:
        print("Registering {} with The Ark".format(arktype))
        print("Collecting {} addresses for {}".format(count, arktype))
        addrs = client.registerHalo(arktype, count)
    else:
        print("Halo is not registered, getting IPs")
        addrs = client.getAddresses(arktype)
        print(addrs)
    addrs['upstreamip'] = arkupst
    addServers(addrs)

    print("In order to view the IP addresses assigned to {}, navigate to {}".format(arktype, os.environ.get("THEARK_SERVER", "http://0.0.0.0:5000")))


if(__name__ == "__main__"):
    _delAllInterfaces()
    main()
