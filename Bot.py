import sys
from time import sleep
import telepot
from telepot.loop import MessageLoop
from Database import DatabaseUtils
from Modules import Currency
from Log import Logger
LOG = Logger('./log', 'bot')
MODULES = [Currency]


class BaseBot:
    def __init__(self, token, db='./app.db'):
        # attributes
        self.cmd_list = {}
        self.modules = {}
        self.db = DatabaseUtils(db)

        # start bot
        LOG.add_log('Initializing Bot...')
        self.bot = telepot.Bot(token)
        MessageLoop(self.bot, self.message_handler).run_as_thread()
        LOG.add_log('Bot has been started.')
        return

    """commands registration"""
    def register_commands(self, module_name, commands):
        for command in commands:
            self.register_command(module_name, command)
        return

    def register_command(self, module_name, command):
        self.cmd_list[command] = module_name
        return

    def remove_commands(self, commands):
        for command in commands:
            self.remove_command(command)
        return

    def remove_command(self, command):
        res = self.cmd_list.pop(command, None)
        if res is not None:
            LOG.add_log("Command {} removed.".format(command))
        else:
            LOG.add_log("Command {} can not be removed: Not found".format(command), mode='WARN')
        return

    """modules"""
    def activate_all_modules(self):
        for m in MODULES:
            # register modules
            self.activate_module(m)
        return

    def activate_module(self, module):
        mod = module.Module(self)
        # initialize module
        mod.initialize()
        # add module to module list
        self.record_module_entry(mod.name, mod)
        # add module's commands
        self.register_commands(mod.name, mod.commands)
        LOG.add_log("Module {} activated.".format(mod.name))
        return

    def deactivate_module(self, module_name):
        mod = self.modules[module_name]
        # stop module
        mod.on_stop()
        # remove module's commands
        self.remove_commands(mod.commands)
        # remove module from module list
        self.remove_module_entry(module_name)
        LOG.add_log("Module {} deactivated.".format(module_name))
        return

    def record_module_entry(self, module_name, module):
        self.modules[module_name] = module
        LOG.add_log("Module {} recorded.".format(module_name))
        return

    def remove_module_entry(self, module_name):
        res = self.modules.pop(module_name, None)
        if res is not None:
            LOG.add_log("Module {} removed.".format(module_name))
        else:
            LOG.add_log("Module {} can not be removed: Not found".format(module_name), mode='WARN')
        return

    """db api"""
    def table_exists(self, table_name):
        return self.db.table_exists(table_name)

    def execute_cmd(self, cmd):
        self.db.execute_cmd(cmd)
        return

    """msg handler"""
    def message_handler(self, msg):
        return

    """on stop"""
    def on_stop(self):
        LOG.add_log("Stopping bot...")
        # close all modules
        modules = list(self.modules.keys())
        for module in modules:
            self.deactivate_module(module)
        # close db
        self.db.on_stop()
        LOG.flush()
        return


if __name__ == '__main__':
    TOKEN = sys.argv[1]
    bot = BaseBot(TOKEN)
    bot.activate_all_modules()
    try:
        while True:
            sleep(10)
    except KeyboardInterrupt as e:
        bot.on_stop()
