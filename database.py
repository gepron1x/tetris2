import sqlite3


class Score:
    def __init__(self, date, level, time, figures_placed):
        self.date = date
        self.level = level
        self.time = time
        self.figures_placed = figures_placed

    def get_date(self):
        return self.date

    def get_level(self):
        return self.level

    def get_time(self):
        return self.time

    def get_figures_placed(self):
        return self.figures_placed


def _construct(rs: tuple):
    return Score(*rs[1::])


class ScoreDatabase:
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection

    def initialize(self):
        cursor = self.connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS scores ("
                       "id INTEGER NOT NULL, "
                       "date TIMESTAMP NOT NULL, "
                       "level VARCHAR(16) NOT NULL, "
                       "time INTEGER NOT NULL, "
                       "figures_placed INTEGER NOT NULL"
                       "PRIMARY KEY(id AUTOINCREMENT)"
                       ")")
        self.connection.commit()

    def save(self, score: Score):
        cursor = self.connection.cursor()
        cursor.execute("INSERT INTO scores (date, level, time, figures_placed) VALUES (?, ?, ?, ?)", (
            score.date,
            score.level,
            score.time,
            score.figures_placed
        ))
        self.connection.commit()

    def load(self, score_id):
        cursor = self.connection.cursor()
        return _construct(cursor.execute("SELECT * FROM scores WHERE id=?", (score_id,)).fetchone())

    def load_all(self):
        cursor = self.connection.cursor()
        return list(map(_construct, cursor.execute("SELECT * FROM scores").fetchall()))






