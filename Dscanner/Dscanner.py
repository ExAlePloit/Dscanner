from data import functions
from data import server
from data import client


def main():
    settings = functions.get_settings()
    language = functions.get_lang(settings)
    functions.clear()
    print(language["welcome"])
    input(language["pause"])
    if settings["modality"] is None:
        while True:
            functions.clear()
            x = input(language["modality_choice"])

            if x == "1":
                x = input(language["permanent_choice"])
                if x == "1":
                    settings["modality"] = "server"
                server.main()

            elif x == "2":
                x = input(language["permanent_choice"])
                if x == "1":
                    settings["modality"] = "client"
                client.main()

    elif settings["modality"] == "server":
        server.main()

    elif settings["modality"] == "client":
        client.main()


if __name__ == '__main__':
    main()
