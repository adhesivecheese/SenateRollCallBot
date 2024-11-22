import requests
from time import sleep
import xmltodict
from configparser import ConfigParser
from atproto import Client, client_utils
from db import Session, Vote_Table


class Vote:
    def __init__(self, number, date, issue, question, result, yeas, nays, title):
        self.number = number
        self.date = date
        self.issue = self.parse_issue(issue, number)
        self.question = question
        self.result = result
        self.yeas = yeas
        self.nays = nays
        self.title = title
        self.trimmed_title = self.trim_title()

    def parse_issue(self, issue, number):
        congress_number = "118th"
        if issue.startswith("PN"):
            return f"https://www.congress.gov/nomination/{congress_number}/{number}"
        elif issue.startswith("S. "):
            return f"https://www.congress.gov/bill/{congress_number}/senate-bill/{number}"
        elif issue.startswith("S.J."):
            return f"https://www.congress.gov/bill/{congress_number}/senate-joint-resolution/{number}"
        elif issue.startswith("H.R."):
            return f"https://www.congress.gov/bill/{congress_number}/house-bill/{number}"
        else:
            return "N/A"

    def trim_title(self):
        if len(self.title) < 200:
            return self.title
        else:
            mangled_title = self.title[:199] + "…"
            return mangled_title

config = ConfigParser()
config.read('config.ini')
username = config["BSKY"].get("username")
password = config["BSKY"].get("password")

congress_number = config["MAIN"].getint("congress_number")
congress_ordinal = config["MAIN"].get("congress_ordinal")
congress_session = config["MAIN"].getint("congress_session")
check_minutes = config["MAIN"].getint("check_minutes")

client = Client()
profile = client.login(username, password)

db = Session()

def commit_vote(number):
    i = Vote_Table(congress=congress_number, session=congress_session, vote_number=number)
    db.add(i)
    db.commit()

def check_seen_vote(number):
    check = db.query(Vote_Table).filter(
            Vote_Table.congress==congress_number
            , Vote_Table.session==congress_session
            , Vote_Table.vote_number==number
        ).first()
    if check: return True
    else: return False

def check_for_votes():
    url = f'https://www.senate.gov/legislative/LIS/roll_call_lists/vote_menu_{congress_number}_{congress_session}.xml'
    response = requests.get(url)
    data = xmltodict.parse(response.content)
    data = data['vote_summary']['votes']['vote']
    all_votes = []
    for vote in data:
        v = Vote(vote['vote_number'], vote['vote_date'], vote['issue'], vote['question'], vote['result'], vote['vote_tally']['yeas'], vote['vote_tally']['nays'],vote['title'])
        if check_seen_vote(v.number): continue
        all_votes.append(v)
        commit_vote(v.number)
    all_votes.reverse()
    for vote in all_votes:
        print(vote.issue)
        if vote.issue != "N/A":
            text = client_utils.TextBuilder().text(f"{vote.date} - ").link(vote.trimmed_title, vote.issue).text(f" - Result: {vote.result} ({vote.yeas}-{vote.nays})")
        else:
            text = client_utils.TextBuilder().text(f"{vote.date} - {vote.trimmed_title} - Result: {vote.result} ({vote.yeas}-{vote.nays})")
        client.send_post(text)
    
while True:
    print("checking for votes")
    check_for_votes()
    sleep(check_minutes*60)
