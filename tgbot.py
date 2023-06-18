import os
import telegram
from chatgpt import ChatGPT, ChatSession
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
    msg = chatgpt.save(verbose=True)
    await update.message.reply_text(f"your session({chatgpt.current_session.session_id}) has been saved")


async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = chatgpt.current_session
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
    session_id = update.message.text.split()[-1]
    chatgpt.resume_session(session_id)
    await update.message.reply_text(f"change session to -> {session_id}")


async def rename(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        assert len(update.message.text.split()) > 1
        name = " ".join(update.message.text.split()[1:])
    except AssertionError:
        await update.message.reply_text(f"rename: needs param - name")
        return
    chatgpt.current_session.set_session_name(name)
    await update.message.reply_text(f"your session({chatgpt.current_session.session_id}) has renamed to -> {name}")


async def system(update: Update, context: ContextTypes.DEFAULT_TYPE):
    system = " ".join(update.message.text.split()[1:])
    chatgpt.current_session.set_system(system)
    await update.message.reply_text(f"your session({chatgpt.current_session.session_id})'s system has changed to -> {system}")


async def ls(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sessions = os.listdir(config.save.root)
    sessions = [sess for sess in sessions if sess.endswith(".json")]
    
    reply = ["All saved sessions:"]
    
    for idx, sess in enumerate(sessions):
        ckpt = os.path.join(config.save.root, sess)
        sess = ChatSession.resume_from_file(ckpt)
        
        s = f"{idx}.({sess.session_id}): {sess.name}"
        if sess.id == chatgpt.current_session.id:
            s += " <- current"
        reply.append(s)
    reply = "\n".join(reply)
    await update.message.reply_text(reply)


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = chatgpt.chat(update.message.text)
    await update.message.reply_text(msg.content)


def main(args):

    global chatgpt, config
    
    config = init_config(args.config)
    # start chatting
    chatgpt = ChatGPT(config.openai, save_root=config.save.root, save_mode=config.save.mode)
    chatgpt.resume_session()

    application = Application.builder().token(config.tgbot.token).build()

    # add commands
    application.add_handler(CommandHandler("new", new_sesion))
    application.add_handler(CommandHandler("his", history))
    application.add_handler(CommandHandler("save", save))
    application.add_handler(CommandHandler("list", ls))
    application.add_handler(CommandHandler("rename", rename))
    application.add_handler(CommandHandler("sys", rename))
    application.add_handler(CommandHandler("ch", ch))
    application.add_handler(CommandHandler("info", info))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # start bot
    application.run_polling()
    chatgpt.save()