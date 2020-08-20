from .BaseModule import Module as Base
from Log import Logger


# date format  ISO8601 strings "YYYY-MM-DD HH:MM:SS.SSS"
str_create_currency_table = """
    CREATE TABLE currency (
        id integer PRIMARY KEY,
        label_ZH text NOT NULL,
        label_EN text NOT NULL,
        exchange_buy float NOT NULL,
        cash_buy float NOT NULL,
        exchange_sell float NOT NULL,
        cash_sell float NOT NULL,
        datetime date NOT NULL)"""


class Module(Base):
    def __init__(self, master):
        super(Module, self).__init__(master)
        self.name = "Currency"   # "name"
        self.commands = ["/currency", ]   # "\command"
        self.LOG = Logger('./log', 'module-currency')
        return

    def initialize(self):
        # register resources
        if not self.master.table_exists('currency'):
            self.master.execute_cmd(str_create_currency_table)
            self.LOG.add_log("Table initialized.")
        return

    def __call__(self, cmd):

        return

    def on_stop(self):
        # stop tasks
        # add here
        self.LOG.add_log("Module {} stopped.".format(self.name))
        self.LOG.flush()
        return
