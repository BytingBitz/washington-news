FROM python:3.10.2-slim-buster

RUN adduser --disabled-password --gecos '' --shell /usr/sbin/nologin user

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER user

CMD [ "python", "-u", "bot.py"]