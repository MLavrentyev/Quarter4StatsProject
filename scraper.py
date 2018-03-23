import requests
import csv
import config

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


def get_all_matches(events):
    all_matches = []
    for event in events:
        request_url = tba_base_url + event + "/matches"
        payload = {"X-TBA-Auth-Key": config.api_key}

        request = requests.get(request_url, params=payload).json()

        for match in event:
            match_key = request["key"]
            red_score = request["score_breakdown"]["red"]["totalPoints"]
            red_auto = request["score_breakdown"]["red"]["autoPoints"]
            blue_score = request["score_breakdown"]["blue"]["totalPoints"]
            blue_auto = request["score_breakdown"]["blue"]["autoPoints"]

            all_matches.append(MatchData(event, match_key, red_score, red_auto, blue_score, blue_auto))

    return all_matches


if __name__ == "__main__":
    all_matches = get_all_matches(["2018ctwat", "2018ctsct"])