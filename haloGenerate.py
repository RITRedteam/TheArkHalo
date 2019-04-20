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
        except:
            pass
    return valid_ips

def addServers(data):
    srv_temp = "worker_processes 5;\nevents {\n    worker_connections 4096;\n}\
            \n\nhttp {\n    server {\n"
    valid_ips = allocateIPs(data['addresses'])
    for ip in valid_ips:
        listen_str = "    listen    " + ip + ":80;\n"
        srv_temp += listen_str
    loc_str = "\n    location / {\n        proxy_pass    " + data['upstreamip']\
            + ";\n    }\n}\n}"
    srv_temp += loc_str

    print(srv_temp)
    with open("/etc/nginx/nginx.conf", "w+") as f:
        f.write(srv_temp)
    return srv_temp

def main():
    client = ArkClient(os.environ.get("THEARK_SERVER", "http://0.0.0.0:5000"))
    arkuser = os.environ.get("THEARK_USER", "admin")
    arkpass = os.environ.get("THEARK_PASS", "letmein")
    arktype = os.environ.get("THEARK_TYPE", "")
    arkupst = os.environ.get("THEARK_UPSTREAM", "")
    try:
        client.login(arkuser, arkpass)
    except:
        raise Exception("Couldn't log in...")
    #if not client.login(arkuser, arkpass):
    #    raise Exception("Couldn't log in...")
    addrs = client.getAddresses(arktype)
    addrs['upstreamip'] = arkupst
    addrs['addresses'] = addrs['addresses'][:3]


    #structs = {}
    #structs['cc'] = {}
    #structs['cc']['Name'] = 'crowdcontrol'
    #structs['cc']['upstreamip'] = '192.168.1.1'
    #structs['cc']['vips'] = ['10.0.0.1', '10.0.0.2', '10.0.0.3', '10.0.0.4']
    #structs['arsenal'] = {}
    #structs['arsenal']['Name'] = 'Arsenal'
    #structs['arsenal']['upstreamip'] = '192.168.1.2'
    #structs['arsenal']['vips'] = ['10.0.0.6', '10.0.0.7', '10.0.0.8', '10.0.0.9']

    #Iterate through services
    addServers(addrs)


if(__name__ == "__main__"):
    _delAllInterfaces()
    main()
