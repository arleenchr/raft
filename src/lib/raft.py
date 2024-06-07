# Out-Repository Library
import asyncio
import socket
import time
import json
import threading
import random
from threading     import Thread
from xmlrpc.client import ServerProxy
from typing        import Any, List
from enum          import Enum

# In-Reposiroty Library
from lib.struct.address       import Address



class RaftNode:
    HEARTBEAT_INTERVAL   = 1
    ELECTION_TIMEOUT_MIN = 3
    ELECTION_TIMEOUT_MAX = 4
    RPC_TIMEOUT          = 0.5

    class NodeType(Enum):
        LEADER    = 1
        CANDIDATE = 2
        FOLLOWER  = 3

    def __init__(self, application : Any, addr: Address, contact_addr: Address = None):
        socket.setdefaulttimeout(RaftNode.RPC_TIMEOUT)
        self.address:             Address           = addr
        self.type:                RaftNode.NodeType = RaftNode.NodeType.FOLLOWER
        self.log:                 List[int, str]    = []
        self.app:                 Any               = application
        self.current_term:        int               = 0
        self.voted_for:           Address           = None
        self.cluster_addr_list:   List[Address]     = []
        self.cluster_leader_addr: Address           = None
        self.election_timer                         = None
        if contact_addr is None:
            self.cluster_addr_list.append(self.address)
            self.__initialize_as_leader()
            # self.__start_election_process()
        else:
            self.__try_to_apply_membership(contact_addr)
            self.reset_election_timer()

    ## IO
    def __print_log(self, text: str):
        print(f"[{self.address}] [{time.strftime('%H:%M:%S')}] {text}")

    def __send_request(self, request: Any, rpc_name: str, addr: Address) -> "json":
        # Warning : This method is blocking
        node         = ServerProxy(f"http://{addr.ip}:{addr.port}")
        json_request = json.dumps(request)
        rpc_function = getattr(node, rpc_name)
        response     = json.loads(rpc_function(json_request))
        return response

    ## Leadership

    
    def reset_election_timer(self):
        if self.election_timer:
            self.election_timer.cancel()
        timeout = random.random() + RaftNode.ELECTION_TIMEOUT_MIN
        self.__print_log("reset timeout: " + str(timeout))
        self.election_timer = threading.Timer(timeout,
                                               self.start_election)
        self.election_timer.start()

    def stop_election_timer(self):
        if self.election_timer:
            self.election_timer.cancel()

    def __start_election_process(self):
        self.__print_log("Starting election process...")
        self.start_election()

    def start_election(self):
        self.stop_election_timer()

        leader_request_thread = threading.Thread(target=self.__leader_request_vote, name="t1")
        leader_request_thread.start()
        leader_request_thread.join()

    # Request vote to be a leader as node become a candidate node. Internode RPC

    def __leader_request_vote(self):
        self.__print_log("[CANDIDATE] start to request vote")
        self.type = RaftNode.NodeType.CANDIDATE

        # Increment current term
        self.current_term += 1

        # Vote for self
        self.voted_for = self.address

        # Reset election timer
        self.reset_election_timer()

        # Send Request Vote RPCs to all other servers
        num_vote = 1
        abstain_node = 0

        last_log_index = -1 if (len(self.log)==0) else len(self.log)-1
        last_log_term = -1 if (len(self.log)==0) else self.log[len(self.log)-1][0]

        request = {
            "term":             self.current_term,
            "candidate_addr":   self.address,
            "last_log_index":   last_log_index,
            "last_log_term":    last_log_term,
        }

        for follower_addr in self.cluster_addr_list:
            print(follower_addr, self.address)
            if follower_addr != self.address:
                print("Minta suara ", follower_addr)
                try:
                    response = json.loads(self.__send_request(request, "request_vote" , follower_addr))
                    if (response["vote_granted"]):
                        num_vote+=1
                except:
                    print("TImeout", follower_addr)
                    abstain_node += 1
                    pass
        
        if (num_vote > ((len(self.cluster_addr_list) - abstain_node)/2)):
            print("num vote: ", num_vote)
            print("quorum: ", ((len(self.cluster_addr_list) - abstain_node)/2) )
            self.__initialize_as_leader()
        else:
            self.type = RaftNode.NodeType.FOLLOWER

        
    def request_vote(self, json_request: str):

        print("KEPANGGIL VOTE")
        request = json.loads(json_request)
        response = {
            "term": self.current_term,
            "vote_granted": False
        }

        if ( int(request["term"]) < self.current_term):
            return json.dumps(response)
        
        voted_for_condition = self.voted_for is None or self.voted_for == request["candidate_addr"]
        
        curr_last_log_index = -1 if (len(self.log)==0) else len(self.log)-1
        curr_last_log_term = -1 if (len(self.log)==0) else self.log[len(self.log)-1][0]
        log_condition = ((int(request["last_log_term"]) > curr_last_log_term) or ((
            int(request["last_log_term"]) == curr_last_log_term) and (int(request["last_log_index"]) >= curr_last_log_index)))
            
        if voted_for_condition and log_condition:
            self.voted_for = request["candidate_addr"]
            response["vote_granted"] = True
        self.__print_log(f"Grant vote {self.voted_for}")
        return json.dumps(response)

    # Initialize as leader, if candidate get majority vote from other node
    def __initialize_as_leader(self):
        self.__print_log("Initialize as leader node...")
        self.cluster_leader_addr = self.address
        self.type                = RaftNode.NodeType.LEADER
        request = {
            "term": self.current_term,
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

    
    def inform_new_member(self, json_request):
        request = json.loads(json_request)
        
        temp_cluster_addr_list = []
        for address in request["cluster_addr_list"]:
            temp_cluster_addr_list.append(Address(address["ip"], address["port"]))
            
        self.cluster_addr_list = temp_cluster_addr_list

        print("New member informed")
        return json.dumps(request)

    
    def inform_new_leader(self, json_request):
        request = json.loads(json_request)
        self.current_term = request["term"]
        self.cluster_leader_addr = request["cluster_leader_addr"]
        self.type = RaftNode.NodeType.FOLLOWER
        self.voted_for = None
        self.reset_election_timer()
        self.__print_log(f"New leader informed: {self.cluster_leader_addr}")
        response = {
            "status": "success",
            "address": self.address
        }
        return json.dumps(response)


    ## Heartbeat
    async def __send_heartbeat(self, peer_addr: Address):
        prev_log_index = self.next_index[peer_addr] - 1
        prev_log_term = self.log[prev_log_index][0] if prev_log_index >= 0 else -1

        entries = self.log[self.next_index[peer_addr]:]

        message = {
            'term': self.current_term,
            'leader_id': self.address,
            'prev_log_index': prev_log_index,
            'prev_log_term': prev_log_term,
            'entries': entries,
            'leader_commit': len(self.log)
        }
        self.__print_log(f"[Leader] Sending heartbeat to {peer_addr} with entries: {entries}")
        try:
            response = self.__send_request(message, "append_entries", peer_addr)
            if response.get("success"):
                self.next_index[peer_addr] = len(self.log)
                self.match_index[peer_addr] = len(self.log) - 1
                self.__print_log(f"[Leader] AppendEntries successful for {peer_addr}")
            else:
                self.next_index[peer_addr] -= 1
                self.__print_log(f"[Leader] AppendEntries failed for {peer_addr}, decreasing next_index")
        except Exception as e:
            self.__print_log(f"[Leader] Failed to send heartbeat to {peer_addr}: {e}")


    async def __leader_heartbeat(self):
        while self.type == RaftNode.NodeType.LEADER:
            self.__print_log("[Leader] Sending heartbeat...")
            send_tasks = [self.__send_heartbeat(peer_addr) for peer_addr in self.cluster_addr_list if peer_addr != self.address]
            await asyncio.gather(*send_tasks)
            await asyncio.sleep(RaftNode.HEARTBEAT_INTERVAL)

            
    # Append log to the leader node
    def append_entries(self, json_request: str) -> "json":
        request = json.loads(json_request)
        response = {
            "term": self.current_term,
            "success": False
        }

        if request["term"] < self.current_term:
            return json.dumps(response)

        self.current_term = request["term"]
        self.cluster_leader_addr = request["leader_id"]
        self.type = RaftNode.NodeType.FOLLOWER
        self.reset_election_timer()

        prev_log_index = request["prev_log_index"]
        prev_log_term = request["prev_log_term"]

        if prev_log_index >= 0 and (len(self.log) <= prev_log_index or self.log[prev_log_index][0] != prev_log_term):
            return json.dumps(response)

        for i, entry in enumerate(request["entries"]):
            if len(self.log) > prev_log_index + 1 + i:
                self.log[prev_log_index + 1 + i] = entry
            else:
                self.log.append(entry)

        response["success"] = True
        return json.dumps(response)

     # Inter-node RPCs
    def heartbeat(self, json_request: str) -> "json":
        # TODO : Implement heartbeat
        request = json.loads(json_request)
        response = {
            "heartbeat_response": "ack",
            "address": self.address,
        }

        if request["term"] >= self.current_term:
            self.current_term = request["term"]
            self.cluster_leader_addr = request["leader_id"]
            self.type = RaftNode.NodeType.FOLLOWER
            self.voted_for = None
            self.reset_election_timer()  # Reset the timer on receiving a heartbeat

        return json.dumps(response)
    
    
    
    
    ## Membership
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
        
        temp_cluster_addr_list = []
        for address in response["cluster_addr_list"]:
            temp_cluster_addr_list.append(Address(address["ip"], address["port"]))
    
        self.cluster_addr_list = temp_cluster_addr_list
        self.cluster_leader_addr = redirected_addr

    def __send_new_member_information(self, address: Address):
        request = {
            "cluster_addr_list": self.cluster_addr_list
        }
        for addr in self.cluster_addr_list:
            if (addr != self.address and addr != address):
                self.__send_request(request, "inform_new_member", addr)
                self.__print_log(f"Inform new member to {addr}")

    # Internode RPC 
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
            address = Address(address["ip"], address["port"])
            self.cluster_addr_list.append(address)
            self.__print_log(f"Adding {address} to cluster...")
            response["status"] = "success"
            response["log"] = self.log
            response["cluster_addr_list"] = self.cluster_addr_list
            # Redirected 
            print("sini")
            
            new_member_broadcaster_thread = threading.Thread(target=self.__send_new_member_information, kwargs={'address' : address}, name="t2")
            new_member_broadcaster_thread.start()
        return json.dumps(response)

    # Client RPCs
    def execute(self, json_request: str) -> "json":
        request = json.loads(json_request)
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
            result = self.app.append(key, value)
        else:
            result = "Invalid service"

        self.log.append((self.current_term, json_request))
        if self.type == RaftNode.NodeType.LEADER:
            self.__replicate_log_entries()

        return json.dumps(result)

def __replicate_log_entries(self):
    asyncio.run(self.__leader_heartbeat())
