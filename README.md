# Washington News Discord Bot

***
# About

It was raining whilst I tried to do laundry, so I decided to create a Discord news bot that can keep me updated with news I - mostly - care about. To do this, newsapi.org was used as it provides simple API access to news across the globe and allows 100 free requests daily. This repository is coded to only get news from the Australian Financial Review source as can be seen in the code below (from the get_news function):

```python
    params = {
        'language': 'en',
        'sources': 'australian-financial-review',
        'from': (datetime.now() - timedelta(days=1)).isoformat(),
        'apiKey': config.news_key
        }
    async with aiohttp.ClientSession() as session, session.get(config.news_url, params=params) as response:
        news = await response.json()
```

Many other sources are available through newsapi.org - alongside other types of requests. If you choose to customise this, you will need to remove the substring code from the get_news function and BotConfig. This code is used to filter down Australian Financial Review topics further, as they specify topic in their URLs.

This bot works quite simply overall - every hour it will get the latest news and post the title and url for that news in the specified Discord guild and channel, provided that news has not already been posted in that channel within the last 7 days by the bot. It will try keep running indefinitely - like any good bot should.

```python
async def news_loop(channel):
    while True:
        try:
            await run_news(channel)
            await asyncio.sleep(3600)
        except Exception as e:
            print(f'Encountered error:\n{e}\nTraceback:\n{traceback.print_exc()}\n\nSleeping...')
            await asyncio.sleep(60)
```

***
# Setup

You will need to create a Discord bot application with permissions to read messages, send messages and view message history. You will need to get the bot to join your Discord server. I am to lazy to write how to do that, Google it. Once that is done and you have cloned this repository, you will need to create a .env file - I strongly recommend not publicly committing the contents of this .env file. You will need Discord developer mode to get some of this information, again Google if needed.

```
DISCORD_TOKEN=your application token for the Discord bot
GUILD_ID=server id of the Discord server the bot will post on
CHANNEL_ID=channel id of discord channel the bot will post in
API_KEY=your newsapi.org key
```

If you are new to .env files, make sure there are no spaces anywhere, do not change variable names. Once setup is complete you can just run the Python file. If you are sophisticated - you can use docker-compose, see key commands below for starting bot on a server with docker-compose:

```python
git clone https://github.com/Jamal135/washington-news       # Download repository
cd washington-news                                          # Enter repository folder
git pull                                                    # Update code (cd first)
docker-compose build                                        # Create docker stuff (cd first)
docker-compose up -d                                        # Start docker stuff (cd first)
docker-compose down                                         # Kill docker stuff (cd first)
docker ps -a                                                # Look at docker stuff...
```

***
# Acknowledgements

I was to lazy to figure some things out myself, so shout out to GPT-4 for doing some of the boring stuff for me. Otherwise cheers to Discord and newsapi.org for having good documentation and easy to use APIs. 

***
# Future

This is becoming a trend with my repositories - I don't have any clue where this repository will go and I make no promises about anything. I do like the idea of taking some user arguments - maybe to query specific news topics. Reactions for more information could be cool as well... who knows.

***
# License

GNU GENERAL PUBLIC LICENSE.
