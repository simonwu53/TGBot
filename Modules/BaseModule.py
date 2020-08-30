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

    def log_info(self, msg):
        self.LOG.info("[%s]: %s" % (self.name, msg))
        return

    def log_warn(self, msg):
        self.LOG.warn("[%s]: %s" % (self.name, msg))
        return

    def log_error(self, msg):
        self.LOG.error("[%s]: %s" % (self.name, msg))
        return
