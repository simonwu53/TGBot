from .BaseModule import Base
from typing import Optional


# date format  ISO8601 strings "YYYY-MM-DD HH:MM:SS.SSS"
str_create_currency_table = """
    CREATE TABLE Currency (
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
        return

    def initialize(self):
        # register resources
        if not self.master.table_exists('Currency'):
            res = self.master.execute_cmd(str_create_currency_table)
            if not res:
                self.log_error("Initialization failed! Currency table not created in DB. Exit.")
                return
            self.log_info("Currency table initialized.")
        return

    def __call__(self, cmd: str, arg: Optional[str] = None) -> bool:
        self.LOG.add_log("Received cmd: %s. arg: %s." % (cmd, arg))
        return True

    def on_stop(self):
        # stop tasks
        # add here
        self.log_info("Module {} stopped.".format(self.name))
        self.LOG.flush()
        return
