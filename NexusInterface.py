from datetime import datetime
import requests
import json

class NexusInterface:

    myheaders = {'content-type': 'application/json-rpc'}
    file_content = ''

    def __init__(self, device_info, action):
        self.ip_address = device_info['ip']
        self.url = 'http://' + self.ip_address + '/ins'
        self.switchuser = device_info['username']
        self.switchpassword = device_info['password']
        self.action = action

    # Based on the variable action, this function will either print the text on the terminal
    # or concatenate to the variable file_content
    def display_text(self, text):
        if self.action == 'print':
            print(text)
        else:
            self.file_content += text

    # Return all the text that needs to be written to the file to the caller
    def get_file_content(self):
        return self.file_content


    # Obtain the current date and time and include it in the date time generation
    def print_generation_datetime(self):
        datetime_now = str(datetime.today())
        text_to_display = "\n"
        text_to_display += "Generated on " + datetime_now + "\n"
        text_to_display += ("-" * len(str("Generated on " + datetime_now))) + "\n"
        self.display_text(text_to_display)


    # Request for 'show version' command from the Nexus switch thru NXAPI and retrieve the relevant info
    # like hostname, IP address, model, serial number and software version
    def display_info(self):
        payload = [
            {
                "jsonrpc": "2.0",
                "method": "cli",
                "params": {
                    "cmd": "show version",
                    "version": 1
                },
                "id": 1
            },
        ]
        response = requests.post(self.url, data=json.dumps(payload), headers=self.myheaders,
                                 auth=(self.switchuser, self.switchpassword)).json()

        self.print_generation_datetime()
        text_to_display = "Device hostname: " + response['result']['body']['host_name'] + "\n"
        text_to_display += "Device IP address: " + self.ip_address + "\n"
        text_to_display += "Device model: " + response['result']['body']['chassis_id'] + "\n"
        text_to_display += "Device serial number: " + response['result']['body']['proc_board_id'] + "\n"
        text_to_display += "Device software version: " + response['result']['body']['kickstart_ver_str'] + "\n"
        self.display_text(text_to_display)


    # Request for 'show interface' command from the Nexus switch thru NXAPI and retrieve the relevant info
    # like status, reliability, rx/tx load and rx/tx error
    def display_alert(self):
        payload = [
            {
                "jsonrpc": "2.0",
                "method": "cli",
                "params": {
                    "cmd": "show interface",
                    "version": 1
                },
                "id": 1
            }
        ]
        response = requests.post(self.url, data=json.dumps(payload), headers=self.myheaders,
                                 auth=(self.switchuser, self.switchpassword)).json()

        # Define the column width as well as its alignment
        template = "{0:16}{1:9}{2:>13}{3:>11}{4:>11}{5:>11}{6:>11}"

        text_to_display = "-" * 84 + "\n"
        text_to_display += template.format("Interface", "Status", "Reliability %", "RX load %", "RX Err %", "TX load %", "TX Err %") + "\n"
        text_to_display += "-" * 84 + "\n"

        for each in response['result']['body']['TABLE_interface']['ROW_interface']:
            if each['interface'].startswith('Eth'):
                interface = each['interface']
                # The status is not merely based on interface up or down. It does apply some logic processing
                # and will only declare the interface is down if its administratively state is up and its
                # actual state is down. It declares the port as normal if the port is down intentionally
                if each['admin_state'] == "up" and each['state'] == "down":
                    status = "Down"
                else:
                    status = "Normal"
                reliability = '{:.2f}'.format(float(each['eth_reliability']) / 255 * 100)
                rxload = '{:.2f}'.format(float(each['eth_rxload']) / 255 * 100)
                # Include exception catching in case the divider is zero
                try:
                    rxerr = '{:.2f}'.format(float(each['eth_inerr']) / float(each['eth_inpkts']) * 100)
                except ZeroDivisionError:
                    rxerr = "0.00"
                txload = '{:.2f}'.format(float(each['eth_txload']) / 255 * 100)
                try:
                    txerr = '{:.2f}'.format(float(each['eth_outerr']) / float(each['eth_outpkts']) * 100)
                except ZeroDivisionError:
                    txerr = "0.00"

                text_to_display += template.format(interface, status, reliability + "%", rxload + "%", rxerr + "%", txload + "%", txerr + "%") + "\n"

        text_to_display += "\n"

        self.display_text(text_to_display)

    # Request for 'show cdp neighbors detail' command from the Nexus switch thru NXAPI and retrieve the relevant info
    # like neighbor hostname, platform, interface and IP addresss
    def display_neighbors(self):
        payload = [
            {
                "jsonrpc": "2.0",
                "method": "cli",
                "params": {
                    "cmd": "show cdp neighbors detail",
                    "version": 1
                },
                "id": 1
            }
        ]
        response = requests.post(self.url, data=json.dumps(payload), headers=self.myheaders,
                                 auth=(self.switchuser, self.switchpassword)).json()

        template = "{0:16}{1:16}{2:20}{3:20}{4:20}"

        text_to_display = "-" * 91 + "\n"
        text_to_display += template.format("Interface", "Neighbor Name", "Neighbor Platform", "Neighbor Interface", "Neighbor IP Address") + "\n"
        text_to_display += "-" * 91 + "\n"

        for each in response['result']['body']['TABLE_cdp_neighbor_detail_info']['ROW_cdp_neighbor_detail_info']:
            if each['intf_id'].startswith('Eth'):
                interface = each['intf_id']
                neighbor_name = each['sysname']
                neighbor_platform = each['platform_id']
                neighbor_interface = each['port_id']
                neighbor_ip = each['v4mgmtaddr']

                text_to_display += template.format(interface, neighbor_name, neighbor_platform, neighbor_interface, neighbor_ip) + "\n"

        text_to_display += "\n"

        self.display_text(text_to_display)

