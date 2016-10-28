from datetime import datetime
import configparser
from NexusInterface import *
import os

def print_banner():
    print(" ____  _                          _               ____        _        ")
    print("|  _ \(_)_ __ ___   ___ _ __  ___(_) ___  _ __   |  _ \  __ _| |_ __ _ ")
    print("| | | | | '_ ` _ \ / _ \ '_ \/ __| |/ _ \| '_ \  | | | |/ _` | __/ _` |")
    print("| |_| | | | | | | |  __/ | | \__ \ | (_) | | | | | |_| | (_| | || (_| |")
    print("|____/|_|_| |_| |_|\___|_| |_|___/_|\___/|_| |_| |____/ \__,_|\__\__,_|")
    print(" _   _      _                      _      _____           _ _    _ _   ")
    print("| \ | | ___| |___      _____  _ __| | __ |_   _|__   ___ | | | _(_) |_ ")
    print("|  \| |/ _ \ __\ \ /\ / / _ \| '__| |/ /   | |/ _ \ / _ \| | |/ / | __|")
    print("| |\  |  __/ |_ \ V  V / (_) | |  |   <    | | (_) | (_) | |   <| | |_ ")
    print("|_| \_|\___|\__| \_/\_/ \___/|_|  |_|\_\   |_|\___/ \___/|_|_|\_\_|\__|")


'''
This function prints the menu of the toolkit. Prior to that, it will clear the terminal
screen by calling the OS command 'cls'. This probably work only in Windows and cross
platform interoperability has not been taken into consideration.
'''
def print_menu():
    os.system('cls')
    print_banner()
    print("\n" + "=" * 12)
    print(" Main Menu:")
    print("=" * 12 + "\n")
    print("1. Print summary of interface alert on screen.")
    print("2. Save summary of interface alert to file.")
    print("3. Print CDP neighbors in detail.")
    print("4. Save CDP neighbors detail to file.")
    print("5. Exit.")


'''
This function reads the configuration file called "config.cfg" stored in the
same directory of the script, collecting all the network devices info like
IP, username and password then put them into a dictionary type variable
and return to the caller.
'''
def parse_config():
    config = configparser.ConfigParser()
    config.read("config.cfg")
    config_data = {}

    for config_section in config.sections():
        config_subdata = {}
        for config_item in config[config_section]:
            config_subdata[config_item] = config[config_section][config_item]
        config_data[config_section] = config_subdata
    return config_data


if __name__ == '__main__':
    while True:
        print_menu()
        user_input = input("\nEnter your option: ")
        if user_input == '1':
            # Variable action is to decide either sending the text to the terminal screen or file writing
            # for now this variable is either 'print' or 'write'
            action = 'print'

            # Call the function and store the nested dictionary into variable devices_list
            devices_list = parse_config()

            # devices_list has two layer. First layer consists of user-defined hostname in the section title
            # of config.cfg file. Second layer is the actual device parameter like {'ip':<ip>, 'username':<username>,
            # 'password':<password>}
            for each in devices_list:
                # For each Nexus device, a separate instance will be created to capture the info required.
                interface_obj = NexusInterface(devices_list[each], action)
                interface_obj.display_info()
                interface_obj.display_alert()
                input("Hit return to go to the next device or back to the menu.")
                print("\n")

        elif user_input == '2':
            # Action variable with the keyword 'write' will ask the function to store all the text
            # in a single variable for file writing purpose
            action = 'write'
            devices_list = parse_config()

            # Initialize a string variable to store the text returned from the function get_file_content() in NexusInterface
            file_content = ''
            for each in devices_list:
                interface_obj = NexusInterface(devices_list[each], action)
                interface_obj.display_info()
                interface_obj.display_alert()
                file_content += interface_obj.get_file_content()

            # Generate the filename by inserting the date and time at that point of time to ensure file uniqueness
            filename = 'interface_alert_' + datetime.today().strftime("%Y%m%d-%H%M%S") + '.txt'
            with open(filename, 'w') as myfile:
                myfile.write(file_content)
            print('The summary of interface alert has been saved to the file name "' + filename + '".')
            input("Hit return to go back to the menu.")
            print("\n")

        elif user_input == '3':
            action = 'print'
            devices_list = parse_config()
            for each in devices_list:
                interface_obj = NexusInterface(devices_list[each], action)
                interface_obj.display_info()
                interface_obj.display_neighbors()
                input("Hit return to go to the next device or back to the menu.")
                print("\n")

        elif user_input == '4':
            action = 'write'
            devices_list = parse_config()
            file_content = ''
            for each in devices_list:
                interface_obj = NexusInterface(devices_list[each], action)
                interface_obj.display_info()
                interface_obj.display_neighbors()
                file_content += interface_obj.get_file_content()
                filename = 'cdp_neighbor_' + datetime.today().strftime("%Y%m%d-%H%M%S") + '.txt'
            with open(filename, 'w') as myfile:
                myfile.write(file_content)
            print('The CDP neighbors detail has been saved to the file name "' + filename + '".')
            input("Hit return to go back to the menu.")
            print("\n")

        elif user_input == '5':
            break
        else:
            input("Invalid input. Hit return and try to enter again.")
