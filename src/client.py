import xmlrpc.client
import json

server = xmlrpc.client.ServerProxy("http://localhost:8080")
execute = getattr(server, "execute")
request = {'service': 'get', 'params': 'halo'}
# request = {'service': 'ping'}
# request = {'service': 'set', 'params': {'key': 'halo', 'value':'iya'}}
# request = {'service': 'delete', 'params': {'key':'halo'}}
# request = {'service': 'append', 'params': {'key': 'halo', 'value':'iya'}}
# request = {'service': 'strln', 'params': {'key': 'halo'}}
# request = {
#             "term":             0,
#             "candidate_addr":   {"ip":"localhost", "port": 8080},
#             "last_log_index":   1,
#             "last_log_term":    2,
#         }
request_str = json.dumps(request)
print(execute(request_str))