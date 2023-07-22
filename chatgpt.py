import os
import openai
import argparse
import json
import random
import string

import logging
from addict import Dict
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


SYSTEM_PROMPTS = {
    "assistant": "You are a helpful assistant.",
}


class ChatSession(object):

    def __init__(self, 
            session_id, 
            session_name=None, 
            model="gpt-3.5-turbo", 
            engine=None,
            system=SYSTEM_PROMPTS["assistant"], 
            max_history=10, 
            history=None,
            save_root=None,
            save_mode="auto"
        ):

        self.session_id = session_id
        self.session_name = session_name
        self.model = model
        self.engine = engine
        self.system = system
        self.max_history = max_history
        self.history = history or []
        self.save_root = save_root
        self.save_mode = save_mode

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
            return None

    @property
    def id(self):
        return self.session_id

    @property
    def name(self):
        return self.session_name or f"Untitled"

    @auto_save
    def set_session_name(self, session_name):
        """ set session name
        """
        self.session_name = session_name

    @auto_save
    def set_max_history(self, max_history):
        self.max_history = max_history

    @auto_save
    def set_system(self, system):
        """ set session name
        """
        if system in SYSTEM_PROMPTS:
            self.system = SYSTEM_PROMPTS[system]
        else:
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
        
    def save(self, verbose=False):
        save_obj = dict(
            session_id=self.session_id,
            session_name=self.session_name,
            model=self.model,
            engine=self.engine,
            time=generate_datetime_str(),
            system=self.system,
            max_history=self.max_history,
            history=[msg.to_dict() for msg in self.history]
        )
        save_path = os.path.join(self.save_root, f"{self.session_id}.json")
        json.dump(save_obj, open(save_path, "w"), ensure_ascii=False, indent=4)
        if verbose:
            logger.info(f"[System] Your session-{self.session_id} has been saved to: {save_path}")

    @staticmethod
    def resume_from_file(ckpt, save_root=None, save_mode=None):
        save_obj = json.load(open(ckpt))
        return ChatSession(
            session_id=save_obj["session_id"], 
            session_name=save_obj.get("session_name", None),
            model=save_obj.get("model", "gpt-3.5-turbo"), 
            engine=save_obj.get("engine", None),
            system=save_obj.get("system", SYSTEM_PROMPTS["assistant"]), 
            max_history=save_obj.get("max_history", 10),
            history=save_obj["history"],
            save_root=save_root,
            save_mode=save_mode,
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
        self.model_name = model
        self.engine = config.get("engine", None)
        self.auth(**config)
        self.init_system = init_system
        self.current_session = None
        self.save_mode = save_mode
        self.save_root = save_root
        self.max_history = max_history
        
    def auth(self, api_key, api_type="openai", api_base=None, api_version="2023-03-15-preview", **kwargs):
        if api_type == "azure":
            openai.api_type = "azure"
            openai.api_base = api_base
            openai.api_version = api_version
        openai.api_key = api_key

    def new_session(self):
        if self.current_session:
            self.current_session.save()
        logger.info("You have started a new chat session")
        session_id = generate_random_string(length=8)
        self.current_session = ChatSession(
            session_id, 
            session_name=None,
            model=self.model_name, 
            engine=self.engine,
            system=SYSTEM_PROMPTS[self.init_system],
            max_history=self.max_history,
            save_mode=self.save_mode,
            save_root=self.save_root
        )
        self.current_session.save()
        return self.current_session.session_id

    def resume_session(self, session_id=None):
        # save current session
        if self.current_session:
            self.save()
        
        # resume session
        if session_id:
            session_file = os.path.join(self.save_root, f"{session_id}.json")
        else:
            latest_sess = None
            for sess in os.listdir(self.save_root):
                path = os.path.join(self.save_root, sess)
                session_content = json.load(open(path))
                save_time = session_content["time"]
                if latest_sess is None or save_time > latest_sess:
                    latest_sess = path
            session_file = latest_sess
            if not latest_sess:
                logger.info("[System] There is no saved session, create a new one.")
                self.new_session()
                return
            
            session_id = os.path.basename(session_file).split(".")[0]

        logger.info(f"[System] Resuming session from {session_id}")
        self.current_session = ChatSession.resume_from_file(session_file, save_root=self.save_root, save_mode=self.save_mode)

    def chat(self, user_input: str):
        resp = self.current_session.chat(user_input)
        if self.save_mode == "auto":
            self.current_session.save()
        return resp

    def save(self, verbose=True):
        """ save current session
        """
        if self.save_root and self.current_session:
            self.current_session.save(verbose=verbose)
