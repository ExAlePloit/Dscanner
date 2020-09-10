from data import functions
import socket
import threading
import sys
import json
from subprocess import Popen, PIPE


def receive_mex(client_socket):
    arr = b''
    while len(arr) < 1:
        arr += client_socket.recv(1024)
    return arr.decode("utf-8")


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

                                    return command
    return None


def connection(client_socket):
    while True:
        json_command = json.loads(receive_mex(client_socket))
        print(json_command["range"], language["client"]["scan_started"])
        command = parsecommand(json_command)
        if command is not None:
            process = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
            process.wait()
            stdout = process.communicate()[0]
            client_socket.send(stdout)
            print(json_command["range"], language["client"]["scan_finished"])
        else:
            client_socket.send(bytes("None", "utf-8"))


def main():
    global settings
    global language
    settings = functions.get_settings()
    language = functions.get_lang(settings)

    functions.clear()
    port = input(language["client"]["first_setup"])
    if port == "":
        port = 4100
    elif not 1024 <= int(port) <= 65535:
        print(language["client"]["error_port_range"])
    else:
        port = int(port)

    print(language["client"]["waiting_connection"])
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('0.0.0.0', port))
    sock.listen(5)

    client_socket, address = sock.accept()
    print(language["client"]["connection_established"], address)
    connection_thread = threading.Thread(target=connection, args=[client_socket], daemon=True)
    connection_thread.start()

    while True:
        x = input(language["client"]["stop_connection_question"])
        if x.lower() == "stop":
            sys.exit()
