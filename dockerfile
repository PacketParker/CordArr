FROM python:3.12-slim

LABEL org.opencontainers.image.source="https://git.pkrm.dev/parker/cordarr"
LABEL org.opencontainers.image.authors="parker <mailto:contact@pkrm.dev>"

WORKDIR /

COPY . .
RUN pip install -r requirements.txt

USER 1000:1000

ENTRYPOINT [ "python" ]
CMD [ "-u",  "code/bot.py" ]