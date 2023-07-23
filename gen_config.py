import argparse
from jinja2 import Template


# 创建命令行解析器
parser = argparse.ArgumentParser(description='Generate configuration file.')
parser.add_argument('--api_key', type=str, required=True, help='OpenAI API Key')
parser.add_argument('--api_base', type=str, help='Azure Base')
parser.add_argument('--api_type', type=str, help='Azure api type')
parser.add_argument('--api_version', type=str, default="2023-03-15-preview", help='OpenAI API version')
parser.add_argument('--engine', type=str, help='engine')
parser.add_argument('--tgbot_token', type=str, help='Telegram Token')
parser.add_argument('--output', '-o', type=str, default="run.yaml", help='Output path')

# 解析命令行参数
args = parser.parse_args()

# 定义需要替换的变量
config_data = {
    'api_key': args.api_key,
    'api_base': args.api_base,
    'api_type': args.api_type,
    'api_version': args.api_version,
    'engine': args.engine,
    'tgbot_token': args.tgbot_token,
}

if __name__ == "__main__":
    # 读取模板文件
    with open('configs/template.yaml', 'r') as f:
        template_str = f.read()

    # 创建Jinja2模板对象
    template = Template(template_str)
    # 使用Jinja2模板引擎渲染模板，生成具体的配置文件内容
    config_content = template.render(config_data)

    # 将生成的配置文件内容写入到文件中
    with open(args.output, 'w') as f:
        f.write(config_content)

