import sqlite3
from Log import Logger
LOG = Logger('./log', 'database')

# Strings
str_query_tables = "SELECT name FROM sqlite_master WHERE type='table'"


# Database instance
class DatabaseUtils:
    def __init__(self, db='./app.db'):

        LOG.info('Connecting to database: {}'.format(db))
        self.con = self.connect_db(db)
        self.cur = self.con.cursor()
        LOG.info('Database connected.')
        return

    def table_exists(self, table_name):
        self.cur.execute(str_query_tables)
        tables = self.cur.fetchall()
        if (table_name,) in tables:
            return 1
        else:
            return 0

    def execute_cmd(self, cmd, args=None, fetch_res=False):
        flag = 0
        try:
            self.cur.execute(cmd, args)
            self.con.commit()
            flag = 1
        except sqlite3.OperationalError as e:
            LOG.error("DB failed to execute the command: %s" % cmd)

        if fetch_res:
            return self.cur.fetchall()
        else:
            return flag

    @staticmethod
    def connect_db(db=None):
        return sqlite3.connect(db)

    def on_stop(self):
        self.con.close()
        LOG.info("Database disconnected.")
        LOG.flush()
        return
