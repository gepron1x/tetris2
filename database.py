
class ScoreDatabase:
    def __init__(self, connection):
        self.connection = connection

    def initialize(self):
        cursor = self.connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS scores ("
                       "id INTEGER NOT NULL, "
                       "date TIMESTAMP NOT NULL, "
                       "level VARCHAR(16) NOT NULL, "
                       "time INTEGER NOT NULL, "
                       "PRIMARY KEY(id AUTOINCREMENT)"
                       ")")
        self.connection.commit()


