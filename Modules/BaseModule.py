from typing import Optional
from Log import Logger


class Base:
    def __init__(self, master):
        self.name = None   # "name"
        self.commands = []   # ["\command", ...]
        self.master = master
        self.LOG = Logger('./log', 'plugins')
        return

    def initialize(self):
        return

    def __call__(self, cmd: str, arg: Optional[str] = None) -> bool:

        return False

    def on_stop(self):
        return

    def add_log(self, msg, mode='INFO'):
        self.LOG.add_log("[%s]: %s" % (self.name, msg), mode)
        return
