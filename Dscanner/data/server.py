import json
import socket
import sys
import threading
from time import sleep
from data import functions


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
                settings["qubo_command"]["pingcount"] = int(
                    input(language["server"]["qubo_command_settings"]["pingcount"]))
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
                settings["qubo_command"]["minonline"] = int(
                    input(language["server"]["qubo_command_settings"]["minonline"]))
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
                functions.save_file(json.dumps(settings), "data/settings.json")
                return


class client:
    def __init__(self, target=None):
        self.wait_status = False
        if target is None:
            self.host = input(language["server"]["ask_ip"])
            print(language["server"]["ask_port"])
            self.port = input(language["choice"])
            if self.port == "":
                self.port = 4100
            else:
                self.port = int(self.port)
        else:
            self.host, self.port = target

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            print(language["server"]["connection_established"], self.host, ":", self.port)
            sleep(2)
        except:
            print(language["server"]["no_connection"])
            input(language["pause"])
            self.kill()

    def receive_packet(self):
        self.wait_status = True
        arr = b''
        while len(arr) < 1:
            arr += self.sock.recv(1024)
        self.wait_status = False
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


class results:
    def __init__(self, range_name, client_number):
        self.range_name = range_name
        self.client_number = client_number
        self.result_list = []
        for i in range(self.client_number):
            self.result_list.append("")
        self.add_scan()

    def show_result(self):
        print('\n'.join(self.result_list))
        input(language["pause"])

    def save_results(self):
        functions.save_file('\n'.join(self.result_list), "results/" + self.range_name + ".txt")

    def get_state(self):
        for x in self.result_list:
            if x == "":
                return False
        return True

    def add_scan(self):
        i = 0
        threads = []
        for client_obj in client_list:
            if self.result_list[i] == "":
                threads.append(threading.Thread(target=self.add_range, args=[client_obj, i], daemon=True))
                threads[-1].start()
            i += 1

        threads.append(threading.Thread(target=self.wait_all, daemon=True))
        threads[-1].start()

    def add_range(self, client_obj, counter):
        while client_obj.wait_status:
            sleep(5)
        self.result_list[counter] = client_obj.receive_packet()

    def wait_all(self):
        while not self.get_state():
            sleep(10)
        self.save_results()


def start_scan():
    if len(client_list) == 0:
        print(language["server"]["cant_start_scan"])
        input(language["pause"])
        return
    raw_range = input(language["server"]["input_range"])
    good_range = functions.range_parse(raw_range)
    list_range = functions.range_calculator(len(client_list), good_range)
    if list_range is not None:
        i = 0
        for client_obj in client_list:
            client_obj.send_range(list_range[i])
            i += 1

        scan_list.append(results(good_range, len(client_list)))

        print(language["server"]["started_scan"])
    else:
        print("Invalid range")
    input(language["pause"])


def show_results():
    while True:
        i = 1
        print(" 0) " + language["server"]["back"])
        for result in scan_list:
            if result.get_state():
                print(" " + str(i) + ") ", result.range_name, language["server"]["scan_finished"])
            else:
                print(" " + str(i) + ") ", result.range_name, language["server"]["scan_running"])
            i += 1

        x = input(language["choice"])
        if x == "":
            break
        elif int(x) == 0:
            break
        elif 0 < int(x) < i:
            scan_list[int(x) - 1].show_result()


def main():
    global settings
    global language
    global scan_list
    global client_list
    settings = functions.get_settings()
    language = functions.get_lang(settings)
    client_list = []
    scan_list = []
    if settings["first_start"]:
        functions.clear()
        print(language["server"]["first_setup"])
        input(language["pause"])
        setup_qubo_command()
        settings["first_start"] = False
        functions.save_file(json.dumps(settings), "data/settings.json")
        print(language["server"]["close_warning"])
        input(language["pause"])

    functions.clear()
    if settings["load_last_session"]:
        load_last_session()

    try:
        main_menu()
    finally:
        close_and_save_all()


def load_last_session():
    print(language["server"]["loading_last_session"])
    settings["load_last_session"] = False
    functions.save_file(json.dumps(settings), "data/settings.json")
    last_session = functions.get_last_session()
    for x in last_session["clients"]:
        client_list.append(client(x))
    for x in last_session["scans"]:
        scan_list.append(results(x, len(client_list)))
    i = 0
    for x in last_session["scans_results"]:
        scan_list[i].result_list = x
        i += 1
    sleep(2)
    functions.clear()


def close_and_save_all():
    while True:
        print(language["server"]["save_ask"])
        x = input(language["choice"])
        if x == "1":
            file_to_save = {
                "clients": [],
                "scans": [],
                "scans_results": []
            }
            for client in client_list:
                file_to_save["clients"].append((client.host, client.port))
            for scan in scan_list:
                file_to_save["scans"].append(scan.range_name)
                file_to_save["scans_results"].append(scan.result_list)
            functions.save_file(json.dumps(file_to_save), "data/tmp/last_session.json")
            settings["load_last_session"] = True
            functions.save_file(json.dumps(settings), "data/settings.json")
            sys.exit()
        elif x == "2":
            break


def main_menu():
    while True:
        language = functions.get_lang(settings)
        functions.clear()
        print(language["server"]["menu"])
        x = input(language["choice"])
        if x == "1":
            scan_manager()
        elif x == "2":
            dscanner_manager()
        elif x == "3":
            dscanner_settings()
        elif x == "4":
            break


def scan_manager():
    while True:
        functions.clear()
        print(language["server"]["scan_manager"])
        x = input(language["choice"])
        if x == "1":
            start_scan()
        elif x == "2":
            show_results()
        elif x == "3":
            break


def dscanner_manager():
    while True:
        functions.clear()
        print(language["server"]["dscanner_manager"])
        x = input(language["choice"])
        if x == "1":
            client_list.append(client())
        elif x == "2":
            break


def dscanner_settings():
    while True:
        global language
        functions.clear()
        print(language["server"]["dscanner_settings"])
        x = input(language["choice"])
        if x == "1":
            setup_qubo_command()

        elif x == "2":
            language = functions.get_lang(settings, 1)
        elif x == "3":
            break
