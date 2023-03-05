import os
import yaml
from addict import Dict


def init_config(config_path):

    with open(config_path, "r") as f:
        yaml_str = f.read()

    config = Dict(yaml.load(yaml_str, Loader=yaml.FullLoader))
    os.makedirs(config.save.root, exist_ok=True)
    return config