from data import functions
from data import server
from data import client
import json


def main():
    settings = functions.get_settings()
    language = functions.get_lang(settings)
    functions.clear()
    print('''
  _____                                             
 |  __ \                                            
 | |  | | ___   ___  __ _  _ __   _ __    ___  _ __ 
 | |  | |/ __| / __|/ _` || '_ \ | '_ \  / _ \| '__|
 | |__| |\__ \| (__| (_| || | | || | | ||  __/| |   
 |_____/ |___/ \___|\__,_||_| |_||_| |_| \___||_|   
                                                   
                                    Ver 0.2
    ''')
    print(language["welcome"])
    input(language["pause"])
    if settings["modality"] is None:
        while True:
            functions.clear()
            print(language["modality_choice"])
            x = input(language["choice"])
            if x == "1":
                print(language["permanent_choice"])
                x = input(language["choice"])
                if x == "1":
                    settings["modality"] = "server"
                    functions.save_file(json.dumps(settings), "data/settings.json")
                server.main()

            elif x == "2":
                print(language["permanent_choice"])
                x = input(language["choice"])
                if x == "1":
                    settings["modality"] = "client"
                    functions.save_file(json.dumps(settings), "data/settings.json")
                client.main()

    elif settings["modality"] == "server":
        server.main()

    elif settings["modality"] == "client":
        client.main()


if __name__ == '__main__':
    main()
