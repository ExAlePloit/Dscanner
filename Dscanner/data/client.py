from data import functions
import socket
import threading
import sys
import json
from subprocess import Popen, PIPE
from time import sleep


def parsecommand(json_command):
    command = "java -jar -Dfile.encoding=UTF-8 data/qubo.jar -nooutput"

    if json_command["range"] is not None:
        charther = ["-", ".", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]
        goodrange = True
        for char in json_command["range"]:
            if charther.count(char) == 0:
                goodrange = False
                break
        if goodrange:
            command += " --iprange " + json_command["range"]

            if json_command["portrange"] is not None:
                charther = ["-", ",", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]
                goodrange = True
                for char in json_command["portrange"]:
                    if charther.count(char) == 0:
                        goodrange = False
                        break
                if goodrange:
                    command += " --portrange " + json_command["portrange"]

                    if json_command["threads"] is not None:
                        if json_command["threads"] > 0:
                            command += " --threads " + str(json_command["threads"])

                            if json_command["timeout"] is not None:
                                if json_command["timeout"] > 0:
                                    command += " --timeout " + str(json_command["timeout"])

                                    if json_command["pingcount"] is not None:
                                        if 0 < json_command["pingcount"] < 20:
                                            command += " --pingcount " + str(json_command["pingcount"])

                                    if json_command["fulloutput"]:
                                        command += " -fulloutput "

                                    if json_command["filtermotd"] is not None:
                                        if 1 < json_command["filtermotd"].len() < 100:
                                            command += " --filtermotd " + json_command["filtermotd"]

                                    if json_command["noping"]:
                                        command += " -noping "

                                    if json_command["minonline"] is not None:
                                        if json_command["minonline"] > 1:
                                            command += " --minonline " + str(json_command["minonline"])

                                    if json_command["filterversion"] is not None:
                                        if 1 < json_command["filterversion"].len() < 100:
                                            command += " --filterversion " + json_command["filterversion"]

                                    return command, json_command["range"]
    return None


def receive_mex(client_socket):
    try:
        arr = b''
        while len(arr) < 1:
            arr += client_socket.recv(1024)
        return arr.decode("utf-8")
    except:
        return 0


class scan:
    def __init__(self, sock):
        self.command = []
        self.scan_range = []
        self.target = []
        self.stdout = []
        self.send_thread = []
        self.sock = sock
        self.connected = True
        self.scan_counter = 0
        self.scan_to_do = 0
        self.scan_thread = threading.Thread(target=self.start_scan, daemon=True)
        self.scan_thread.start()

    def add_scan(self, command, target, scan_range):
        if self.scan_counter < self.scan_to_do:
            print(scan_range, language["client"]["scan_queue"])
        self.command.append(command)
        self.target.append(target)
        self.scan_range.append(scan_range)
        self.scan_to_do += 1

    def start_scan(self):
        while True:
            if self.scan_counter < self.scan_to_do:
                process = Popen(self.command[self.scan_counter], shell=True, stdout=PIPE, stderr=PIPE)
                print(self.scan_range[self.scan_counter], language["client"]["scan_started"])
                process.wait()
                self.stdout.append(process.communicate()[0])
                print(self.scan_range[self.scan_counter], language["client"]["scan_finished"])
                self.send_thread.append(threading.Thread(target=self.send_results, daemon=True))
                self.send_thread[self.scan_counter].start()
                self.scan_counter += 1

    def send_results(self):
        counter = self.scan_counter
        while True:
            if self.connected:
                self.sock.send(self.stdout[counter])
                break
            sleep(5)

    def new_socket(self, sock):
        self.sock = sock
        self.connected = True

    def set_status(self, status):
        self.connected = status


def connection(port):
    alert_connection = False
    while True:
        print(language["client"]["waiting_connection"])
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('0.0.0.0', port))
        sock.listen(5)
        client_socket, address = sock.accept()
        connected = True
        if alert_connection:
            scanner.new_socket(client_socket)
            alert_connection = False
        else:
            scanner = scan(client_socket)
        print(language["client"]["connection_established"], address)
        while connected:
            received_mex = receive_mex(client_socket)
            if received_mex == 0:
                connected = False
                scanner.set_status(connected)
                alert_connection = True
                print(language["client"]["connection_lost"], address)
            else:
                json_command = json.loads(received_mex)
                command, scan_range = parsecommand(json_command)
                if command is not None:
                    scanner.add_scan(command, address, scan_range)
                else:
                    client_socket.send(bytes("None", "utf-8"))


def main():
    global settings
    global language
    settings = functions.get_settings()
    language = functions.get_lang(settings)

    functions.clear()
    print(language["client"]["first_setup"])
    port = input(language["choice"])
    if port == "":
        port = 4100
    elif not 1025 <= int(port) <= 65535:
        print(language["client"]["error_port_range"])
    else:
        port = int(port)

    connection_thread = threading.Thread(target=connection, args=[port], daemon=True)
    connection_thread.start()

    while True:
        x = input(language["client"]["stop_connection_question"])
        if x.lower() == "stop":
            sys.exit()
