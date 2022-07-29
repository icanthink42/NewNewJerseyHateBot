from datetime import datetime

import discord
from discord.utils import get

import data


class PlaylistSong:
    def __init__(self, url: str, info, channel: discord.VoiceChannel, user: discord.User):
        self.url = url
        self.info = info
        self.channel = channel
        self.user = user

    async def play_song(self):
        await play(self.info, self.channel)
        await data.bot.change_presence(
            activity=discord.Activity(type=discord.ActivityType.listening, name=self.info['title']))


async def song_finish():
    if len(data.queue) != 0:
        data.queue.pop(0)
    if len(data.queue) > 0:
        await data.queue[0].play_song()
    elif datetime.now().weekday() == data.config["toad_day"]:
        await play(data.toad_info, data.general)
    else:
        await data.bot.change_presence(
            activity=discord.Activity(type=discord.ActivityType.listening, name="Nothing! Play something with /play"))


async def play(info, channel: discord.VoiceChannel):
    vc = get(data.bot.voice_clients, guild=channel.guild)
    if vc is None or not vc.is_connected():
        vc = await channel.connect()
    if vc.is_playing():
        vc.stop()
    vc.play(discord.FFmpegPCMAudio(info["formats"][0]["url"], **data.config["ffmpeg_options"]), after=lambda err: data.bot.loop.create_task(song_finish()))
