import re
import pickle
import requests

from config import *
from datetime import datetime
from requests import Response

from bs4 import BeautifulSoup
from bs4.element import Tag

logfile = "response.log"


def log_response(response: Response):
    with open(logfile, "wb") as fp:
        pickle.dump(response, fp)


def get_session_id() -> str:
    config = load_config()
    route = config["route"]
    r = requests.get(route, allow_redirects=False)
    log_response(r)
    soup = BeautifulSoup(r.text, "html.parser")
    metatag = soup.find("meta", {"http-equiv": "Refresh"})
    if not metatag:
        print(f"No Refresh metatag found: {route}")
        return ""
    content = metatag.get("content") or ""
    matches = re.findall(re.compile(r"http://\S+"), content)
    if len(matches) == 0:
        print("No URL found in Refresh metatag.")
        return ""
    r = requests.get(matches[0])
    log_response(r)
    cookies = r.cookies
    if "JSESSIONID" in cookies:
        return cookies["JSESSIONID"]
    return ""


def get_cookies() -> dict:
    config = load_config()
    session_id = config["session_id"]
    if not session_id:
        return {}
    return {
        "JSESSIONID": config["session_id"]
    }


def get_headers() -> dict:
    config = load_config()
    user_agent = config["user_agent"]
    if not user_agent:
        return {}
    return {
        "User-agent": user_agent
    }


def login():
    config = load_config()
    response = requests.post(config["endpoints"]["login"], {
        "username": config["username"],
        "password": config["password"],
        "phone": "0",
        "type": "2",
        "jsonresponse": "1",
        "checkbox": "check"
    }, headers=get_headers(), cookies=get_cookies(), timeout=5)
    log_response(response)
    # getting json from response
    try:
        d = response.json()
        if not isinstance(d, dict):
            raise ValueError
    except:
        print("Response is not a JSON.")
        return
    # response status
    error_key = d.get("errorKey")
    if error_key == "success":
        print(f"Successfully logged into {config['username']}.")
    elif error_key == "redirect_to_nas":
        print("Invalid session ID.")
    elif error_key == "failureCase":
        if d.get("errorMessage"):
            print(d["errorMessage"] + "" if d["errorMessage"].endswith(".") else ".")
        else:
            print("No error message.")
    else:
        print("Something unexpected happened.")


def logout():
    config = load_config()
    response = requests.post(config["endpoints"]["logout"], headers=get_headers(), cookies=get_cookies())
    log_response(response)
    print("Done.")


def refresh():
    config = load_config()
    session_id = get_session_id()
    if session_id:
        print("Session refreshed.")
    config["session_id"] = session_id
    save_config(config)


def extract_number(text: str) -> str:
    num_pattern = re.compile(r"\d+\.?\d+")
    matches = re.findall(num_pattern, text)
    if len(matches) == 0:
        return "0"
    return matches[0]


class Session:
    name: str
    number: int
    account_id: str
    rate_plan: str
    start_time: datetime
    upload: float
    download: float

    def __init__(self, name: str, number: int, account_id: str, rate_plan: str, start_time: datetime, upload: str, download: str):
        self.name = name
        self.number = number
        self.account_id = account_id
        self.rate_plan = rate_plan
        self.start_time = start_time
        self.upload = upload
        self.download = download

    @staticmethod
    def from_rowtag(row: Tag):
        info = [i.text.strip() for i in row.find_all("td")]
        try:
            start_time = datetime.fromisoformat(info[4])
            onclick: str = row.find("input")["onclick"]
            number = int(extract_number(onclick))
            return Session(info[0], number, info[1], info[2], start_time, info[6], info[7])
        except:
            print("Invalid row structure.")
            return Session("", 0, "", "", datetime(1, 1, 1), 0, 0)
        
    def __str__(self) -> str:
        return f"{self.account_id} - {self.rate_plan}"
    
    def print_details(self):
        print(f"Name: {self.name}")
        print(f"Rate plan: {self.rate_plan}")
        print(f"Account ID: {self.account_id}")
        print(f"Start time: {self.start_time}")
        print(f"Time elapsed: {(datetime.now()-self.start_time).seconds//60} mins")
        print(f"Uploaded: {self.upload}")
        print(f"Downloaded: {self.download}")


def get_active_sessions() -> list[Session]:
    config = load_config()
    requests.post(config["endpoints"]["login"], {
        "generatePassword": "true",
        "phone": "0",
        "type": "1",
        "username": config["username"],
        "password": config["password"],
        "submit": "continue"
    }, headers=get_headers(), cookies=get_cookies())
    response = requests.get(config["endpoints"]["home"], headers=get_headers(), cookies=get_cookies())
    log_response(response)
    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table", {"id": "row"})
    rows = []
    if table:
        rows = table.find_all("tr", {"class": ("odd", "even")})
    else:
        print("Table not found. Refreshing the session may fix this.")
    return [Session.from_rowtag(row) for row in rows]


def terminate_session(sesno: int):
    config = load_config()
    requests.get(config["endpoints"]["logout"], params={
        "from": "curses",
        "sesno": sesno
    }, cookies=get_cookies(), headers=get_headers())


__all__ = [
    "login",
    "logout",
    "refresh",
    "Session",
    "get_active_sessions",
    "terminate_session"
]
