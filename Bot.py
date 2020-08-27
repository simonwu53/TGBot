import sys
from time import sleep, time
import telepot
from telepot.loop import MessageLoop
from Database import DatabaseUtils
from Modules import Currency
from Log import Logger

LOG = Logger('./log', 'bot')
MODULES = [Currency]
str_create_user_table = """
    CREATE TABLE User (
        id integer PRIMARY KEY,
        username text,
        firstname text,
        lastname text,
        language text NOT NULL,
        timestamp text NOT NULL)"""


"""
{'message_id': 5, 
 'from': {'id': 592685641, 'is_bot': False, 'first_name': 'Shan', 'last_name': 'Wu', 
          'username': 'big533', 'language_code': 'en'}, 
 'chat': {'id': 592685641, 'first_name': 'Shan', 'last_name': 'Wu', 'username': 'big533', 'type': 'private'}, 
 'date': 1597950931, 
 'text': '/currency 1 w e', 
 'entities': [{'offset': 0, 'length': 9, 'type': 'bot_command'}]}
"""


class BaseBot:
    def __init__(self, token, db='./app.db'):
        # private attributes
        self.__cmd_list = {}
        self.__modules = {}
        # public params
        self.db = DatabaseUtils(db)

        # check db
        if not self.db.table_exists("User"):
            res = self.db.execute_cmd(str_create_user_table)
            if not res:
                LOG.add_log("Initialization failed! User table not created in DB. Exit.", 'ERROR')
                exit(0)
            LOG.add_log("User table added.")

        # start bot
        LOG.add_log('Initializing Bot...')
        self.__bot = telepot.Bot(token)
        MessageLoop(self.__bot, self.message_handler).run_as_thread()
        LOG.add_log('Bot has been started.')
        return

    """commands registration"""
    def register_commands(self, module_name, commands):
        for command in commands:
            self.register_command(module_name, command)
        return

    def register_command(self, module_name, command):
        self.__cmd_list[command] = module_name
        return

    def remove_commands(self, commands):
        for command in commands:
            self.remove_command(command)
        return

    def remove_command(self, command):
        res = self.__cmd_list.pop(command, None)
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
        mod = self.__modules[module_name]
        # stop module
        mod.on_stop()
        # remove module's commands
        self.remove_commands(mod.commands)
        # remove module from module list
        self.remove_module_entry(module_name)
        LOG.add_log("Module {} deactivated.".format(module_name))
        return

    def record_module_entry(self, module_name, module):
        self.__modules[module_name] = module
        LOG.add_log("Module {} recorded.".format(module_name))
        return

    def remove_module_entry(self, module_name):
        res = self.__modules.pop(module_name, None)
        if res is not None:
            LOG.add_log("Module {} removed.".format(module_name))
        else:
            LOG.add_log("Module {} can not be removed: Not found".format(module_name), mode='WARN')
        return

    """db api"""
    def table_exists(self, table_name):
        return self.db.table_exists(table_name)

    def execute_cmd(self, cmd, args=None):
        res = self.db.execute_cmd(cmd, args)
        return res

    """statistics"""
    def add_user(self, sender):
        LOG.add_log("Adding user [%s](%d) to DB." % (sender['username'], sender['id']))
        cmd = \
            """
            INSERT INTO User
            (id, username, firstname, lastname, language, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
            """
        res = self.execute_cmd(cmd, (sender['id'], sender['username'], sender['first_name'], sender['last_time'],
                                     sender['language_code'], int(time())))
        if not res:
            LOG.add_log("Failed to add user [%s](%d)" % (sender['username'], sender['id']), 'ERROR')
        return

    """msg handler"""
    def message_handler(self, msg):
        print(msg)
        # extract command
        msg_split = msg['text'].split(' ')
        cmd = msg_split[0]
        arg = ' '.join(msg_split[1:])
        sender = msg['from']
        # content_type, chat_type, chat_id = telepot.glance(msg)

        # welcome
        if msg['text'].startswith('/start'):
            LOG.add_log("New user %s(%d) started using the bot!" % (sender['username'], sender['id']))
            self.add_user(sender)
            return

        # dispatch command to module
        LOG.add_log("Received command [%s] from %s(%d)." % (cmd, sender['username'], sender['id']))
        if mod_name := self.__cmd_list.get(cmd, False):
            res = self.__modules[mod_name](cmd, arg)
            
        return

    """on stop"""
    def on_stop(self):
        LOG.add_log("Stopping bot...")
        # close all modules
        modules = list(self.__modules.keys())
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
