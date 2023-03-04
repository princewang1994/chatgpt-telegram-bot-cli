import os
from addict import Dict
from chatgpt import ChatGPT


class ChatGPTCommand(object):

    CMD_PREFIX = "_cmd_"

    def __init__(self, chatgpt: ChatGPT, config: Dict):
        self.chatgpt = chatgpt
        self.config = config
        self.cmd_list = self.init_commands()

    def init_commands(self):
        cmd_list = []
        for attr in dir(self):
            if attr.startswith(ChatGPTCommand.CMD_PREFIX):
                cmd_list.append(attr[len(ChatGPTCommand.CMD_PREFIX):])
        print("Command List: ", cmd_list)
        return cmd_list
    
    def __call__(self, cmd, args):
        fn = getattr(self, f"{ChatGPTCommand.CMD_PREFIX}{cmd}")
        return fn(*args)

    def _cmd_new(self):
        self.chagpt.new_session()

    def _cmd_save(self):
        self.chatgpt.current_session.save(self.config.save.root)

    def _cmd_history(self):
        sess = self.chatgpt.current_session
        for msg in sess.history:
            print(msg)

    def _cmd_ls(self):
        """ list all saved sessions
        """
        sessions = os.listdir(self.config.save.root)
        session_ids = [sess.split(".")[0] for sess in sessions if sess.endswith(".json")]
        for _id in session_ids:
            print(_id)

    def _cmd_resume(self, sess_id):
        pass