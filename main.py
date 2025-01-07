import sys
import traceback

from api import *
from config import *

logfile = "error.log"

aliases = {
    "li": "login",
    "lo": "logout",
    "r": "refresh",
    "f": "freshlogin",
    "a": "auth",
    "s": "sessions",
    "k": "kill",
    "rt": "route",
    "h": "help"
}


def change_auth_details():
    username = input("Username: ")
    password = input("Password: ")
    config = load_config()
    config["username"] = username
    config["password"] = password
    save_config(config)
    print("Updated auth details.")


def list_sessions():
    sessions = get_active_sessions()
    if len(sessions) >= 1:
        heading = "Session: 1"
        print(heading)
        print('-' * len(heading))
        sessions[0].print_details()
    for i in range(1, len(sessions)):
        heading = f"Session: {i+1}"
        print('\n' + heading)
        print('-' * len(heading))
        sessions[i].print_details()


def kill_session():
    sessions = get_active_sessions()
    session = int(input("Session number: "))
    if session > len(sessions) or session < 1:
        print(f"There are {len(sessions)} active session(s).")
        return
    terminate_session(sessions[session].number)
    print("Done.")


def choose_route():
    routes = {
        "http://1.254.254.254":
            "Works well with windows and linux, but may not work sometimes in android.",
        "http://connectivitycheck.gstatic.com":
            "Works well with android, but does not work with windows and linux."
    }
    keys = list(routes.keys())
    for i in range(len(keys)):
        key = keys[i]
        print(f"{i+1}. {key}")
        print(routes[key])
    choice = int(input("\nChoose: "))
    if choice < 1 or choice > len(keys):
        print("Invalid choice.")
        return
    config = load_config()
    config["route"] = keys[choice - 1]
    save_config(config)
    print("Updated route.")


def fresh_login():
    refresh()
    login()


def print_help():
    print("+-----------+")
    print("| MoE Wi-Fi |")
    print("+-----------+")
    print()
    print("Available options")
    print("-----------------")
    for option in options:
        print(option)
    print()
    print("Available aliases")
    print("-----------------")
    for alias in aliases:
        print(f"{alias}\t{aliases[alias]}")


options = {
    "login": login,
    "logout": logout,
    "refresh": refresh,
    "freshlogin": fresh_login,
    "auth": change_auth_details,
    "sessions": list_sessions,
    "kill": kill_session,
    "route": choose_route,
    "help": print_help
}


def main():
    if len(sys.argv) < 2:
        print("Option not specified.") 
        print(f"Available options: {', '.join(options.keys())}")
        return
    option = sys.argv[1]
    if sys.argv[1] not in options:
        if sys.argv[1] not in aliases:
            print("Invalid option.") 
            print(f"Available options: {', '.join(options.keys())}")
            return
        option = aliases[sys.argv[1]]
    options[option]()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nKeyboard interrupt.")
    except Exception as e:
        print(f"\nError: {e}")
        with open(logfile, "w") as fp:
            fp.write(traceback.format_exc())
