from web import app, db

import json
import time
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import os
import config


class MatchRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    teamNumber = db.Column(db.String(5), nullable=False)
    matchNum = db.Column(db.Integer, nullable=False)
    notesHighAuto = db.Column(db.Integer, nullable=False)
    notesHighTele = db.Column(db.Integer, nullable=False)
    notesLowAuto = db.Column(db.Integer, nullable=False)
    notesMissedAuto = db.Column(db.Integer, nullable=False)
    notesMissedTele = db.Column(db.Integer, nullable=False)
    amp = db.Column(db.Integer, nullable=False)
    cycles = db.Column(db.Integer, nullable=False)
    climb = db.Column(db.String(32), nullable=False)
    trap = db.Column(db.Boolean, nullable=False)
    autoPoints = db.Column(db.Integer, nullable=False)
    telePoints = db.Column(db.Integer, nullable=False)
    climbPoints = db.Column(db.Integer, nullable=False)
    totalPoints = db.Column(db.Integer, nullable=False)
    present = db.Column(db.Boolean, nullable=False)
    rating = db.Column(db.Integer, nullable=False)

    def __init__(
        self,
        teamNumber,
        matchNum,
        notesHighAuto,
        notesHighTele,
        notesLowAuto,
        notesMissedAuto,
        notesMissedTele,
        amp,
        cycles,
        climb,
        trap,
        autoPoints,
        telePoints,
        climbPoints,
        totalPoints,
        present,
        rating,
    ):
        self.teamNumber = teamNumber
        self.matchNum = matchNum
        self.notesHighAuto = notesHighAuto
        self.notesHighTele = notesHighTele
        self.notesLowAuto = notesLowAuto
        self.notesMissedAuto = notesMissedAuto
        self.notesMissedTele = notesMissedTele
        self.amp = amp
        self.cycles = cycles
        self.climb = climb
        self.trap = trap
        self.autoPoints = autoPoints
        self.telePoints = telePoints
        self.climbPoints = climbPoints
        self.totalPoints = totalPoints
        self.present = present
        self.rating = rating
        self.data = (
            teamNumber,
            matchNum,
            notesHighAuto,
            notesHighTele,
            notesLowAuto,
            notesMissedAuto,
            notesMissedTele,
            amp,
            cycles,
            climb,
            trap,
            autoPoints,
            telePoints,
            climbPoints,
            totalPoints,
            present,
            rating,
        )

    def __repr__(self):
        return str(
            (
                self.teamNumber,
                self.matchNum,
                self.notesHighAuto,
                self.notesHighTele,
                self.notesLowAuto,
                self.notesMissedAuto,
                self.notesMissedTele,
                self.amp,
                self.cycles,
                self.climb,
                self.trap,
                self.autoPoints,
                self.telePoints,
                self.climbPoints,
                self.totalPoints,
                self.present,
                self.rating,
            )
        )


present = lambda state: False if state == "Did not show" else False
climb = lambda state: 0 if state == "Did not hang" else 3
trap = lambda state: 0 if state == "false" else 5


def on_created(event):
    try:
        with open(event.src_path, "r") as f:
            data = json.load(f)
    except PermissionError:
        time.sleep(3)
        with open(event.src_path, "r") as f:
            data = json.load(f)
    with app.app_context():
        db.session.add_all(
            [
                MatchRecord(
                    teamNumber=record["teamNumber"],
                    matchNum=int(record["matchNumber"]),
                    notesHighAuto=int(record["notesHighAuto"]),
                    notesHighTele=int(record["notesHighTeleop"]),
                    notesLowAuto=int(record["notesLowAuto"]),
                    notesMissedAuto=int(record["notesMissedAuto"]),
                    notesMissedTele=int(record["notesMissedTeleop"]),
                    amp=int(record["amplify"]),
                    cycles=int(record["notesHighAuto"])
                    + int(record["notesHighTeleop"])
                    + int(record["notesLowAuto"])
                    + int(record["amplify"]),
                    climb=record["hangState"],
                    trap=bool(trap(record["didTrap"])),
                    autoPoints=(
                        5 * int(record["notesHighAuto"])
                        + 2 * int(record["notesLowAuto"])
                    ),
                    telePoints=(
                        2 * int(record["notesHighTeleop"]) + int(record["amplify"])
                    ),
                    climbPoints=(climb(record["hangState"]) + trap(record["didTrap"])),
                    totalPoints=(
                        5 * int(record["notesHighAuto"])
                        + 2 * int(record["notesLowAuto"])
                        + (2 * int(record["notesHighTeleop"]) + int(record["amplify"]))
                        + (climb(record["hangState"]) + trap(record["didTrap"]))
                    ),
                    present=present(record["robotState"]),
                    rating=int(record["rating"]),
                )
                for record in data["root"]
            ]
        )

        db.session.commit()


def watchman():
    patterns = ["*.json"]
    ignore_patterns = None
    ignore_directories = None
    case_sensitive = True
    handler = PatternMatchingEventHandler(
        patterns, ignore_patterns, ignore_directories, case_sensitive
    )

    handler.on_created = on_created

    path = os.path.join(config.BASE_DIR, "web/data/")
    recurse = False
    observer = Observer()
    observer.schedule(handler, path, recursive=recurse)

    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        observer.join()
