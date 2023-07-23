#!/bin/sh

set -e
set -x
cd ${WORKDIR}

export CONFIG_DIR=/data/configs
export TGBOT_TOKEN
export OPENAI_KEY
export API_TYPE
export ENGINE

mkdir -p $CONFIG_DIR


if [ -f "$CONFIG_DIR/run.yaml" ]; then
  echo "run.yaml already exists in $CONFIG_DIR"
else
  python3 gen_config.py \
    --api_key=$OPENAI_KEY \
    --api_type=$API_TYPE \
    --api_base=$API_BASE \
    --api_version=${API_VERSION-"2023-03-15-preview"} \
    --engine=$ENGINE \
    --tgbot_token=$TGBOT_TOKEN \
    -o $CONFIG_DIR/run.yaml

fi

python3 launch.py --config=$CONFIG_DIR/run.yaml --mode=tgbot