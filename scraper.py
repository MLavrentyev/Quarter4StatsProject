import requests
import csv
import config
import random
import os
from datetime import datetime, date

tba_base_url = "https://www.thebluealliance.com/api/v3/"

class MatchData:
    def __init__(self, event_key, match_key, red_score, red_auto, blue_score, blue_auto):
        self.event = event_key
        self.match = match_key

        self.red_score = red_score
        self.red_auto = red_auto
        self.blue_score = blue_score
        self.blue_auto = blue_auto

        self.winner = "red" if red_score > blue_score else "blue"
        self.auto_winner = "red" if red_auto > blue_auto else "blue"
        self.winners_match = self.winner == self.auto_winner


def get_completed_events(year):
    current_date = date.today()

    request_url = tba_base_url + "events/" + str(year) + "/simple"
    payload = {"X-TBA-Auth-Key": config.api_key}
    request = requests.get(request_url, params=payload).json()

    all_event_keys = []
    for event in request:
        event_end_date = datetime.strptime(event["end_date"], "%Y-%m-%d").date()
        if event_end_date < current_date and 0 <= event["event_type"] <= 6:
            all_event_keys.append(event["key"])

    return all_event_keys

def get_all_matches(events):
    all_matches = []
    for event in events:
        print("Getting " + event)
        request_url = tba_base_url + "event/" + event + "/matches"
        payload = {"X-TBA-Auth-Key": config.api_key}
        request = requests.get(request_url, params=payload).json()

        for match in request:
            match_key = match["key"]
            red_score = match["score_breakdown"]["red"]["totalPoints"]
            red_auto = match["score_breakdown"]["red"]["autoPoints"]
            blue_score = match["score_breakdown"]["blue"]["totalPoints"]
            blue_auto = match["score_breakdown"]["blue"]["autoPoints"]

            all_matches.append(MatchData(event, match_key, red_score, red_auto, blue_score, blue_auto))

    return all_matches

def pick_random_matches(matches, sample_size):
    return random.sample(matches, sample_size)

def import_matches(path):
    if not os.path.exists(path):
        raise FileNotFoundError

    matches = []
    with open(path, 'r', newline='') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            matches.append(MatchData(*row[:6]))

    return matches

def export_matches(matches, path):
    if not os.path.exists(path.rsplit("/", 1)[0]):
        os.makedirs(path.rsplit("/", 1)[0])

    with open(path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["event", "match", "red_score", "red_auto", "blue_score", "blue_auto",
                         "winner", "auto_winner", "winners_match"])

        for match in matches:
            row = vars(match).values()
            writer.writerow(row)

if __name__ == "__main__":
    all_matches = import_matches("../data/all_matches.csv")
    print(vars(all_matches[0]))