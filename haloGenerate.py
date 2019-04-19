from pyroute2 import IPDB

def allocateIPs(ips):
    for i in ips:
        ip = IPDB()
        with ip.interfaces.eth0 as eth0:
                eth0.add_ip('%s/24' % i)
        ip.release()


def addServers(struct):
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

def main():
    
    structs = {}
    structs['cc'] = {}
    structs['cc']['Name'] = 'crowdcontrol'
    structs['cc']['upstreamip'] = '192.168.1.1'
    structs['cc']['vips'] = ['10.0.0.1', '10.0.0.2', '10.0.0.3', '10.0.0.4']
    structs['arsenal'] = {}
    structs['arsenal']['Name'] = 'Arsenal'
    structs['arsenal']['upstreamip'] = '192.168.1.2'
    structs['arsenal']['vips'] = ['10.0.0.6', '10.0.0.7', '10.0.0.8', '10.0.0.9']

    #Iterate through services
    addServers(structs['cc'])


if(__name__ == "__main__"):
    main()