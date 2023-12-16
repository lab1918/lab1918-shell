from lab1918_shell.config import Config


def main():
    config = Config()
    config.ensure_default_config()
    default_config = config.get_config(profile="default")
    if default_config["api_key"] == "<replace with api key>":
        print("config proper api key at ~/.lab1918/shell.ini!")


if __name__ == "__main__":
    main()
