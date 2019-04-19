from pyroute2 import IPDB
from arkclient import ArkClient
import os


def allocateIPs(ips):
    for i in ips:
        ip = IPDB()
        with ip.interfaces.ens160 as eth0:
                eth0.add_ip('%s/24' % i)
        ip.release()


def addServers(struct):
    srv_temp = "worker_processes 5;\nevents {\n    worker_connections 4096;\n}\
            \n\nhttp {\n    server {\n"
    print(struct)
    for ip in struct['vips']['addresses']:
        listen_str = "    listen    " + ip + ":80;\n"
        srv_temp += listen_str
    loc_str = "\n    location / {\n        proxy_pass    " + struct['upstreamip']\
            + "\n    }\n}\n}"
    srv_temp += loc_str
    """
    server_template = "\n\
    server {            \n\
      listen:   %s;     \n\
      location: / {     \n\
          proxy_pass http://%s \n\
          proxy_set_header        Host            $host; \n\
          proxy_set_header        X-Real-IP       $remote_addr; \n\
          proxy_set_header        X-Forwarded-For $proxy_add_x_forwarded_for; \n\
      }                 \n\
    }"                  
    allocateIPs(struct['vips'])
    retval = ""
    for i in struct['vips']:
        print(server_template % (i, struct['upstreamip']))
    """
    print(srv_temp)
    return srv_temp

def main():
    client = ArkClient(os.environ.get("THEARK_SERVER", "http://0.0.0.0:5000"))
    arkuser = os.environ.get("THEARK_USER", "admin")
    arkpass = os.environ.get("THEARK_PASS", "letmein")
    try:
        client.login(arkuser, arkpass)
    except:
        raise Exception("Couldn't log in...")
    #if not client.login(arkuser, arkpass):
    #    raise Exception("Couldn't log in...")
    addrs = client.getAddresses('CrowdControl')
    cc = {}
    cc['Name'] = 'crowdcontrol'
    cc['upstreamip'] = 'cc.c2the.world'
    cc['vips'] = addrs
    
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
    addServers(cc)


if(__name__ == "__main__"):
    main()
