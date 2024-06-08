from flask import Flask, request, jsonify
from flask_cors import CORS
import xmlrpc.client
import json

app = Flask(__name__)
CORS(app)

server = xmlrpc.client.ServerProxy("http://localhost:8080")
execute = getattr(server, "execute")

@app.route('/api')
def hello_world():
    return 'Hello, World!'

@app.route('/api/service', methods=['POST'])
def handle_request():
    data = request.get_json()
    request_str = json.dumps(data)
    result = execute(request_str)
    response = json.loads(json.loads(result))
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)