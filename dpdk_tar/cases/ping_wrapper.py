#!/usr/bin/env python

# Built-in modules
import sys
import os
import getpass
from topology.TopologyAPI import TopologyAPI

from reg2_wrapper.test_wrapper.client_server_wrapper import ClientServerWrapper

class DpdkWrapper(ClientServerWrapper):

    def get_server_prog_path(self):
        return "echo Server"

    def get_client_prog_path(self):
        return "../ping.py"

    def configure_parser(self):
        super(DpdkWrapper, self).configure_parser()
 
        # Arguments
	self.add_dynamic_client_argument('--ip', self.get_server_manage_ip, value_only=False, priority=1)
        self.add_client_cmd_argument('--msg_size', help='The msg size', type=str, value_only=False, priority=2)
        self.add_client_cmd_argument('--iter_num', help='The iter num', type=str, value_only=False, priority=3)
        self.add_client_cmd_argument('--timeout', help='The timeout', type=str, value_only=False, priority=4)

	#self.add_dynamic_server_argument('--ip_address_server', self.get_server_manage_ip, value_only=True, priority=1)
        #self.add_server_cmd_argument('--port_server', help='The server port', type=str, value_only=True, priority=2)

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
    wrapper = DpdkWrapper("JX Wrapper")
    wrapper.execute(sys.argv[1:])

