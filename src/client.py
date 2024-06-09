import xmlrpc.client
import json

server = xmlrpc.client.ServerProxy("http://localhost:8070")

# request = {'service': 'get', 'params': 'hali'}
# request = {'service': 'ping', 'params': ''}
# request = {'service': 'set', 'params': {'key': 'hal0', 'value':'iyi'}}
# request = {'service': 'delete', 'params': {'key':'halo'}}
# request = {'service': 'append', 'params': {'key': 'halo', 'value':'iya'}}
# request = {'service': 'strln', 'params': {'key': 'halo'}}
request = {'service': 'request_log'}
# request = {
#             "term":             0,
#             "candidate_addr":   {"ip":"localhost", "port": 8080},
#             "last_log_index":   1,
#             "last_log_term":    2,
#         }
if (request['service'] == 'request_log'):
    execute = getattr(server,"request_log")
else:
    execute = getattr(server, "execute")
request_str = json.dumps(request)
print(execute(request_str))