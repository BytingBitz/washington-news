''' Created: 15/07/2023 '''

import discord
import os
import traceback
import aiohttp
from dotenv import load_dotenv
import asyncio
from datetime import datetime, timedelta

intents = discord.Intents.default()
bot = discord.Client(intents=intents)
load_dotenv()

class BotConfig:
    def __init__(self):
        self.token = self.get_env_variable('DISCORD_TOKEN')
        self.guild_id = self.get_env_variable('GUILD_ID')
        self.channel_id = self.get_env_variable('CHANNEL_ID')
        self.news_key = self.get_env_variable('API_KEY')
        self.news_url = 'https://newsapi.org/v2/top-headlines'
        self.substrings = ['/policy/', '/companies/', '/technology/']
    def get_env_variable(self, variable: str):
        env_var = os.getenv(variable)
        if env_var is None:
            raise EnvironmentError(f'Env {variable} not set!')
        return env_var

async def get_message_data(message):
    if message.author != bot.user or not message.embeds:
        return None
    for embed in message.embeds:
        if not embed.url or not embed.description:
            return None
        return {'title': embed.description, 'url': embed.url}

async def get_history(channel):
    history_data = {'titles': [], 'urls': []}
    async for message in channel.history(limit=500):
        message_data = await get_message_data(message)
        if message_data == None:
            continue
        history_data['titles'].append(message_data['title'])
        history_data['urls'].append(message_data['url'])
    return history_data

async def get_news():
    params = {
        'language': 'en',
        'sources': 'australian-financial-review',
        'from': (datetime.now() - timedelta(days=1)).isoformat(),
        'apiKey': config.news_key
        }
    async with aiohttp.ClientSession() as session:
        async with session.get(config.news_url, params=params) as response:
            news = await response.json()
    if news['status'] != 'ok':
        raise ValueError(f'News API returned a non-ok status:\n{news}')
    return news

async def filter_news(news, channel):
    history = await get_history(channel)
    for article in news['articles'].copy():
        if 'url' not in article or 'title' not in article:
            news['articles'].remove(article)
        elif not any(substring in article['url'] for substring in config.substrings):
            news['articles'].remove(article)
        elif article['url'] in history['urls'] or article['title'] in history['titles']:
            news['articles'].remove(article)
    return news

async def post_news(news, channel):
    if len(news['articles']) == 0:
        return
    for article in news['articles']:
        await channel.send(f'**{article["title"]}**\n{article["url"]}')

async def run_news(channel):
    news = await get_news()
    print(f'News retrieved: {news["totalResults"]} results')
    news = await filter_news(news, channel)
    print(f'News filtered: {len(news["articles"])} new results')
    await post_news(news, channel)
    print(f'Posted {len(news["articles"])} new results...')

async def news_loop(channel):
    while True:
        try:
            await run_news(channel)
            await asyncio.sleep(3600)
        except Exception as e:
            print(f'Encountered error:\n{e}\n{traceback.print_exc()}\nSleeping...')
            await asyncio.sleep(600)

@bot.event
async def on_ready():
    print('Bot is alive...')
    guild = await bot.fetch_guild(config.guild_id)
    channel = await guild.fetch_channel(config.channel_id)
    print('Setup successful')
    bot.loop.create_task(news_loop(channel))

if __name__ == "__main__":
    config = BotConfig()
    bot.run(config.token)
