# Quarter4StatsProject
A script to get data for an AP Stats Project analyzing the importance of autonomous in FIRST Power Up. 

## Running it
To run this, you'll need to get an API key from The Blue Alliance. Head on over [here](https://www.thebluealliance.com/account) to get one. Paste that into a file named `config.py`in the directory of the project. Here's what `config.py` should look like:
```python
api_key = "your_key_here"
```
After that, you should be all set! Go ahead and run it!

## Basics
- `MatchData` class - stores each match's data that is relevant for the project including both alliance's total scores, auto scores, the winner, and the autonomous period winner.
- `get_completed_events(year)` - gets all the event keys for a given year. Only includes events that are official and are completed (i.e. `"end_date"` is earlier than the current day).
- `get_all_matches(events)` - gets a list of MatchData objects, one for every match played in all the events. Essentially aggregates all the matches for the given events.
- `pick_random_matches(matches, sample_size)` - returns a list (with size `sample_size`) of matches randomly selected from the list of matches given by `matches`.
- `import_matches(path)` - import matches from a csv file given by `path` into a list of MatchData objects. If the file does not exist, return a `FileNotFoundError`.
- `export_matches(matches, path)` - export the list `matches` (of MatchData objects) into a csv file given by `path`. If the path doesn't exist, it's created.
