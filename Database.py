import sqlite3
from Log import Logger
LOG = Logger('./log', 'database')

# Strings
str_query_tables = "SELECT name FROM sqlite_master WHERE type='table'"


# Database instance
class DatabaseUtils:
    def __init__(self, db='./app.db'):

        LOG.add_log('Connecting to database: {}'.format(db))
        self.con = self.connect_db(db)
        self.cur = self.con.cursor()
        LOG.add_log('Database connected.')
        return

    def table_exists(self, table_name):
        self.cur.execute(str_query_tables)
        tables = self.cur.fetchall()
        if (table_name,) in tables:
            return 1
        else:
            return 0

    def execute_cmd(self, cmd):
        self.cur.execute(cmd)
        self.con.commit()
        return

    @staticmethod
    def connect_db(db=None):
        return sqlite3.connect(db)

    def on_stop(self):
        self.con.close()
        LOG.add_log("Database disconnected.")
        LOG.flush()
        return
