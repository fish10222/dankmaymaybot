import asyncio
import discord
import ffmpeg
import time
import youtube_dl
from discord.ext import commands
from discord.voice_client import VoiceClient


ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)



client = commands.Bot(command_prefix='!')

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.command(pass_context=True)
async def join(ctx):
    if ctx.author.voice is None or ctx.author.voice.channel is None:
        return
    voice_channel = ctx.author.voice.channel
    if ctx.voice_client is None:
        vc = await voice_channel.connect()
    else:
        await ctx.voice_client.move_to(voice_channel)
        vc = ctx.voice_client

@client.command(pass_context=True)
async def leave(ctx):
    await ctx.voice_client.disconnect()

@client.command(pass_context=True)
async def damedane(ctx):
    if ctx.author.voice is None or ctx.author.voice.channel is None:
        return
    voice_channel = ctx.author.voice.channel
    if ctx.voice_client is None:
        vc = await voice_channel.connect()
    else:
        await ctx.voice_client.move_to(voice_channel)
        vc = ctx.voice_client
    await ctx.send("DAME DA NE")
    player = await YTDLSource.from_url('https://www.youtube.com/watch?v=83_ZBY2zeGs', stream=True)
    vc.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
    while vc.is_playing():
        time.sleep(1)
    await vc.disconnect()



# @client.event
# async def on_message(message):
#     if message.author == client.user:
#         return

#     if message.content.startswith('$hello'):
#         await message.channel.send('Hello!')


client.run('ODIwNTA1ODQwMDc0MzU4ODE0.YE2JnA.GZQGgxDDjIwRr3tbSgcqzdlCyKc')