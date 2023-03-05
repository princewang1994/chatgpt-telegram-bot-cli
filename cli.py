import os
import argparse
import logging
from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from chatgpt import ChatGPT
from config import init_config
from commands import ChatGPTCommand


# globals
chatgpt = None
commands = None


def eval_command(user_input):

    splited = user_input.split()
    if len(splited) == 0:
        return
    
    # eval command
    if splited[0] in commands.cmds:
        cmd, args = splited[0], splited[1:]
        logging.debug(f"{cmd} {args}")
        commands(cmd, args)
    else:
        rsp = chatgpt.chat(user_input)
        if rsp:
            print(f"<ChatGPT>: {rsp.content}")


def main(args):

    global chatgpt, commands

    config = init_config(args.config)

    # start commandline chatting
    chatgpt = ChatGPT(config.openai.api_key, save_root=config.save.root)
    chatgpt.resume_session()
    commands = ChatGPTCommand(chatgpt, config)
    
    while True:

        try:
            user_input = prompt("<User>: ", history=FileHistory('.history.txt'))
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
    