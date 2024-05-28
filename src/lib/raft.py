# Out-Repository Library
import asyncio
import socket
import time
import json
from threading     import Thread
from xmlrpc.client import ServerProxy
from typing        import Any, List
from enum          import Enum

# In-Reposiroty Library
from lib.struct.address       import Address



class RaftNode:
    HEARTBEAT_INTERVAL   = 1
    ELECTION_TIMEOUT_MIN = 2
    ELECTION_TIMEOUT_MAX = 3
    RPC_TIMEOUT          = 0.5

    class NodeType(Enum):
        LEADER    = 1
        CANDIDATE = 2
        FOLLOWER  = 3

    def __init__(self, application : Any, addr: Address, contact_addr: Address = None):
        socket.setdefaulttimeout(RaftNode.RPC_TIMEOUT)
        self.address:             Address           = addr
        self.type:                RaftNode.NodeType = RaftNode.NodeType.FOLLOWER
        self.log:                 List[str, str]    = []
        self.app:                 Any               = application
        self.election_term:       int               = 0
        self.cluster_addr_list:   List[Address]     = []
        self.cluster_leader_addr: Address           = None
        if contact_addr is None:
            self.cluster_addr_list.append(self.address)
            self.__initialize_as_leader()
        else:
            self.__try_to_apply_membership(contact_addr)

    # Internal Raft Node methods
    def __print_log(self, text: str):
        print(f"[{self.address}] [{time.strftime('%H:%M:%S')}] {text}")

    def __initialize_as_leader(self):
        self.__print_log("Initialize as leader node...")
        self.cluster_leader_addr = self.address
        self.type                = RaftNode.NodeType.LEADER
        request = {
            "cluster_leader_addr": self.address
        }
        # TODO : Inform to all node this is new leader
        for peer_addr in self.cluster_addr_list:
            if peer_addr != self.address:
                try:
                    self.__send_request(request, "inform_new_leader", peer_addr)
                except Exception as e:
                    self.__print_log(f"Failed to inform {peer_addr} about new leader: {e}")
        
        self.heartbeat_thread = Thread(target=asyncio.run,args=[self.__leader_heartbeat()])
        self.heartbeat_thread.start()

    async def __send_heartbeat(self, peer_addr: Address):
        # Construct the heartbeat message
        message = {
            'term': self.election_term,
            'leader_id': self.address,
            'commit_index': len(self.log)  # assuming commit_index is the length of the log
        }
        self.__print_log(f"[Leader] Sending heartbeat to {peer_addr}")
        try:
            response = self.__send_request(message, "heartbeat", peer_addr)
            if response.get("heartbeat_response") == "ack":
                self.__print_log(f"[Leader] Heartbeat acknowledged by {peer_addr}")
        except Exception as e:
            self.__print_log(f"[Leader] Failed to send heartbeat to {peer_addr}: {e}")

    async def __leader_heartbeat(self):
        # DONE : Send periodic heartbeat
        while self.type == RaftNode.NodeType.LEADER:
            self.__print_log("[Leader] Sending heartbeat...")
            send_tasks = [self.__send_heartbeat(peer_addr) for peer_addr in self.cluster_addr_list if peer_addr != self.address]
            await asyncio.gather(*send_tasks)
            # pass
            await asyncio.sleep(RaftNode.HEARTBEAT_INTERVAL)
    
    def apply_membership(self, address : Address):
        response = {
            "status": "redirected",
            "address": {
                "ip":   self.address.ip,
                "port": self.address.port,
            }
        }
        # Proses apply membership jika node yang diminta adalah leader node
        if (self.type == RaftNode.NodeType.LEADER):
            address = json.loads(address)
            self.cluster_addr_list.append(Address(address["ip"], address["port"]))
            self.__print_log(f"Adding {address} to cluster...")
            response["status"] = "success"
            response["log"] = self.log
            response["cluster_addr_list"] = self.cluster_addr_list
            return json.dumps(response)
        # Redirected 
        return json.dumps(response)

    def __try_to_apply_membership(self, contact_addr: Address):
        redirected_addr = contact_addr
        response = {
            "status": "redirected",
            "address": {
                "ip":   contact_addr.ip,
                "port": contact_addr.port,
            }
        }
        while response["status"] != "success":
            redirected_addr = Address(response["address"]["ip"], response["address"]["port"])
            response        = self.__send_request(self.address, "apply_membership", redirected_addr)
        self.log                 = response["log"]
        self.cluster_addr_list   = response["cluster_addr_list"]
        self.cluster_leader_addr = redirected_addr

    def __send_request(self, request: Any, rpc_name: str, addr: Address) -> "json":
        # Warning : This method is blocking
        node         = ServerProxy(f"http://{addr.ip}:{addr.port}")
        json_request = json.dumps(request)
        rpc_function = getattr(node, rpc_name)
        response     = json.loads(rpc_function(json_request))
        return response

    # Inter-node RPCs
    def heartbeat(self, json_request: str) -> "json":
        # TODO : Implement heartbeat
        response = {
            "heartbeat_response": "ack",
            "address":            self.address,
        }
        return json.dumps(response)


    # Client RPCs
    def execute(self, json_request: str) -> "json":
        request = json.loads(json_request)

        # TODO : Implement execute
        service = request.get("service")
        params = request.get("params")

        if service == "ping":
            result = self.app.ping()
        elif service == "get":
            result = self.app.get(params)
        elif service == "set":
            key = params.get("key")
            value = params.get("value")
            result = self.app.set(key, value)
        elif service == "strln":
            key = params.get("key")
            result = self.app.strln(key)
        elif service == "delete":
            key = params.get("key")
            result = self.app.delete(key)
        elif service == "append":
            key = params.get("key")
            value = params.get("value")
            result = self.app.append(key,value)
        else:
            result = "Invalid service"

        return json.dumps(result)