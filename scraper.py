import requests
import csv
import config
import random
import os
from math import sqrt
from datetime import datetime, date

tba_base_url = "https://www.thebluealliance.com/api/v3/"


class MatchData:
    def __init__(self, event_key, match_key, week, red_score, red_auto, blue_score, blue_auto):
        self.event = event_key
        self.match = match_key
        self.week = int(week)

        self.red_score = int(red_score)
        self.red_auto = int(red_auto)
        self.blue_score = int(blue_score)
        self.blue_auto = int(blue_auto)

        if self.red_score > self.blue_score:
            self.winner = "red"
        elif self.blue_score > self.red_score:
            self.winner = "blue"
        else:
            self.winner = "tie"

        if self.red_auto > self.blue_auto:
            self.auto_winner = "red"
        elif self.blue_auto > self.red_auto:
            self.auto_winner = "blue"
        else:
            self.auto_winner = "tie"

        self.winners_match = self.winner == self.auto_winner and self.winner != "tie" and self.auto_winner != "tie"

        if self.red_score - self.red_auto > self.blue_score - self.blue_auto:
            winner_no_auto = "red"
        elif self.blue_score - self.blue_auto > self.red_score - self.red_auto:
            winner_no_auto = "blue"
        else:
            winner_no_auto = "tie"

        self.decided_by_auto = winner_no_auto != self.winner


class Event:
    def __init__(self, key, week, start_date, end_date):
        self.key = key
        self.week = week

        self.start_date = start_date
        self.end_date = end_date


def get_completed_events(year):
    current_date = date.today()

    request_url = tba_base_url + "events/" + str(year)
    payload = {"X-TBA-Auth-Key": config.api_key}
    request = requests.get(request_url, params=payload).json()

    all_events = []
    for event in request:
        event_end_date = datetime.strptime(event["end_date"], "%Y-%m-%d").date()
        event_start_date = datetime.strptime(event["start_date"], "%Y-%m-%d").date()
        if event_end_date < current_date and 0 <= event["event_type"] <= 6:
            all_events.append(Event(event["key"], event["week"]+1, event_start_date, event_end_date))

    return all_events


def get_all_matches(events):
    all_matches = []
    for event in events:
        print("Getting " + event.key)
        request_url = tba_base_url + "event/" + event.key + "/matches"
        payload = {"X-TBA-Auth-Key": config.api_key}
        request = requests.get(request_url, params=payload).json()

        for match in request:
            match_key = match["key"]
            red_score = match["score_breakdown"]["red"]["totalPoints"]
            red_auto = match["score_breakdown"]["red"]["autoPoints"]
            blue_score = match["score_breakdown"]["blue"]["totalPoints"]
            blue_auto = match["score_breakdown"]["blue"]["autoPoints"]

            all_matches.append(MatchData(event.key, match_key, event.week, red_score, red_auto, blue_score, blue_auto))

    return all_matches


def pick_random_matches(matches, sample_size):
    return random.sample(matches, sample_size)


def calc_sample_stats(matches):
    n = len(matches)
    num_same_winners = 0
    num_decided_by_auto = 0
    for match in matches:
        if match.winners_match:
            num_same_winners += 1
        if match.decided_by_auto:
            num_decided_by_auto += 1

    p_same = num_same_winners / n
    q_same = 1 - p_same
    std_err_same = sqrt(p_same * q_same / n)

    p_dec = num_decided_by_auto / n
    q_dec = 1 - p_dec
    std_err_dec = sqrt(p_dec * q_dec / n)

    return n, (p_same, q_same, std_err_same), (p_dec, q_dec, std_err_dec)


def filter_matches_by_week(matches, week):
    return [match for match in matches if match.week == week]


def import_matches(path):
    if not os.path.exists(path):
        raise FileNotFoundError

    matches = []
    with open(path, 'r', newline='') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            matches.append(MatchData(*row[:7]))

    return matches


def export_matches(matches, path):
    if not os.path.exists(path.rsplit("/", 1)[0]):
        os.makedirs(path.rsplit("/", 1)[0])

    with open(path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["event", "match", "week",
                         "red_score", "red_auto", "blue_score", "blue_auto",
                         "winner", "auto_winner", "winners_match", "decided_by_auto"])

        for match in matches:
            row = vars(match).values()
            writer.writerow(row)


if __name__ == "__main__":
    all_matches = import_matches("../data/all_matches.csv")
    # all_events = get_completed_events(2018)
    # all_matches = get_all_matches(all_events)
    # export_matches(all_matches, "../data/all_matches.csv")

    selected_sample = pick_random_matches(all_matches, int(len(all_matches)*0.09))
    export_matches(selected_sample, "../data/sample.csv")

    for w in range(1, 8):
        w_sample = filter_matches_by_week(selected_sample, w)
        export_matches(w_sample, "../data/sample_w" + str(w) + ".csv")
