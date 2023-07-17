''' Created: 15/07/2023 '''

import discord
import os
import aiohttp
from dotenv import load_dotenv
import asyncio
from datetime import datetime, timedelta

load_dotenv()
token = os.getenv('DISCORD_TOKEN')
guild_id = os.getenv('GUILD_ID')
channel_id = os.getenv('CHANNEL_ID')
bot = discord.Client(intents=discord.Intents.default())
news_url = "https://newsapi.org/v2/top-headlines"
news_key = os.getenv('API_KEY')

class NewsAPIError(Exception):
    pass

async def get_history(channel):
    history_urls = []
    two_weeks_ago = datetime.now() - timedelta(weeks=1)
    async for message in channel.history(after=two_weeks_ago):
        if message.author == bot.user:
            if message.embeds:
                for embed in message.embeds:
                    if embed.url:
                        history_urls.append(embed.url)
            if message.attachments:
                for attachment in message.attachments:
                    history_urls.append(attachment.url)
    return history_urls

async def get_news():
    parameters = {
        'language': 'en',
        'sources': 'australian-financial-review',
        'from': (datetime.now() - timedelta(days=1)).isoformat(),
        'apiKey': news_key
        }
    async with aiohttp.ClientSession() as session:
        async with session.get(news_url, params=parameters) as response:
            news = await response.json()
    if news['status'] != 'ok':
        raise NewsAPIError('News API returned a non-ok status')
    print(f'News retrieved: {news["totalResults"]} results')
    return news

async def run_news(channel):
    history = await get_history(channel)
    news = await get_news()
    news['articles'] = [article for article in news['articles'] if 'url' in article and article['url'] not in history]
    for article in news['articles']:
        await channel.send(f'**{article["title"]}**\n{article["url"]}')
    print(f'Posting news: {len(news["articles"])} new results')
    await asyncio.sleep(3600)

@bot.event
async def on_ready():
    guild = await bot.fetch_guild(guild_id)
    channel = await guild.fetch_channel(channel_id)
    print('Setup successful')
    fail = 0
    while True:
        try:
            await run_news(channel)
            fail = 0
        except (aiohttp.ClientError, asyncio.TimeoutError, NewsAPIError):
            print('Encountered news issue, sleeping...')
            await asyncio.sleep(30)
        except Exception as error:
            fail += 1
            print(f'Encountered issue #{fail}:\n\n{error}')
            if fail >= 10:
                print(f'\n\n#{fail} Code aborting')
                quit()

if __name__ == "__main__":
    bot.run(token)
