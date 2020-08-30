import sys
from time import time
import os
import signal
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
    def __init__(self, token, stop_token, db='./app.db', activate_all_modules=True, start_bot=True):
        # private attributes
        self.__cmd_list = {}
        self.__modules = {}
        self.__token = token
        self.__bot = None
        self.__stop_token = stop_token
        # public params
        self.db = DatabaseUtils(db)

        # check db
        if not self.db.table_exists("User"):
            res = self.db.execute_cmd(str_create_user_table)
            if not res:
                LOG.error("Initialization failed! User table not created in DB. Exit.")
                exit(0)
            LOG.info("User table added.")

        # activate modules
        if activate_all_modules:
            self.activate_all_modules()

        # start bot
        if start_bot:
            LOG.info('Bot has been started.')
            self.__bot = telepot.Bot(self.__token)
            MessageLoop(self.__bot, self.message_handler).run_forever()
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
            LOG.info("Command {} removed.".format(command))
        else:
            LOG.warn("Command {} can not be removed: Not found".format(command))
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
        LOG.info("Module {} activated.".format(mod.name))
        return

    def deactivate_module(self, module_name):
        mod = self.__modules[module_name]
        # stop module
        mod.on_stop()
        # remove module's commands
        self.remove_commands(mod.commands)
        # remove module from module list
        self.remove_module_entry(module_name)
        LOG.info("Module {} deactivated.".format(module_name))
        return

    def record_module_entry(self, module_name, module):
        self.__modules[module_name] = module
        LOG.info("Module {} recorded.".format(module_name))
        return

    def remove_module_entry(self, module_name):
        res = self.__modules.pop(module_name, None)
        if res is not None:
            LOG.info("Module {} removed.".format(module_name))
        else:
            LOG.warn("Module {} can not be removed: Not found".format(module_name))
        return

    """db api"""
    def table_exists(self, table_name):
        return self.db.table_exists(table_name)

    def execute_cmd(self, cmd, args=None, fetch_res=False):
        res = self.db.execute_cmd(cmd, args, fetch_res)
        return res

    """statistics"""
    def add_user(self, sender):
        # query user before adding
        query = "SELECT username, firstname, lastname FROM User WHERE id = ?"
        if res := self.execute_cmd(query, (sender['id'],), fetch_res=True):
            LOG.info("User [%s](%d) already registered in DB." % (sender['username'], sender['id']))
            if len(res) > 1:
                LOG.warn("More than one user found by id %d!!" % sender['id'])
            update = \
                """
                UPDATE User 
                SET username = ?, firstname = ?, lastname = ?, language = ?, timestamp = ? 
                WHERE id = ?
                """
            if self.execute_cmd(update, (sender['username'], sender['first_name'], sender['last_name'],
                                         sender['language_code'], int(time()), sender['id'])):
                LOG.info("User status updated in DB.")
            else:
                LOG.error("User status not update in DB.")
            return

        # adding new user
        LOG.info("Adding user [%s](%d) to DB." % (sender['username'], sender['id']))
        cmd = \
            """
            INSERT INTO User
            (id, username, firstname, lastname, language, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
            """
        if self.execute_cmd(cmd, (sender['id'], sender['username'], sender['first_name'], sender['last_name'],
                                  sender['language_code'], int(time()))):
            LOG.info("New user added.")
        else:
            LOG.error("Failed to add user [%s](%d)" % (sender['username'], sender['id']))
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
            LOG.info("New user %s(%d) started using the bot!" % (sender['username'], sender['id']))
            self.add_user(sender)
            return

        # termination
        if msg['text'].startswith('/terminate'):
            if arg == self.__stop_token:
                LOG.info("Terminating bot...")
                self.on_stop()
                LOG.info("Bot has stopped.")
            return

        # dispatch command to module
        LOG.info("Received command [%s] from %s(%d)." % (cmd, sender['username'], sender['id']))
        if mod_name := self.__cmd_list.get(cmd, False):
            try:
                res = self.__modules[mod_name](cmd, arg)
            except Exception as e:
                LOG.error("An error occurred while executing command[%s]!" % cmd)
                LOG.error(e)
            return

    """on stop"""
    def on_stop(self):
        LOG.info("Stopping bot...")
        # close all modules
        modules = list(self.__modules.keys())
        for module in modules:
            self.deactivate_module(module)
        # close db
        self.db.on_stop()
        LOG.flush()
        os.kill(os.getpid(), signal.SIGTERM)


if __name__ == '__main__':
    # create bot
    TOKEN = sys.argv[1]
    STOPP = sys.argv[2]
    bot = BaseBot(TOKEN, STOPP, activate_all_modules=True, start_bot=True)
