#!/usr/bin/env python

# Built-in modules
import sys
import os
import getpass
from topology.TopologyAPI import TopologyAPI

from reg2_wrapper.test_wrapper.client_server_wrapper import ClientServerWrapper

class SockperfWrapper(ClientServerWrapper):

    def get_server_prog_path(self):
        return "../sockperfWrapper.py --daemon " #--daemon --ip 11.4.3.7 --mip 10.224.14.162 --cip 11.4.3.8 "

    def get_client_prog_path(self):
        return "../sockperfWrapper.py " #--ip 11.4.3.7 --mip 10.224.14.162 --cip 11.4.3.8 "

    def configure_parser(self):
        super(SockperfWrapper, self).configure_parser()

        # Arguments
        #self.add_dynamic_client_argument('--mip', self.??, value_only=False, priority=1)
        
        #self.add_dynamic_client_argument('--cip', self.??, value_only=False, priority=3)
        self.add_server_cmd_argument('--daemon',help='Run sockperf wrapper as a daemon', type=str, value_only=False, priority=1)
        self.add_dynamic_server_argument('--ip', self.get_server_tested_ip, value_only=False, priority=2)
        self.add_dynamic_client_argument('--ip', self.get_server_tested_ip, value_only=False, priority=2)
        self.add_dynamic_server_argument('--mip', self.get_server_manage_ip, value_only=False, priority=3)
        self.add_dynamic_client_argument('--mip', self.get_server_manage_ip, value_only=False, priority=3)
        self.add_dynamic_server_argument('--cip', self.get_client_tested_ip, value_only=False, priority=4)
        self.add_dynamic_client_argument('--cip', self.get_client_tested_ip, value_only=False, priority=4)
        #self.add_server_cmd_argument('--daemon',help='Run sockperf wrapper as a daemon', type=str, value_only=False, priority=1)
        #self.add_dynamic_cmd_argument('--ip', self.get_server_tested_ip, value_only=False, priority=2)
        #self.add_dynamic_cmd_argument('--mip', self.get_server_manage_ip, value_only=False, priority=3)
        #self.add_dynamic_cmd_argument('--cip', self.get_client_tested_ip, value_only=False, priority=4)

        self.add_cmd_argument('--activity', help='Measure activity by printing a \'.\' for the last <N> messages processed.', type=int, value_only=False, priority=12)
        self.add_cmd_argument('--Activity', help='Measure activity by printing the duration for last <N> messages processed.', type=int, value_only=False, priority=14)
        self.add_cmd_argument('--mc-loopback-enable', help='Enables mc loopback (default: Disabled)', type=str, value_only=False, priority=21)
        self.add_cmd_argument('--vmazcopyread', help='If possible use VMA\'s zero copy reads API (See VMA\'s readme)', type=str, value_only=False, priority=24)
        self.add_cmd_argument('--nonblocked', help='Open non-blocked sockets.', type=str, value_only=False, priority=33)
        self.add_cmd_argument('--dontwarmup', help='Don\'t send warm up messages on start', type=str, value_only=False, priority=40)
        self.add_cmd_argument('--buffer-size', help='Set total socket receive/send buffer <size> in bytes (system defined by default)', type=long, value_only=False, priority=35)
        self.add_cmd_argument('--msg-size', help='Use messages of size <size> bytes (Minimum Default:12)', type=str, value_only=False, priority=34)
        self.add_cmd_argument('--mps', help='Set number of messages-per-second (Default = 10000 - for under-load mode, or max - for ping-pong and throughput modes', type=str, value_only=False, priority=39)
        self.add_cmd_argument('--burst', help='Control the client\'s number of a messages sent in every burst', type=long, value_only=False, priority=41)
        self.add_cmd_argument('--time', help='Run for <sec> seconds (Default 1, max = 36000000)', type=long, value_only=False, priority=11)
        self.add_cmd_argument('--tcp', help='Use TCP protocol (Default: UDP)', type=str, value_only=False, priority=37)
        self.add_cmd_argument('--iomux-type', help='Type of multiple file descriptors handle [s|select|p|poll|e|epoll|r|recvfrom](default select)', type=str, value_only=False, priority=13)
        self.add_cmd_argument('--file', help='Read multiple ip+port combinations from file <file> (server uses select)', type=str, value_only=False, priority=36)
        self.add_cmd_argument('--timeout', help='Set select/poll/epoll timeout to <msec>, -1 for infinite (Default is 10 msec)', type=int, value_only=False, priority=15)
        self.add_cmd_argument('--mc-rx-if', help='Address of interface on which to receive mulitcast messages (can be other than route table)', type=str, value_only=False, priority=16)
        self.add_cmd_argument('--mc-tx-if', help='Address of interface on which to transmit mulitcast messages (can be other than route table)', type=str, value_only=False, priority=17)
        self.add_cmd_argument('--mc-ttl', help='Limit the lifetime of the message (Default: 2)', type=int, value_only=False, priority=18)
        self.add_cmd_argument('--pre-warmup-wait', help='Time to wait before sending warm up messages (seconds)', type=int, value_only=False, priority=19)
        self.add_cmd_argument('--no-rdtsc', help='Don\'t use register when taking time; instead use monotonic clock.', type=str, value_only=False, priority=20)
        self.add_cmd_argument('--ping-pong', help='Run sockperf client for latency test in ping pong mode.', type=str, value_only=False, priority=5)
        self.add_cmd_argument('--playback', help='Run sockperf client for latency test using playback of predefined traffic, based on timeline and message size.', type=str, value_only=False, priority=6)
        self.add_cmd_argument('--under-load', help='Run sockperf client for latency under load test.', type=str, value_only=False, priority=7)
        self.add_cmd_argument('--throughput', help='Run sockperf client for one way throughput test.', type=str, value_only=False, priority=8)
        self.add_cmd_argument('--server', help='Run sockperf as a server.', type=str, value_only=False, priority=9)
        self.add_cmd_argument('--servers', help='The number of servers to be started', type=int, value_only=False, priority=22)
        self.add_cmd_argument('--mode', help='The mode to run sockperf with', type=int, value_only=False, priority=23)
        self.add_cmd_argument('--multicast', help='Generate multicast traffic', type=str, value_only=False, priority=38)
        self.add_cmd_argument('--sockets', help='The number of sockets in the sockperf feed file', type=str, value_only=False, priority=10)
        self.add_cmd_argument('--multi-port', help='Generate traffic across multiple ports', type=str, value_only=False, priority=25)
        self.add_cmd_argument('--mixed-file', help='Generate a mixed feed file', type=str, value_only=False, priority=26)
        self.add_cmd_argument('--VMA_APPLICATION_ID', help='VMA application ID', type=str, value_only=False, priority=27)
        self.add_cmd_argument('--VMA_CONFIG_FILE', help='VMA configuration file', type=str, value_only=False, priority=28)
        self.add_cmd_argument('--VMA_STATS_FILE', help='The output file for the VMA state', type=str, value_only=False, priority=29)
        self.add_cmd_argument('--clients', help='The number of clients', type=int, value_only=False, priority=30)
        self.add_cmd_argument('--management', help='Use management interface', type=str, value_only=False, priority=31)
        self.add_cmd_argument('--max-memory', help='Use maximum memory availble on the machine', type=str, value_only=False, priority=32)


    def get_server_manage_ip(self):
        return self.ServerPlayer.Ip

    def get_server_tested_ip(self):
        # Define needed parameters
        here = os.path.dirname(os.path.abspath(__file__))
        print("Running directory is " + here + "!")
        print("Running user is " + getpass.getuser() + "!")

        server_ip = self.ServerPlayer.Ip
        ip = ""

        self.topology_api = TopologyAPI(self.topo_file)
        hosts = self.topology_api.get_all_hosts()
        for host in hosts:
            base_ip = self.topology_api.get_object_attribute(host, "BASE_IP")
            if base_ip == server_ip:
                ports = self.topology_api.get_device_active_ports(host)
                ip = self.topology_api.get_port_ip(ports[0])

        return ip

 
    def get_client_tested_ip(self):
        # Define needed parameters
        here = os.path.dirname(os.path.abspath(__file__))
        print("Running directory is " + here + "!")
        print("Running user is " + getpass.getuser() + "!")

        client_ip = self.ClientPlayers[0].Ip
        ip = ""

        self.topology_api = TopologyAPI(self.topo_file)
        hosts = self.topology_api.get_all_hosts()
        for host in hosts:
            base_ip = self.topology_api.get_object_attribute(host, "BASE_IP")
            if base_ip == client_ip:
                ports = self.topology_api.get_device_active_ports(host)
                ip = self.topology_api.get_port_ip(ports[0])

        return ip


if __name__ == "__main__":
    wrapper = SockperfWrapper("JX Wrapper", kill_server=True)
    #wrapper = DpdkWrapper("JX Wrapper")
    wrapper.execute(sys.argv[1:])
