from data import functions
import sys
import json
import threading
import socket
import ipaddress
from time import sleep


def setup_qubo_command():
    while True:
        functions.clear()
        print(language["server"]["qubo_command_settings"]["pingcount"], settings["qubo_command"]["pingcount"])
        print(language["server"]["qubo_command_settings"]["fulloutput"], settings["qubo_command"]["fulloutput"])
        print(language["server"]["qubo_command_settings"]["filtermotd"], settings["qubo_command"]["filtermotd"])
        print(language["server"]["qubo_command_settings"]["noping"], settings["qubo_command"]["noping"])
        print(language["server"]["qubo_command_settings"]["minonline"], settings["qubo_command"]["minonline"])
        print(language["server"]["qubo_command_settings"]["portrange"], settings["qubo_command"]["portrange"])
        print(language["server"]["qubo_command_settings"]["threads"], settings["qubo_command"]["threads"])
        print(language["server"]["qubo_command_settings"]["timeout"], settings["qubo_command"]["timeout"])
        print(language["server"]["qubo_command_settings"]["filterversion"], settings["qubo_command"]["filterversion"])
        print(language["server"]["qubo_command_settings"]["exit"])
        x = int(input(language["choice"]))
        if 1 <= x <= 9:
            if x == 1:
                settings["qubo_command"]["pingcount"] = int(input(language["server"]["qubo_command_settings"]["pingcount"]))
            elif x == 2:
                if settings["qubo_command"]["fulloutput"] is None:
                    settings["qubo_command"]["fulloutput"] = True
                elif settings["qubo_command"]["fulloutput"]:
                    settings["qubo_command"]["fulloutput"] = False
                else:
                    settings["qubo_command"]["fulloutput"] = True
            elif x == 3:
                settings["qubo_command"]["filtermotd"] = input(
                    language["server"]["qubo_command_settings"]["filtermotd"])
            elif x == 4:
                if settings["qubo_command"]["noping"] is None:
                    settings["qubo_command"]["noping"] = True
                elif settings["qubo_command"]["noping"]:
                    settings["qubo_command"]["noping"] = False
                else:
                    settings["qubo_command"]["noping"] = True
            elif x == 5:
                settings["qubo_command"]["minonline"] = int(input(language["server"]["qubo_command_settings"]["minonline"]))
            elif x == 6:
                settings["qubo_command"]["portrange"] = input(language["server"]["qubo_command_settings"]["portrange"])
            elif x == 7:
                settings["qubo_command"]["threads"] = int(input(language["server"]["qubo_command_settings"]["threads"]))
            elif x == 8:
                settings["qubo_command"]["timeout"] = int(input(language["server"]["qubo_command_settings"]["timeout"]))
            elif x == 9:
                settings["qubo_command"]["filterversion"] = input(
                    language["server"]["qubo_command_settings"]["filterversion"])
        elif x == 10:
            if settings["qubo_command"]["portrange"] is None \
                    or settings["qubo_command"]["threads"] is None \
                    or settings["qubo_command"]["timeout"] is None:
                print(language["server"]["qubo_command_settings"]["cant_exit"])
                input(language["pause"])
            else:
                return


class client:
    def __init__(self):
        self.host = input(language["server"]["ask_ip"])
        self.port = input(language["server"]["ask_port"])
        if self.port == "":
            self.port = 4100
        else:
            self.port = int(self.port)
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            print(language["server"]["connection_established"])
        except:
            print(language["Server"]["no_connection"])
            input(language["pause"])
            self.kill()

    def receive_packet(self):
        arr = b''
        while len(arr) < 1:
            arr += self.sock.recv(1024)
        return arr.decode("utf-8")

    def send_packet(self, packet):
        self.sock.send(bytes(packet, "utf-8"))

    def send_range(self, raw_range):
        json_qubo_command = settings["qubo_command"]
        json_qubo_command["range"] = raw_range
        self.send_packet(json.dumps(json_qubo_command))

    def kill(self):
        self.sock.close()
        i = 0
        for client_obj in client_list:
            if self == client_obj:
                del client_list[i]
            i = i + 1
        del self


def range_calculator(number_of_client, raw_range):
    first_ip = raw_range.split("-")[0]
    last_ip = raw_range.split("-")[1]
    print(first_ip, "-", last_ip)
    first_ip_int = int(ipaddress.IPv4Address(first_ip))
    last_ip_int = int(ipaddress.IPv4Address(last_ip))

    difference = last_ip_int - first_ip_int
    diff_between_ip = int(difference / number_of_client)
    diff_between_ip_copy = diff_between_ip

    divided_range = [(str(first_ip) + "-" + str(ipaddress.IPv4Address(diff_between_ip + first_ip_int)))]

    for x in range(number_of_client - 1):
        range_string = str(ipaddress.IPv4Address(diff_between_ip + first_ip_int + 1)) + "-"
        diff_between_ip += diff_between_ip_copy
        if x == number_of_client - 2:
            range_string += last_ip
        else:
            range_string += str(ipaddress.IPv4Address(diff_between_ip + first_ip_int))
        divided_range.append(range_string)
    return divided_range


class results:
    def __init__(self, range_name, client_number):
        self.range_name = range_name
        self.client_number = client_number
        self.result_list = []

    def show_result(self):
        print('\n'.join(self.result_list))
        input(language["pause"])

    def save_results(self):
        functions.save_file('\n'.join(self.result_list), "results/" + self.range_name + ".txt")

    def get_state(self):
        if len(self.result_list) != self.client_number:
            return self.range_name + language["server"]["scan_running"]
        else:
            return self.range_name + language["server"]["scan_finished"]

    def add_range(self, client_obj):
        self.result_list.append(client_obj.receive_packet())

    def wait_all(self):
        while len(self.result_list) != self.client_number:
            sleep(10)
        self.save_results()


def receive_results(range_name):
    result_list.append(results(range_name, len(client_list)))

    for client_obj in client_list:
        thread_list.append(threading.Thread(target=result_list[len(thread_list) - 1].add_range, args=[client_obj], daemon=True))
        thread_list[len(thread_list) - 1].start()

    thread_list.append(threading.Thread(target=result_list[len(result_list) - 1].wait_all))
    thread_list[len(thread_list) - 1].daemon = True
    thread_list[len(thread_list) - 1].start()


def start_scan():
    if len(client_list) == 0:
        print(language["server"]["cant_start_scan"])
        print(language["pause"])
        return
    raw_range = input(language["server"]["input_range"])
    list_range = range_calculator(len(client_list), raw_range)
    i = 0
    for client_obj in client_list:
        client_obj.send_range(list_range[i])
        i += 1
    thread = threading.Thread(target=receive_results, args=[raw_range], daemon=True)
    thread.start()
    print(language["server"]["started_scan"])
    input(language["pause"])


def show_results():
    i = 1
    print(" 0) " + language["server"]["back"])
    for result in result_list:
        print(" ", i, ") " + result.get_state())
        i += 1
    if x := int(input(language["choice"])) != 0:
        result_list[x - 1].show_result()


def main():
    global settings
    global language
    global result_list
    global thread_list
    global client_list
    settings = functions.get_settings()
    language = functions.get_lang(settings)
    client_list = []
    thread_list = []
    result_list = []
    if settings["first_start"]:
        functions.clear()
        print(language["server"]["first_setup"])
        input(language["pause"])
        setup_qubo_command()
        settings["first_start"] = False
        functions.save_file(json.dumps(settings), "data/settings.json")
    while True:
        language = functions.get_lang(settings)
        functions.clear()
        x = input(language["server"]["menu"])
        if x == "1":
            scan_manager()
        elif x == "2":
            dscanner_manager()
        elif x == "3":
            dscanner_settings()
        elif x == "4":
            sys.exit()


def scan_manager():
    while True:
        functions.clear()
        x = input(language["server"]["scan_manager"])
        if x == "1":
            start_scan()
        elif x == "2":
            show_results()
        elif x == "3":
            break


def dscanner_manager():
    while True:
        functions.clear()
        x = input(language["server"]["dscanner_manager"])
        if x == "1":
            client_list.append(client())
        elif x == "2":
            break


def dscanner_settings():
    while True:
        functions.clear()
        x = input(language["server"]["dscanner_settings"])
        if x == "1":
            setup_qubo_command()
        elif x == "2":
            functions.get_lang(settings, 1)
            break
        elif x == "3":
            break
