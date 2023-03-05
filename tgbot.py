import os
import telegram
from chatgpt import ChatGPT
from config import init_config
from telegram import Update
from telegram.ext import MessageHandler, Application, CommandHandler, ContextTypes, filters

chatgpt: ChatGPT = None
config = None

async def new_sesion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 当用户输入 /new 命令，该方法将被调用
    session_id = chatgpt.new_session()
    await update.message.reply_text(f"new session_id: {session_id}")


async def history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 当用户输入 /his 命令，该方法将被调用
    sess = chatgpt.current_session
    if sess.history:
        await update.message.reply_text(f"Show latest {sess.max_history} messages:")
        for _id, msg in enumerate(sess.history[-sess.max_history:]):
            reply = f"@{msg.role}: {msg.content}"
            await update.message.reply_text(reply)
    else:
        await update.message.reply_text("No history found in current session")


async def save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = chatgpt.save()
    await update.message.reply_text(f"your session({chatgpt.current_session.session_id}) has been saved")


async def ls(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sessions = os.listdir(config.save.root)
    session_ids = [sess.split(".")[0] for sess in sessions if sess.endswith(".json")]
    reply = ["All saved sessions:"]
    for _id in session_ids:
        reply.append(f"- {_id}")
    reply = "\n".join(reply)
    await update.message.reply_text(reply)


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = chatgpt.chat(update.message.text)
    await update.message.reply_text(msg.content)


def main(args):

    global chatgpt, config
    
    config = init_config(args.config)
    # start chatting
    chatgpt = ChatGPT(config.openai.api_key, save_root=config.save.root)
    chatgpt.resume_session()

    application = Application.builder().token(config.tgbot.token).build()

    # add commands
    application.add_handler(CommandHandler("new", new_sesion))
    application.add_handler(CommandHandler("his", history))
    application.add_handler(CommandHandler("save", save))
    application.add_handler(CommandHandler("ls", ls))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # start bot
    application.run_polling()
    chatgpt.save()