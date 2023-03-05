# ChatGPT Telegram-Bot/CLI Tool

This project uses the OpenAI API to enable conversational capabilities both in the command console and through a Telegram bot. The ChatGPT API is used to process natural language, understand the intent of the user and generate appropriate responses. (This introduction is almost written by ChatGPT)

## Usage

To use this tool, please follow these instructions:

1. Clone the repository to your local machine.

```
git clone https://github.com/princewang1994/chatgpt-telegram-bot-cli.git
```

2. Install the requirements using pip.

```
pip install -r requirements.txt
```

3. Write your own config

```shell
cp configs/example.yaml configs/my.yaml
```

here is an example:

```yaml
openai:
  api_key: "YOUR_OPENAI_API_KEY"

save:
  root: "./session"

tgbot:
  token: "TELEGRAM TOKEN"  # if run with telegram bot
```

4. To run the script in the command console, run the following code:

for cli mode:

```shell
python3 launch.py --config=configs/my.yaml
```

for telegram-bot mode:

```shell
python launch.py --config=configs/my.yaml --mode=tgbot
```
