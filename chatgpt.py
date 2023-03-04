import os
import openai
from collections import deque
from message import Message
from enum import Enum


class ChatGPTRole(Enum):
    SYSTEM = 0
    ASSISTANT = 1
    USER = 2


SYSTEM_PROMPTS = {
    "helpful_assistant": Message(role="system", content="You are a helpful assistant."),
}


class ChatSession(object):

    def __init__(self, model, sys_prompt, max_history=10) -> None:
        self.sys_prompt = sys_prompt
        self.model = model
        self.max_history = max_history
        self.history = deque()

    def chat(self, user_input: str):
        # init with system prompt
        messages = [self.sys_prompt.to_dict()]
        messages += [msg.to_dict() for msg in self.history]
        
        cur_msg = Message(role="user", content=user_input)
        messages.append(cur_msg.to_dict())
        
        completion = openai.ChatCompletion.create(
            model=self.model,
            messages=messages
        )
        
        ret = completion.choices[0].message
        response_msg = Message(role=ret.role, content=ret.content)

        self.history.append(response_msg)
        if len(self.history) > self.max_history:
            self.history.popleft()
        return response_msg
    


class ChatGPT(object):

    def __init__(self, model="gpt-3.5-turbo", bot_role="helpful_assistant"):
        self.model_name = model
        self.auth(os.getenv("OPENAI_API_KEY"))
        self.sys_prompt = SYSTEM_PROMPTS[bot_role]
        
    def auth(self, api_key):
        openai.api_key = api_key

    def new_session(self):
        return ChatSession(self.model_name, self.sys_prompt)

    def __call__(self, message: Message):
        pass


def get_args():
    import argparse

    parser = argparse.ArgumentParser(description='ChatGPT')

    parser.add_argument('--model_path', type=str, default='./model',
                        help='预训练模型的路径，默认为"./model"')
    parser.add_argument('--length', type=int, default=50,
                        help='生成文本的长度，默认为50')
    parser.add_argument('--num_samples', type=int, default=1,
                        help='生成文本的数量，默认为1')
    parser.add_argument('--temperature', type=float, default=1.0,
                        help='用于控制生成文本的随机性，值越大生成的文本越随机，默认为1.0')
    parser.add_argument('--top_k', type=int, default=0,
                        help='用于控制生成文本的范围，只在最可能的K个词中生成，默认为0')
    parser.add_argument('--top_p', type=float, default=0.9,
                        help='用于控制生成文本的范围，只在概率总和累计大于给定值时停止生成，默认为0.9')

    args = parser.parse_args()

    return args


if __name__ == '__main__':
    args = get_args()
    chatgpt = ChatGPT()
    sess = chatgpt.new_session()

    # texts = [
    #     "我要卖一个大容量水杯，帮我写一个广告标题，知乎风格",
    #     "换成抖音风格"
    # ]
    
    while True:

        user_input = input("[User]: ")

        try:
            rsp = sess.chat(user_input)
            print(f"[ChatGPT]: {rsp.content}")
        except Exception as e:
            import traceback
            traceback.print_exc()
    