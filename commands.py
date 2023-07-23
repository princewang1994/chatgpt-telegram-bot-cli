import os
from addict import Dict
from chatgpt import ChatGPT, ChatSession


class ChatGPTCommand(object):

    CMD_PREFIX = "_cmd_"

    def __init__(self, chatgpt, init_session, user, config: Dict):
        self.chatgpt = chatgpt
        self.user = user
        self.session = init_session
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
        new_session = self.chatgpt.new_session(self.user)
        self.session = new_session

    def _cmd_save(self):
        """ save current session
        """
        self.chatgpt.current_session.save(verbose=True)

    def _cmd_his(self):
        """ show history of current session
        """
        sess = self.session
        for _id, msg in enumerate(sess.history):
            print(f"<{msg.role}>: {msg.content}")

    def _cmd_list(self):
        """ list all saved sessions
        """
        
        sessions = self.chatgpt.session_pool[self.user]

        for idx, sess in enumerate(sessions.values()):
            
            s = f"{idx}.[{sess.session_id}]: {sess.name}"
            if sess.id == self.session.id:
                s += " ← current"
            print(s)

    def _cmd_ch(self, sess_id):
        """ resume(change) specific session with session id
        """
        self.session = self.chatgpt.get_session(self.user, sess_id)

    def _cmd_rename(self, session_name):
        """ rename current session
        """
        self.session.set_session_name(session_name)
    
    def _cmd_sys(self, system):
        """ update system prompt
        """
        self.session.set_system(system)

    def _cmd_info(self):
        """ show current session info
        """
        print(self.session)

    def _cmd_max(self, max_history):
        """ set max history
        """
        self.session.set_max_history(int(max_history))