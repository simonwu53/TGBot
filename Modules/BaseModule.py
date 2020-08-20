class Module:
    def __init__(self, master):
        self.name = None   # "name"
        self.commands = []   # ["\command", ...]
        self.master = master
        return

    def initialize(self):
        return

    def __call__(self, cmd):
        return

    def on_stop(self):
        return
