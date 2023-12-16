from lab1918_shell.config import Config


def main():
    config = Config()
    default = config.get_config(profile="default")
    if default["api_key"] == "<replace with api key>":
        print("config proper api key at ~/.lab1918/shell.ini!")


if __name__ == "__main__":
    main()
