import os
import openai
import argparse
import json
import random
import string

import logging
from addict import Dict
from collections import defaultdict
from message import Message
from enum import Enum
import datetime


LOG_LEVEL = {
    "INFO": logging.INFO,
    "DEBUG": logging.DEBUG
}

# init logger
def init_logger():
    logger = logging.getLogger('chatgpt')

    level = os.getenv("CHATGPT_LOG_LEVEL", "INFO")
    logger.setLevel(LOG_LEVEL[level])

    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


logger = init_logger()


def generate_random_string(length=8):
    # 生成长度为 length 的随机字符串
    letters_and_digits = string.ascii_lowercase + string.digits
    rand_string = ''.join((random.choice(letters_and_digits) for i in range(length)))
    return rand_string


def generate_datetime_str():
    now = datetime.datetime.now()
    formatted_time = now.strftime("%Y%m%d_%H:%M:%S")
    return formatted_time


class ChatGPTRole(Enum):
    SYSTEM = 0
    ASSISTANT = 1
    USER = 2


def auto_save(fn):

    def wrap(self, *args, **kwargs):
        if self.save_mode == "auto":
            self.save(verbose=False)
            logger.debug(f"session({self.session_id}) saved")
        fn(self, *args, **kwargs)
    return wrap


DEFAULT_SYSTEM_PROMPTS = "You are a helpful assistant."


class ChatSession(object):

    def __init__(self, 
            session_id, 
            session_name,
            chatgpt,
            create_time,
            system=DEFAULT_SYSTEM_PROMPTS, 
            history=None
        ):

        self.session_id = session_id
        self.session_name = session_name
        self.model = chatgpt.model
        self.engine = chatgpt.engine
        self.system = system
        self.create_time = create_time
        self.max_history = chatgpt.max_history
        self.history = history or []

        for i, his in enumerate(self.history):
            if not isinstance(his, Message):
                self.history[i] = Message.from_dict(self.history[i])

    def chat(self, user_input: str) -> Message:

        # init with system prompt
        messages = [dict(role="system", content=self.system)]

        # add history context
        history = self.history[-self.max_history:]
        messages += [msg.to_dict() for msg in history]
        
        # add user input
        cur_msg = Message(role="user", content=user_input)
        messages.append(cur_msg.to_dict())
        
        # parse response
        try:
            # call openai api
            logger.debug(f"model: {self.model}")
            logger.debug(f"engine: {self.engine}")
            for msg in messages:
                logger.debug(msg)
            completion = openai.ChatCompletion.create(
                engine=self.engine,
                model=self.model,
                messages=messages
            )
            
            ret = completion.choices[0].message
            response_msg = Message(role=ret.role, content=ret.content)
            self.history.extend([cur_msg, response_msg])
            return response_msg
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Message(role="system", content=f"system error: {e}")

    @property
    def id(self):
        return self.session_id

    @property
    def name(self):
        return self.session_name or f"Untitled"

    def set_session_name(self, session_name):
        """ set session name
        """
        self.session_name = session_name

    def set_max_history(self, max_history):
        self.max_history = max_history

    def set_system(self, system):
        """ set session name
        """
        self.system = system
        logging.info(f"[System] - {self.id}: update system='{self.system}'")

    def __repr__(self) -> str:
        return \
        f"""ChatGPTSession(
        id='{self.session_id}', 
        name={self.name}, 
        model={self.model}, 
        system='{self.system}', 
        history={len(self.history)},
        max_history={self.max_history}
        )
        """
        
    def save(self, save_root, verbose=False):
        
        save_obj = dict(
            session_id=self.session_id,
            session_name=self.session_name,
            create_time=self.create_time,
            system=self.system,
            history=[msg.to_dict() for msg in self.history]
        )
        
        os.makedirs(save_root, exist_ok=True)
        save_path = os.path.join(save_root, f"{self.session_id}.json")
        json.dump(save_obj, open(save_path, "w"), ensure_ascii=False, indent=4)
        if verbose:
            logger.info(f"[System] Your session-{self.session_id} has been saved to: {save_path}")

    @staticmethod
    def resume_from_file(chatgpt, ckpt):
        save_obj = json.load(open(ckpt))
        return ChatSession(
            session_id=save_obj["session_id"], 
            session_name=save_obj.get("session_name", None),
            chatgpt=chatgpt,
            create_time=save_obj["create_time"],
            system=save_obj.get("system", DEFAULT_SYSTEM_PROMPTS), 
            history=save_obj["history"],
        )


class ChatGPT(object):

    def __init__(self, 
            config, 
            model="gpt-3.5-turbo", 
            init_system="assistant",
            max_history=10,
            save_root=None,
            save_mode="auto"
        ):
        self.model = model
        self.engine = config.get("engine", None)
        self.auth(**config)
        self.init_system = init_system
        self.session_pool = defaultdict(dict)
        self.save_mode = save_mode
        self.save_root = save_root
        self.max_history = max_history
        self.resume_sessions()
        
    def auth(self, api_key, api_type="openai", api_base=None, api_version="2023-03-15-preview", **kwargs):
        if api_type == "azure":
            openai.api_type = "azure"
            openai.api_base = api_base
            openai.api_version = api_version
        openai.api_key = api_key

    def new_session(self, user):
        logger.info("You have started a new chat session")
        session_id = generate_random_string(length=8)
        new_session = ChatSession(
            session_id, 
            session_name=None,
            chatgpt=self,
            create_time=generate_datetime_str(),
            system=DEFAULT_SYSTEM_PROMPTS
        )
        self.session_pool[user][session_id] = new_session
        return new_session

    def resume_sessions(self):
        
        # resume session
        for user in os.listdir(self.save_root):
            logger.info(f"[System] Resuming session for '{user}'")
            user_root = os.path.join(self.save_root, user)
            for sess in os.listdir(user_root):
                path = os.path.join(user_root, sess) 
                session_id = os.path.basename(path).split(".")[0]

                logger.info(f"[System] Resuming session from {path}")
                self.session_pool[user][session_id] = ChatSession.resume_from_file(self, path)

    def get_session(self, user, session_id=None):
        if session_id is None:
            latest_session_time = "19000101"
            latest_session = None
            for sess in self.session_pool[user].values():
                if sess.create_time > latest_session_time:
                    latest_session_time = sess.create_time
                    latest_session = sess
            
            if latest_session is None:
                return self.new_session(user)
            return latest_session

        return self.session_pool[user][session_id]

    def save(self, verbose=True):
        """ save current session
        """
        for user, sessions in self.session_pool.items():
            for session in sessions.values():
                save_root = os.path.join(self.save_root, user)
                session.save(save_root, verbose=verbose)
