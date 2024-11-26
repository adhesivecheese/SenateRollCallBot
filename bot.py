from configparser import ConfigParser
import requests
from time import sleep

import xmltodict
from atproto import Client, client_utils

from db import Session, Vote_Table
from bot_logging import logger


config = ConfigParser()
config.read('config.ini')
username = config["BSKY"].get("username")
password = config["BSKY"].get("password")

congress_number = config["MAIN"].getint("congress_number")
congress_session = config["MAIN"].getint("congress_session")
check_minutes = config["MAIN"].getint("check_minutes")



client = Client()
profile = client.login(username, password)
db = Session()


class Vote:
    def __init__(self, congress_number, number, date, issue, question, result, yeas, nays, title):
        self.number = number
        self.ordinal = self.getOrdinal(congress_number)
        self.date = date
        self.issue = self.parse_issue(issue)
        self.question = question
        self.result = result
        self.yeas = yeas
        self.nays = nays
        self.title = title
        self.trimmed_title = self.trim_title()

    def getOrdinal(self, congress_number):
        if congress_number % 100 in (11, 12, 13): return f"{congress_number}th"
        elif congress_number % 10 == 1: return f"{congress_number}st"
        elif congress_number % 10 == 2: return f"{congress_number}nd"
        elif congress_number % 10 == 3: return f"{congress_number}rd"
        else: return f"{congress_number}th"

    def parse_issue(self, issue):
        if issue.startswith("PN"):
            return f"https://www.congress.gov/nomination/{self.ordinal}/{self.number}"
        elif issue.startswith("S. "):
            return f"https://www.congress.gov/bill/{self.ordinal}/senate-bill/{self.number}"
        elif issue.startswith("S.J."):
            return f"https://www.congress.gov/bill/{self.ordinal}/senate-joint-resolution/{self.number}"
        elif issue.startswith("H.R."):
            return f"https://www.congress.gov/bill/{self.ordinal}/house-bill/{self.number}"
        else:
            return "N/A"

    def trim_title(self):
        if len(self.title) < 200:
            return self.title
        else:
            mangled_title = self.title[:199] + "…"
            return mangled_title


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
    unposted_votes = []
    for vote in data:
        v = Vote(congress_number, vote['vote_number'], vote['vote_date'], vote['issue'], vote['question'], vote['result'], vote['vote_tally']['yeas'], vote['vote_tally']['nays'],vote['title'])
        if check_seen_vote(v.number): continue
        unposted_votes.append(v)
        commit_vote(v.number)
    unposted_votes.reverse()
    for vote in unposted_votes:
        print(vote.issue)
        if vote.issue != "N/A":
            text = client_utils.TextBuilder().text(f"{vote.date} - ").link(vote.trimmed_title, vote.issue).text(f" - Result: {vote.result} ({vote.yeas}-{vote.nays})")
            logger.info(f"Sending skeet! `{vote.date} - {vote.trimmed_title} - Result: {vote.result} ({vote.yeas}-{vote.nays}) Link: {vote.issue}`")
        else:
            msg = f"{vote.date} - {vote.trimmed_title} - Result: {vote.result} ({vote.yeas}-{vote.nays})"
            text = client_utils.TextBuilder().text(msg)
            logger.info(f"Sending skeet: `{msg}`")
        try:
            client.send_post(text)
            logger.debug("skeet sent!")
        except Exception as e:
            logger.error(e)

while True:
    logger.debug("checking for votes")
    check_for_votes()
    sleep(check_minutes*60)
