import sys
import argparse
import cli
import tgbot


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='ChatGPT')
    parser.add_argument('--config', type=str, default=None, required=True,
                        help='config_file')
    parser.add_argument('--model', type=str, default='gpt-3.5-turbo',
                        help='chagpt model name')
    parser.add_argument('--debug', action="store_true",
                        help='debug mode')
    parser.add_argument('--mode', type=str, default="cmd", choices=("tgbot", "cmd"), 
                        help='launch mode, (tgbot or cmd)')

    args = parser.parse_args()

    if args.mode == "cmd":
        sys.exit(cli.main(args))
    else:
        sys.exit(tgbot.main(args))
    