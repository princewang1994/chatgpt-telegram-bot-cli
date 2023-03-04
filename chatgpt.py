import os
import openai
import argparse
import json
import random

from addict import Dict
from message import Message
from enum import Enum
import datetime


import random
import string

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


SYSTEM_PROMPTS = {
    "helpful_assistant": Message(role="system", content="You are a helpful assistant."),
}


class ChatSession(object):

    def __init__(self, session_id, model, sys_prompt, max_history=10, history=None):
        self.sys_prompt = sys_prompt
        self.model = model
        self.session_id = session_id
        self.max_history = max_history
        self.history = []
        for i, his in enumerate(self.history):
            if isinstance(his, Message):
                self.history[i] = Message.from_dict(self.history[i])

    def chat(self, user_input: str):
        # init with system prompt
        messages = [self.sys_prompt.to_dict()]

        # add history context
        history = self.history[-self.max_history:]
        messages += [msg.to_dict() for msg in history]
        
        # add user input
        cur_msg = Message(role="user", content=user_input)
        messages.append(cur_msg.to_dict())
        
        # call openai api
        completion = openai.ChatCompletion.create(
            model=self.model,
            messages=messages
        )
        
        # parse response
        try:
            ret = completion.choices[0].message
            response_msg = Message(role=ret.role, content=ret.content)
            self.history += [cur_msg, response_msg]
            return response_msg
        except:
            return None
        
    def save(self, output_root):
        save_obj = dict(
            session_id=self.session_id,
            time=generate_datetime_str(),
            system=self.sys_prompt.to_dict(),
            history=[msg.to_dict() for msg in  self.history]
        )
        save_path = os.path.join(output_root, f"{self.session_id}.json")
        json.dump(save_obj, open(save_path, "w"), ensure_ascii=False, indent=4)
        print(f"Your session-{self.session_id} has been saved to: {save_path}")


class ChatGPT(object):

    def __init__(self, 
            api_key, 
            model="gpt-3.5-turbo", 
            bot_role="helpful_assistant",
            save_root=None
        ):
        self.save_root = save_root
        self.model_name = model
        self.auth(api_key)
        self.sys_prompt = SYSTEM_PROMPTS[bot_role]
        self.current_session = None
        
    def auth(self, api_key):
        openai.api_key = api_key

    def new_session(self):
        print("You have started a new chat session")
        session_id = generate_random_string(length=8)
        self.current_session = ChatSession(session_id, self.model_name, self.sys_prompt)

    def resume_session(self, session_id=None):
        # save current session
        if self.current_session:
            self.save()
        # resume session
        # import pdb; pdb.set_trace()
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
                print("[System] There is no saved session, create a new one.")
                self.new_session()
                return
            
            session_id = os.path.basename(session_file).split(".")[0]

        print(f"[System] Resume session from {session_id}")

        session_content = json.load(open(session_file))
        self.current_session = ChatSession(
            session_id=session_content["session_id"], 
            model=self.model_name, 
            sys_prompt=self.sys_prompt, 
            history=session_content["history"]
        )

    def chat(self, user_input: str):
        return self.current_session.chat(user_input)

    def save(self):
        """ save current session
        """
        if self.save_root:
            self.current_session.save(self.save_root)
