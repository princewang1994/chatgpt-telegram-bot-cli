#!/bin/sh

set -e
cd ${WORKDIR}

export CONFIG_DIR=/data/configs
export TELEGRAM_TOKEN
export OPENAI_KEY

mkdir -p $CONFIG_DIR


if [ -f "$CONFIG_DIR/run.yaml" ]; then
  echo "run.yaml already exists in $CONFIG_DIR"
else
  # check necessary tokens
  if [ -z "$OPENAI_KEY" ]; then
    echo "OPENAI_KEY is not set, exiting."
    exit
  fi

  if [ -z "$TELEGRAM_TOKEN" ]; then 
    echo "TELEGRAM_TOKEN is not set, exiting."
    exit
  fi
  echo "Copying run.yaml template to $CONFIG_DIR"
  cp $WORKDIR/configs/example.yaml $CONFIG_DIR/run.yaml
  
  # replace openai.api_key with $OPENAI_KEY
  sed -i "s/api_key:.*/api_key: $OPENAI_KEY/g" $CONFIG_DIR/run.yaml
  
  # replace tgbot.token with $TELEGRAM_TOKEN
  sed -i "s/token:.*/token: $TELEGRAM_TOKEN/g" $CONFIG_DIR/run.yaml

fi


python3 launch.py --config=$CONFIG_DIR/run.yaml --mode=tgbot