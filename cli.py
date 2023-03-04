import os
import argparse
import yaml
import logging
from addict import Dict
from prompt_toolkit import prompt
from chatgpt import ChatGPT
from commands import ChatGPTCommand


# globals
chatgpt = None
commands = None


def init_config(config_path):

    with open(config_path, "r") as f:
        yaml_str = f.read()

    config = Dict(yaml.load(yaml_str, Loader=yaml.FullLoader))
    os.makedirs(config.save.root, exist_ok=True)
    return config


def eval_command(user_input):

    splited = user_input.split()
    if len(splited) == 0:
        return
    
    # eval command
    if splited[0] in commands.cmd_list:
        cmd, args = splited[0], splited[1:]
        logging.debug(f"{cmd} {args}")
        commands(cmd, args)
    else:
        rsp = chatgpt.chat(user_input)
        if rsp:
            print(f"<ChatGPT>: {rsp.content}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='ChatGPT')
    parser.add_argument('--config', type=str, default=None, required=True,
                        help='config_file')
    parser.add_argument('--model', type=str, default='gpt-3.5-turbo',
                        help='chagpt model name')
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

    config = init_config(args.config)

    # start commandline chatting
    chatgpt = ChatGPT(config.openai.api_key, save_root=config.save.root)
    chatgpt.resume_session()
    commands = ChatGPTCommand(chatgpt, config)
    
    while True:

        try:
            user_input = prompt("<User>: ")
            eval_command(user_input)
        except KeyboardInterrupt:
            pass
        except EOFError:
            chatgpt.save()
            print("Good bye!")
            exit(0)
        except Exception as e:
            import traceback
            traceback.print_exc()
    