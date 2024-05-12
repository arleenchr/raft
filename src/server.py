# Out-Repository Library
import sys
import os
from xmlrpc.server      import SimpleXMLRPCServer

# In-Repository Library
from lib.struct.address import Address
from lib.raft           import RaftNode
from lib.app            import KVStore


def start_serving(addr: Address, contact_node_addr: Address) -> None:
    print(f"Starting Raft Server at {addr.ip}:{addr.port}")
    server =  SimpleXMLRPCServer((addr.ip, addr.port)) 
    # server.register_introspection_functions()
    server.register_instance(RaftNode(KVStore(), addr, contact_node_addr))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print(f"Kill Raft Server at {addr.ip}:{addr.port}")
        os._exit(42)
        



if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: server.py ip port [contact_ip] [contact_port]")
        exit()

    # Set the server and contact address
    contact_addr = None
    if len(sys.argv) == 5:
        contact_addr = Address(sys.argv[3], int(sys.argv[4]))
    server_addr = Address(sys.argv[1], int(sys.argv[2]))

    # Start server
    start_serving(server_addr, contact_addr)
