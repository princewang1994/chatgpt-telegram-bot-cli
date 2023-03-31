FROM alpine
RUN apk update  \
    && apk add python3-dev py3-pip git \
    && ln -sf /usr/share/zoneinfo/${TZ} /etc/localtime \
    && echo "${TZ}" > /etc/timezone \
    && ln -sf /usr/bin/python3 /usr/bin/python \
    && pip install -r https://raw.githubusercontent.com/princewang1994/chatgpt-telegram-bot-cli/master/requirements.txt \
    && rm -rf /tmp/* /root/.cache /var/cache/apk/*

ENV LANG="C.UTF-8" \
    TZ="Asia/Shanghai" \
    WORKDIR="/chatgpt" \
    REPO_URL="https://github.com/princewang1994/chatgpt-telegram-bot-cli.git"

WORKDIR ${WORKDIR}

RUN mkdir -p ${WORKDIR} \
    && python_ver=$(python3 -V | awk '{print $2}') \
    && git clone -b master ${REPO_URL} ${WORKDIR} --depth=1 --recurse-submodule \
    && git config --global --add safe.directory ${WORKDIR} \
    && chmod +x ${WORKDIR}/docker/entrypoint.sh \
    && ls -l ${WORKDIR}/docker/entrypoint.sh

VOLUME ["/data"]

ENTRYPOINT ["/chatgpt/docker/entrypoint.sh"]