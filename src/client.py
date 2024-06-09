import xmlrpc.client
import json

server = xmlrpc.client.ServerProxy("http://localhost:8090")

# request = {'service': 'ping', 'params': ''}
request = {'service': 'set', 'params': {'key': '1', 'value':'A'}}
# request = {'service': 'append', 'params': {'key': '1', 'value':'BC'}}
# request = {'service': 'set', 'params': {'key': '2', 'value':'SI'}}
# request = {'service': 'append', 'params': {'key': '2', 'value':'S'}}
# request = {'service': 'get', 'params': '2'}

# request = {'service': 'strln', 'params': {'key': '1'}}
# request = {'service': 'strln', 'params': {'key': '2'}}
# request = {'service': 'delete', 'params': {'key':'1'}}
# request = {'service': 'append', 'params': {'key': '2', 'value':'TE'}}
# request = {'service': 'append', 'params': {'key': '2', 'value':'R'}}

# request = {'service': 'set', 'params': {'key': '3', 'value':''}}
# request = {'service': 'append', 'params': {'key': '3', 'value':'UwU'}}
# request = {'service': 'append', 'params': {'key': '4', 'value':'Onii-Chan'}}
# request = {'service': 'append', 'params': {'key': '4', 'value':'Daisuki'}}

# request = {'service': 'set', 'params': {'key': 'halo', 'value':'SI'}}
# request = {'service': 'get', 'params': '2'}
# request = {'service': 'get', 'params': '3'}
# request = {'service': 'get', 'params': '4'}

# request = {'service': 'request_log'}
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