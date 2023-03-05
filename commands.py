import os
from addict import Dict
from chatgpt import ChatGPT


class ChatGPTCommand(object):

    CMD_PREFIX = "_cmd_"

    def __init__(self, chatgpt: ChatGPT, config: Dict):
        self.chatgpt = chatgpt
        self.config = config
        self.cmds = self.init_commands()
        self._cmd_help()

    def init_commands(self):
        cmds = {}
        for attr in dir(self):
            if attr.startswith(ChatGPTCommand.CMD_PREFIX):
                cmd = attr[len(ChatGPTCommand.CMD_PREFIX):]
                cmds[cmd] = getattr(self, attr)
        
        return cmds
    
    def __call__(self, cmd, args):
        fn = getattr(self, f"{ChatGPTCommand.CMD_PREFIX}{cmd}")
        return fn(*args)

    def _cmd_help(self):
        """ show this document
        """
        print("Command List: ")
        for cmd, fn in self.cmds.items():
            doc = fn.__doc__.strip() if fn.__doc__ else ""
            print(f"\t[{cmd}]: {doc}")

    def _cmd_new(self):
        """ create a new session
        """
        self.chatgpt.new_session()

    def _cmd_save(self):
        """ save current session
        """
        self.chatgpt.current_session.save(self.config.save.root)

    def _cmd_his(self):
        """ show history of current session
        """
        sess = self.chatgpt.current_session
        for _id, msg in enumerate(sess.history):
            print(f"<{msg.role}>: {msg.content}")

    def _cmd_ls(self):
        """ list all saved sessions
        """
        sessions = os.listdir(self.config.save.root)
        session_ids = [sess.split(".")[0] for sess in sessions if sess.endswith(".json")]
        for _id in session_ids:
            print(_id)

    def _cmd_resume(self, sess_id):
        """ resume specific session with session id
        """
        self.chatgpt.resume_session(sess_id)