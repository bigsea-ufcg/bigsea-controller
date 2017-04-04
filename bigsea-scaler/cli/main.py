from api.v10 import app
import ConfigParser


def main():
    config = ConfigParser.RawConfigParser()
    config.read("controller.cfg")

    host = config.get("flask", "host")
    port = config.getint("flask", "port")

    app.run(host, port, debug = True)

if __name__ == "__main__":
    main()
