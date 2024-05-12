import xmlrpc.client

server = xmlrpc.client.ServerProxy("http://localhost:8080")
execute = getattr(server, "execute")
request = {'service': 'get', 'params':'kunci'}
print(execute(request))
