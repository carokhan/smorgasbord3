from web import app, db, sentry

import pandas as pd


def load_data():
    with app.app_context():
        records = db.session.query(sentry.MatchRecord).all()

    if len(records) == 0:
        return None
    else:
        data = pd.DataFrame(
            [
                (
                    r.teamNumber,
                    r.matchNum,
                    r.notesHighAuto,
                    r.notesHighTele,
                    r.notesLowAuto,
                    r.notesMissedAuto,
                    r.notesMissedTele,
                    r.amp,
                    r.cycles,
                    r.climb,
                    r.trap,
                    r.autoPoints,
                    r.telePoints,
                    r.climbPoints,
                    r.totalPoints,
                    r.present,
                    r.rating,
                )
                for r in records
            ],
            columns=[
                "teamNumber",
                "matchNum",
                "notesHighAuto",
                "notesHighTele",
                "notesLowAuto",
                "notesMissedAuto",
                "notesMissedTele",
                "amp",
                "cycles",
                "climb",
                "trap",
                "autoPoints",
                "telePoints",
                "climbPoints",
                "totalPoints",
                "present",
                "rating",
            ],
        )
        data["autoPointsNormalized"] = (
            data["autoPoints"] / data["autoPoints"].abs().max()
        )
        data["telePointsNormalized"] = (
            data["telePoints"] / data["telePoints"].abs().max()
        )
        data["climbPointsNormalized"] = (
            data["climbPoints"] / data["climbPoints"].abs().max()
        )
        data["ratingNormalized"] = (
            data["rating"] / data["rating"].abs().max()
        )
        data["cyclesNormalized"] = data["cycles"] / data["cycles"].abs().max()

        return data
