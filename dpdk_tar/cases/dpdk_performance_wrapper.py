#!/usr/bin/env python

# Built-in modules
import sys
import os
import getpass
from topology.TopologyAPI import TopologyAPI

from reg2_wrapper.test_wrapper.client_server_wrapper import ClientServerWrapper

class DpdkWrapper(ClientServerWrapper):

    def get_server_prog_path(self):
        return "../dpdk_performance.py --server --mip 10.224.14.113 --ip 22.4.3.5 --cip 22.4.3.6"

    def get_client_prog_path(self):
        return "../dpdk_performance.py --ip 22.4.3.5  --mip 10.224.14.113 --cip 22.4.3.6"

    def configure_parser(self):
        super(DpdkWrapper, self).configure_parser()
 
        # Arguments
	#self.add_dynamic_client_argument('--mip', self.??, value_only=False, priority=1)
        #self.add_dynamic_client_argument('--ip', self.get_server_manage_ip, value_only=False, priority=2)
        #self.add_dynamic_client_argument('--cip', self.??, value_only=False, priority=3)
        
        self.add_cmd_argument('--invalidMac', help='Pass Invalid Mac', type=str, value_only=False, priority=1)
        self.add_cmd_argument('--setPromisc', help='Set Promiscous Mode', type=str, value_only=False, priority=2)
        self.add_cmd_argument('--add_mac', help='Add Mac Address', type=str, value_only=False, priority=3)
        self.add_cmd_argument('--dest_ip', help='Destination IP', type=str, value_only=False, priority=4)
        self.add_cmd_argument('--txq', help='Transmission Queue', type=str, value_only=False, priority=5)
        self.add_cmd_argument('--rxq', help='Receive Queue', type=str, value_only=False, priority=6)
        self.add_cmd_argument('--portUpInInit', help='The port link is brought up during init', type=str, value_only=False, priority=7)
        self.add_cmd_argument('--mtuSet', help='Set the mtu for the giving amount for mellanox interface', type=str, value_only=False, priority=8)
        self.add_cmd_argument('--vlanFiltering', help='Set vlan filter on or off', type=str, value_only=False, priority=9)
        self.add_cmd_argument('--mtuSetMultipleTimes', help='Set MTU multiple times at run time', type=str, value_only=False, priority=10)
        self.add_cmd_argument('--autonegotiateEthtool', help='Set autonegotiate value through Ethtool', type=str, value_only=False, priority=11)
        self.add_cmd_argument('--rxEthtool', help='Set RX value through Ethtool', type=str, value_only=False, priority=12)
        self.add_cmd_argument('--txEthtool', help='Set TX value through Ethtool', type=str, value_only=False, priority=13)
        self.add_cmd_argument('--disable_rss', help='disable_rss', type=str, value_only=False, priority=14)
        self.add_cmd_argument('--rssQueuesFlage', help='rssQueuesFlage', type=str, value_only=False, priority=15)
        self.add_cmd_argument('--device', help='device to run on', type=str, value_only=False, priority=16)
        self.add_cmd_argument('--dnfs', help='Enable DNFS', type=str, value_only=False, priority=17)
        self.add_cmd_argument('--RSS', help='Enable RSS', type=str, value_only=False, priority=18)
        self.add_cmd_argument('--Bidirectional', help='Enable Bidirectional', type=str, value_only=False, priority=19)
        self.add_cmd_argument('--recv-inline', help='Enable Receive Inline', type=str, value_only=False, priority=20)
        self.add_cmd_argument('--msg-size', help='message Size', type=str, value_only=False, priority=21)
        self.add_cmd_argument('--checksum', help='Check bad checksum IP, UDP or TCP', type=str, value_only=False, priority=22)
        self.add_cmd_argument('--first_case', help='First Performance case', type=str, value_only=False, priority=23)
        self.add_cmd_argument('--last_case', help='Last Performance case', type=str, value_only=False, priority=24)
        self.add_cmd_argument('--master_rc', help='Create New Vlan and Virtual Interface to Test PMD', type=str, value_only=False, priority=25)

    def get_server_manage_ip(self):
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
                              
if __name__ == "__main__":
    wrapper = DpdkWrapper("JX Wrapper", kill_server=False)
    #wrapper = DpdkWrapper("JX Wrapper")
    wrapper.execute(sys.argv[1:])

