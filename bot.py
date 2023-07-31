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
        self.substrings = ['/policy', '/companies', '/technology']
    def get_env_variable(self, variable: str):
        try:
            return os.getenv(variable)
        except KeyError:
            raise EnvironmentError(f'Env {variable} not set!')

async def get_history(channel):
    history_data = {'descriptions': [], 'urls': []}
    async for message in channel.history(limit=500):
        if message.author == bot.user and message.embeds:
            for embed in message.embeds:
                if embed.url and embed.description:
                    history_data['descriptions'].append(embed.description)
                    history_data['urls'].append(embed.url)
    return history_data

async def get_news():
    params = {
        'language': 'en',
        'sources': 'australian-financial-review',
        'from': (datetime.now() - timedelta(days=1)).isoformat(),
        'apiKey': config.news_key
        }
    async with aiohttp.ClientSession() as session, session.get(config.news_url, params=params) as response:
        news = await response.json()
    if news['status'] != 'ok':
        raise ValueError(f'News API returned a non-ok status:\n{news}')
    news['articles'] = [article for article in news['articles'] if any(substring in article['url'] for substring in config.substrings)]
    return news

async def run_news(channel):
    history = await get_history(channel)
    news = await get_news()
    print(f'News retrieved: {news["totalResults"]} results')
    news['articles'] = [article for article in news['articles'] if 'url' in article and 'title' in article]
    news['articles'] = [article for article in news['articles'] if article['url'] not in history['urls']]
    news['articles'] = [article for article in news['articles'] if article['title'] not in history['descriptions']]
    print(f'News filtered: {len(news["articles"])} new results')
    for article in news['articles']:
        await channel.send(f'**{article["title"]}**\n{article["url"]}')
    print('Posting news...')

async def news_loop(channel):
    while True:
        try:
            await run_news(channel)
            await asyncio.sleep(3600)
        except Exception as e:
            print(f'Encountered error:\n{e}\nTraceback:\n{traceback.print_exc()}\n\nSleeping...')
            await asyncio.sleep(60)

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
