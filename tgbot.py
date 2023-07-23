import os
import telegram
from chatgpt import ChatGPT, ChatSession
from config import init_config
from telegram import Update
from telegram.ext import MessageHandler, Application, CommandHandler, ContextTypes, filters

chatgpt: ChatGPT = None
current_sessions = {}  # key=chat_id, value=curren_session
config = None


def get_user_current_session(update):
    user = update.message.chat_id
    if user in current_sessions:
        return current_sessions[user]
    session = chatgpt.get_session(user)
    current_sessions[user] = session
    return session


async def new_sesion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.chat_id
    new_session = chatgpt.new_session(user)
    current_sessions[user] = new_session
    await update.message.reply_text(f"new session_id: {new_session.session_id}")


async def history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sess = get_user_current_session(update)
    if sess.history:
        await update.message.reply_text(f"Show latest {sess.max_history} messages:")
        for _id, msg in enumerate(sess.history[-sess.max_history:]):
            reply = f"@{msg.role}: {msg.content}"
            await update.message.reply_text(reply)
    else:
        await update.message.reply_text("No history found in current session")


async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = get_user_current_session(update)
    info = f"""
    id='{session.session_id}'
    name={session.name}
    model={session.model}
    system='{session.system}'
    history={len(session.history)}
    max_history={session.max_history}
    """
    await update.message.reply_text(info)


async def ch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.chat_id
    session_id = update.message.text.split()[-1]
    session = chatgpt.get_session(user, session_id)
    if session:
        current_sessions[user] = session
        await update.message.reply_text(f"change session to -> {session_id}")
    else:
        await update.message.reply_text(f"no session {session_id}")


async def rename(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    try:
        assert len(update.message.text.split()) > 1
        name = " ".join(update.message.text.split()[1:])
    except AssertionError:
        await update.message.reply_text(f"rename: needs param - name")
        return
    
    session = get_user_current_session(update)
    session.set_session_name(name)
    await update.message.reply_text(f"your session({session.session_id}) has renamed to -> {name}")


async def system(update: Update, context: ContextTypes.DEFAULT_TYPE):
    system = " ".join(update.message.text.split()[1:])
    session = get_user_current_session(update)
    session.set_system(system)
    await update.message.reply_text(f"your session({session.session_id})'s system has changed to -> {system}")


async def ls(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    reply = ["All saved sessions:"]
    user = update.message.chat_id
    sessions = chatgpt.get_user_sessions(user)

    current_session = get_user_current_session(update)
    for idx, sess in enumerate(sessions.values()):
        
        s = f"{idx}.({sess.session_id}): {sess.name}"
        if sess.id == current_session.id:
            s += " <- current"
        reply.append(s)
    reply = "\n".join(reply)
    await update.message.reply_text(reply)


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = get_user_current_session(update)
    msg = session.chat(update.message.text)
    await update.message.reply_text(msg.content)


def main(args):

    global chatgpt, config
    
    config = init_config(args.config)
    # start chatting
    chatgpt = ChatGPT(config.openai, save_root=config.save.root, save_mode=config.save.mode)

    application = Application.builder().token(config.tgbot.token).build()

    # add commands
    application.add_handler(CommandHandler("new", new_sesion))
    application.add_handler(CommandHandler("his", history))
    application.add_handler(CommandHandler("list", ls))
    application.add_handler(CommandHandler("rename", rename))
    application.add_handler(CommandHandler("sys", system))
    application.add_handler(CommandHandler("ch", ch))
    application.add_handler(CommandHandler("info", info))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # start bot
    try:
        application.run_polling()
    except Exception as e:
        print(e)
    finally:
        chatgpt.save(verbose=True)