import xmlrpc.client
import json

server = xmlrpc.client.ServerProxy("http://localhost:8080")
execute = getattr(server, "execute")
request = {'service': 'get', 'params': 'kunci'}
request_str = json.dumps(request)
print(execute(request_str))