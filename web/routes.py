import pandas as pd
from flask import render_template, request
from web.datamanager import load_data
import yaml
import web.graphs as graphs
from web import app
import tbapy
import os
from dotenv import load_dotenv
from datetime import datetime
import time
import statbotics
import config

load_dotenv()

with open(os.path.join(config.BASE_DIR, 'web/data/teams.yaml'), "r") as f:
    teamnames = yaml.load(f, Loader=yaml.Loader)


@app.route("/event")
def event_page():
    data = load_data()
    if data is None:
        context = {"team_list": [], "time": datetime.now().strftime("%H:%M:%S")}
        return render_template("204.html", context=context)

    teams = {}
    for num in list(data["teamNumber"]):
        try:
            teams[int(num)] = teamnames[int(num)]
        except KeyError:
            data = data[data.teamNumber != num]
    team_nums = {name: number for number, name in teams.items()}

    auto_average = round(data["autoPoints"].mean(), 2)
    teleop_average = round(data["telePoints"].mean(), 2)
    climb_average = round(data["climbPoints"].mean(), 2)
    cycles = round(data["cycles"].mean(), 2)
    failure = round(1 - data["present"].mean(), 2)
    matches = data["matchNum"].max()

    graph = graphs.overall_event(data)

    context = {
        "auto_average": auto_average,
        "teleop_average": teleop_average,
        "climb_average": climb_average,
        "cycles": cycles,
        "failure": failure,
        "matches": matches,
        "team_list": sorted(list(teams.values())),
        "team_nums": team_nums,
        "graph": graph,
        "time": datetime.now().strftime("%H:%M:%S"),
    }
    return render_template("event.html", context=context)


@app.route("/team", methods=["POST"])
def team_page():
    data = load_data()

    teams = {}
    for num in list(data["teamNumber"]):
        try:
            teams[int(num)] = teamnames[int(num)]
        except KeyError:
            data = data[data.teamNumber != num]
    team_nums = {name: number for number, name in teams.items()}

    team = request.form["team_name"].split(" ")[0]
    name = teamnames[int(team)]

    lookup = lambda x: data[data.teamNumber == x]
    team_data = lookup(int(team))

    total_avg = round(team_data["totalPoints"].mean(), 2)

    auto_avg = round(team_data["autoPoints"].mean(), 2)
    teleop_avg = round(team_data["telePoints"].mean(), 2)
    climb_avg = round(team_data["climbPoints"].mean(), 2)

    cycle_avg = round(team_data["cycles"].mean(), 2)

    rating = round(team_data["rating"].mean(), 2)
    failure = round(1 - team_data["present"].mean(), 2)

    graph = graphs.by_team(team_data)

    context = {
        "name": name,
        "total_avg": "Average points: " + str(total_avg),
        "auto_avg": auto_avg,
        "teleop_avg": teleop_avg,
        "climb_avg": climb_avg,
        "cycle_avg": cycle_avg,
        "rating": rating,
        "failure": failure,
        "graph": graph,
        "team_list": sorted(list(teams.values())),
        "team_nums": team_nums,
        "time": datetime.now().strftime("%H:%M:%S"),
    }

    return render_template("team.html", context=context)


@app.route("/")
def pit_page():
    data = load_data()
    teams = {}

    try:
        for num in list(data["teamNumber"]):
            try:
                teams[int(num)] = teamnames[int(num)]
            except KeyError:
                data = data[data.teamNumber != num]
        team_nums = {name: number for number, name in teams.items()}
    except TypeError:
        team_nums = {}

    tba = tbapy.TBA(os.environ["TBA_API_KEY"])

    matches = tba.event_matches(config.EVENT_CODE)
    matches = sorted(matches, key=lambda match: 0 if match["predicted_time"] is None else match["predicted_time"])

    current = "END"
    for match in matches:
        if match["actual_time"] is None:
            if match["comp_level"] != "qm":
                current = match["comp_level"] + str(match["match_number"])
            elif match["comp_level"] == "qm":
                current = str(match["match_number"])
            break

    team_matches = tba.team_matches(
        team=int(config.TEAM), event=config.EVENT_CODE, year=int(config.YEAR)
    )
    team_matches = sorted(team_matches, key=lambda match: 0 if match["predicted_time"] is None else match["predicted_time"])[::-1]

    next_team = "END"
    next_color = ""
    next_style = ""
    next_time = 0
    wins = 0
    losses = 0
    ties = 0

    if len(team_matches) == 0:
        record = "0-0-0"

    for match in team_matches:
        if match["actual_time"] is None:
            if match["comp_level"] != "qm":
                next_team = match["comp_level"] + str(match["match_number"])
            elif match["comp_level"] == "qm":
                next_team = str(match["match_number"])

            if "frc" + str(config.TEAM) in match["alliances"]["blue"]["team_keys"]:
                next_color = "Blue in"
                next_style = "; color:dodgerblue"
            elif "frc" + str(config.TEAM) in match["alliances"]["red"]["team_keys"]:
                next_color = "Red in"
                next_style = "; color:crimson"
            else:
                next_color = ""
                next_style = ""

            next_time = round(
                (match["predicted_time"] - time.mktime(datetime.now().timetuple())) / 60
            )

        elif match["actual_time"] is not None:
            win = match["winning_alliance"]
            if win == "":
                ties += 1
            elif "frc" + str(config.TEAM) in match["alliances"][win]["team_keys"]:
                wins += 1
            else:
                losses += 1

        record = str(wins) + "-" + str(losses) + "-" + str(ties)

    upcoming = [match for match in team_matches if match["actual_time"] is None]

    nums = [match["key"].split("_")[-1] for match in upcoming]
    red1 = [match["alliances"]["red"]["team_keys"][0][3:] for match in upcoming]
    red2 = [match["alliances"]["red"]["team_keys"][1][3:] for match in upcoming]
    red3 = [match["alliances"]["red"]["team_keys"][2][3:] for match in upcoming]
    blue1 = [match["alliances"]["blue"]["team_keys"][0][3:] for match in upcoming]
    blue2 = [match["alliances"]["blue"]["team_keys"][1][3:] for match in upcoming]
    blue3 = [match["alliances"]["blue"]["team_keys"][2][3:] for match in upcoming]
    etas = [
        str(
            round(
                (match["predicted_time"] - time.mktime(datetime.now().timetuple())) / 60
            )
        )
        + " min"
        for match in upcoming
    ]

    schedule = {
        "#": nums,
        "Red 1": red1,
        "Red 2": red2,
        "Red 3": red3,
        "Blue 1": blue1,
        "Blue 2": blue2,
        "Blue 3": blue3,
        "ETA": etas,
    }
    table_fields = {
        field: field.split(" ")[0].lower() + field.split(" ")[1]
        for field in list(schedule.keys())
        if "e" in field
    }

    df = pd.DataFrame(schedule)

    context = {
        "current": current,
        "next_team": next_team,
        "next_color": next_color,
        "next_style": next_style,
        "next_time": next_time,
        "record": record,
        "team": str(config.TEAM),
        "columns": df.columns.values,
        "rows": list(df.values.tolist()),
        "table_fields": table_fields,
        "zip": zip,
        "time": datetime.now().strftime("%H:%M:%S"),
        "team_list": sorted(list(teams.values())),
        "team_nums": team_nums,
    }

    return render_template("pit.html", context=context)


@app.route("/playground", methods=["POST"])
def alliance_page():
    data = load_data()

    teams = {}

    if data is not None:
        for num in list(data["teamNumber"]):
            try:
                teams[int(num)] = teamnames[int(num)]
            except KeyError:
                data = data[data.teamNumber != num]
    team_nums = {name: number for number, name in teams.items()}

    red_alliance = [
        request.form["red1"].split(" ")[0],
        request.form["red2"].split(" ")[0],
        request.form["red3"].split(" ")[0],
    ]

    blue_alliance = [
        request.form["blue1"].split(" ")[0],
        request.form["blue2"].split(" ")[0],
        request.form["blue3"].split(" ")[0],
    ]

    sb = statbotics.Statbotics()

    redEPA = sum(
        [
            sb.get_team_year(int(team), int(config.YEAR), ["epa_end"])["epa_end"]
            for team in red_alliance
        ]
    )
    blueEPA = sum(
        [
            sb.get_team_year(int(team), int(config.YEAR), ["epa_end"])["epa_end"]
            for team in blue_alliance
        ]
    )

    red_score = round(redEPA * 1.065)
    blue_score = round(blueEPA * 1.065)

    percentage = round(
        100
        / (
            1
            + 10
            ** (
                (-5 / 8 * (redEPA - blueEPA))
                / sb.get_year(int(config.YEAR), ["score_sd"])["score_sd"]
            )
        ),
        2,
    )

    if percentage < 50:
        percentage = 100 - percentage

    if data is not None:
        lookup = lambda x: data[data.teamNumber == x]
        red_dfs = [lookup(int(team)) for team in red_alliance]
        blue_dfs = [lookup(int(team)) for team in blue_alliance]

        try:
            graph = graphs.alliance_graph(red_dfs, blue_dfs)
        except ValueError:
            graph = None
    else:
        red_dfs = None
        blue_dfs = None
        graph = None

    context = {
        "red1": red_alliance[0],
        "red2": red_alliance[1],
        "red3": red_alliance[2],
        "blue1": blue_alliance[0],
        "blue2": blue_alliance[1],
        "blue3": blue_alliance[2],
        "red_score": red_score,
        "blue_score": blue_score,
        "percentage": percentage,
        "time": datetime.now().strftime("%H:%M:%S"),
        "team_list": sorted(list(teams.values())),
        "team_nums": team_nums,
        "graph": graph,
    }

    return render_template("alliances.html", context=context)
