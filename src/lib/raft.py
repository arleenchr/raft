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
    ELECTION_TIMEOUT_MIN = 2
    ELECTION_TIMEOUT_MAX = 5
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
        self.commit_index:        int               = -1
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
        # self.__print_log(request)
        node = ServerProxy(f"http://{addr.ip}:{addr.port}")
        json_request = json.dumps(request)
        rpc_function = getattr(node, rpc_name)
        start_time = time.time()
        try:
            response = json.loads(rpc_function(json_request))
            end_time = time.time()
            # self.__print_log(f"RPC call {rpc_name} to {addr} took {end_time - start_time:.2f} seconds")
            return response
        except Exception as e:
            end_time = time.time()
            # self.__print_log(f"RPC call {rpc_name} to {addr} failed after {end_time - start_time:.2f} seconds with error: {e}")
            raise

    ## Leadership

    
    def reset_election_timer(self):
        if self.election_timer:
            self.election_timer.cancel()
        timeout = random.random()*4 + RaftNode.ELECTION_TIMEOUT_MIN
        timeout = min(timeout, RaftNode.ELECTION_TIMEOUT_MAX)
        self.__print_log("reset timeout: " + str(timeout))
        self.election_timer = threading.Timer(timeout,
                                               self.start_election)
        self.election_timer.start()

    def stop_election_timer(self):
        if self.election_timer:
            self.election_timer.cancel()

    def start_election(self):
        self.stop_election_timer()

        leader_request_thread = threading.Thread(target= self.run_async_task, args=[self.__leader_request_vote()])
        leader_request_thread.start()

    # Request vote to be a leader as node become a candidate node. Internode RPC

    async def __leader_request_vote(self):
        self.__print_log("[CANDIDATE] start to request vote")
        self.type = RaftNode.NodeType.CANDIDATE

        # Increment current term
        self.current_term += 1

        # Vote for self
        self.voted_for = self.address

        # Reset election timer
        self.reset_election_timer()

        # Send Request Vote RPCs to all other servers
        self.num_vote = 1
        self.abstain_node = 0
        self.lock = threading.Lock()

        last_log_index = -1 if (len(self.log)==0) else len(self.log)-1
        last_log_term = -1 if (len(self.log)==0) else int(self.log[len(self.log)-1]["term"])

        request = {
            "term":             self.current_term,
            "candidate_addr":   self.address,
            "last_log_index":   last_log_index,
            "last_log_term":    last_log_term,
        }
        list_thread = []

        for follower_addr in self.cluster_addr_list:
            # print(follower_addr, self.address)
            if follower_addr != self.address:
                thread = threading.Thread(target=self.__send_request_vote, kwargs={"follower_addr": follower_addr, "request": request})
                thread.start()
                list_thread.append(thread)
        
        await asyncio.sleep(RaftNode.HEARTBEAT_INTERVAL * 2)
        self.__print_log("num vote: "+ str(self.num_vote))
        self.__print_log("quorum: "+ str((len(self.cluster_addr_list) - self.abstain_node)/2) )
        if (self.num_vote > ((len(self.cluster_addr_list) - self.abstain_node)/2)):
            self.__initialize_as_leader()
        else:
            self.type = RaftNode.NodeType.FOLLOWER

    def __send_request_vote(self, follower_addr, request):
        self.__print_log("Minta suara " + str(follower_addr))
        try:
            response = (self.__send_request(request, "request_vote" , follower_addr))
            print(follower_addr, response)
            if (response["vote_granted"]):
                self.lock.acquire()
                self.num_vote+=1
                self.lock.release()

        except Exception as e:
            
            self.__print_log("Timeout" + str(follower_addr) + " with error:" + str(e))

        
    def request_vote(self, json_request: str):

        self.__print_log("KEPANGGIL VOTE")
        request = json.loads(json_request)
        response = {
            "term": self.current_term,
            "vote_granted": False
        }

        candidate_addr = Address(request["candidate_addr"]["ip"], request["candidate_addr"]["port"])
        if ( int(request["term"]) < self.current_term):
            return json.dumps(response)
        
        voted_for_condition = self.voted_for is None or self.voted_for == candidate_addr
        
        curr_last_log_index = -1 if (len(self.log)==0) else len(self.log)-1
        curr_last_log_term = -1 if (len(self.log)==0) else self.log[len(self.log)-1][0]
        log_condition = ((int(request["last_log_term"]) > curr_last_log_term) or ((
            int(request["last_log_term"]) == curr_last_log_term) and (int(request["last_log_index"]) >= curr_last_log_index)))
            
        if voted_for_condition and log_condition:
            self.reset_election_timer()
            self.voted_for = candidate_addr
            response["vote_granted"] = True
        self.__print_log(f"Grant vote {self.voted_for}")
        return json.dumps(response)

    def run_async_task(self, coro):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(coro)

    # Initialize as leader, if candidate get majority vote from other node
    def __initialize_as_leader(self):
        self.__print_log("Initialize as leader node...")
        self.stop_election_timer()
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
                
        try:
            self.heartbeat_thread = Thread(target=self.run_async_task, args=[self.__leader_heartbeat()])
            self.heartbeat_thread.start()
        except Exception as e:
            self.__print_log(f"Failed to start heartbeat thread: {e}")

    
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
    def __send_heartbeat(self, peer_addr: Address):
        # Construct the heartbeat message
        message = {
            'term': self.current_term,
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
        list_thread = []
        while self.type == RaftNode.NodeType.LEADER:
            self.__print_log("[Leader] Sending heartbeat...")
            for peer_addr in self.cluster_addr_list:
                if (peer_addr != self.address):
                    thread = threading.Thread(target=self.__send_heartbeat, kwargs={'peer_addr' : peer_addr}, name=str(peer_addr.port))
                    thread.start()
                    list_thread.append(thread)
            # send_tasks = [self.__send_heartbeat(peer_addr) for peer_addr in self.cluster_addr_list if peer_addr != self.address]
            # await asyncio.gather(*send_tasks)
            # pass
            await asyncio.sleep(RaftNode.HEARTBEAT_INTERVAL)
            list_thread = []

     # Inter-node RPCs
    def heartbeat(self, json_request: str) -> "json":
        # DONE : Implement heartbeat
        request = json.loads(json_request)
        response = {
            "heartbeat_response": "ack",
            "address": self.address,
        }

        if request["term"] >= self.current_term:
            self.current_term = int(request["term"])
            self.cluster_leader_addr = Address(request["leader_id"]["ip"],request["leader_id"]["port"] )
            self.type = RaftNode.NodeType.FOLLOWER
            self.voted_for = None
            self.reset_election_timer()  # Reset the timer on receiving a heartbeat

        return json.dumps(response)
    
    ## Membership
    def __try_to_apply_membership(self, contact_addr: Address):
        redirected_addr = Address(contact_addr.ip, contact_addr.port)
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

    def execute_app (self, json_request):
        request = json.loads(json_request)
        service = request["service"]
        params = request["params"]

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
        self.__print_log(f"{service}, {params}")
        return json.dumps(result)

    def execute(self, json_request: str) -> "json":
        request = json.loads(json_request)
        result = None

        # DONE : Implement execute
        if (self.type != RaftNode.NodeType.LEADER):
            # error
            result = f"This node is not leader. Please send request to {self.cluster_leader_addr.ip}:{self.cluster_leader_addr.port}"  
        else:
            n_node_committed = 1
            service = request["service"]
            params = request["params"]

            # Log replication
            new_entry = {
                "term": self.current_term,
                "command": {"service": service, "params": params}
            }
            self.log.append(new_entry)
            
            # Log replication: send AppendEntries RPC to all followers
            for follower in self.cluster_addr_list:
                if follower != self.cluster_leader_addr:
                    prev_log_idx = len(self.log) - 2
                    prev_log_term = self.log[prev_log_idx]["term"] if prev_log_idx >= 0 else -1
                    append_request = {
                        "term": self.current_term,
                        "leader_id": self.cluster_leader_addr,
                        "prev_log_idx": prev_log_idx,
                        "prev_log_term": prev_log_term,
                        "entries": [new_entry],
                        "leader_commit": self.commit_index
                    }
                    result = self.send_append_entries(follower, append_request)
                    print(result)

                    if (result["success"]):
                        n_node_committed += 1
            
            if (n_node_committed > (len(self.cluster_addr_list) / 2)):
                # if majority, execute
                result = self.execute_app(json_request)

                # Inform follower to execute
                for follower in self.cluster_addr_list:
                    if follower != self.cluster_leader_addr:
                        self.__send_request(request, "execute_app", follower)

        return json.dumps(result)
    
    def send_append_entries(self, follower, append_request):
        response = self.__send_request(append_request, "append_entries", follower)
        return response

    def append_entries(self, json_request):
        result = json.loads(json_request)
        term = int(result["term"])
        prev_log_idx = int(result["prev_log_idx"])
        prev_log_term = int(result["prev_log_term"])
        entries = result["entries"]
        leader_commit = int(result["leader_commit"])

        # Handle kasus log pertama, prevnya masih ga ada
        if (term < self.current_term):
            is_success = False
        else:
            # Update current term and convert to follower if necessary
            if term > self.current_term:
                self.current_term = term
                self.type = RaftNode.NodeType.FOLLOWER

            # Check if log contains an entry at prev_log_idx with term prev_log_term
            if len(self.log) > 0 and prev_log_idx >= 0 and (len(self.log) <= prev_log_idx or self.log[prev_log_idx]["term"] != prev_log_term):
                print('------------------------------')
                print("prev log idx:", prev_log_idx)
                print("len self log", len(self.log))
                if (len(self.log) > 0):
                    print("self.log[prev_log_idx][\"term\"]", self.log[prev_log_idx]["term"])
                print("prev log term", prev_log_term)
                is_success = False
            else:
                # Check if an existing entry conflicts with a new one (same index but different terms), 
                for entry in entries:
                    if (prev_log_idx>=0) and (self.log[prev_log_idx]["term"] != prev_log_term):
                        # delete the existing entry and all that follow it
                        idx = self.log.index(entry)
                        del self.log[idx:]
                        prev_log_idx = len(self.log) - 2
                        prev_log_term = self.log[prev_log_idx]["term"] if prev_log_idx >= 0 else -1
                        print("Rollback")

                # Append any new entries not already in the log
                self.log = self.log[:prev_log_idx + 1] + entries
                print(self.log)
                is_success = True

                # Update commit index
                if leader_commit > self.commit_index:
                    self.commit_index = min(leader_commit, len(self.log) - 1)

        response = {
            "term": self.current_term,
            "success": is_success
        }

        return json.dumps(response)
        
