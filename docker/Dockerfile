FROM python:3-alpine

ENV LANG="C.UTF-8" \
    TZ="Asia/Shanghai" \
    WORKDIR="/chatgpt"

COPY . ${WORKDIR}

RUN apk update  \
    && ln -sf /usr/share/zoneinfo/${TZ} /etc/localtime \
    && echo "${TZ}" > /etc/timezone \
    && pip install -r ${WORKDIR}/requirements.txt \
    && rm -rf /tmp/* /root/.cache /var/cache/apk/*


RUN chmod +x ${WORKDIR}/docker/entrypoint.sh

VOLUME ["/data"]

ENTRYPOINT ["/chatgpt/docker/entrypoint.sh"]