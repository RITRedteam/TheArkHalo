# TheArkHalo

A Halo works with the [Ark](https://github.com/RITRedteam/TheArk) to listen on many different virtual IP addresses and upstream them to a single C2.

It is deigned to be fairly easy to deploy a single Halo or many. See [docker-compose.yml](docker-compose.yml) for basic deployment.

# TODO
- Make a real readme

> The features below will all be implemented with the new config file


- Make it work with a list of IPs and not just the Ark
- TCP forwarding
- Allow custom http headers