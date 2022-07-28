from datetime import datetime

import discord
from discord.utils import get
from youtube_dl import YoutubeDL

import data


class PlaylistSong:
    def __init__(self, url: str, info, channel: discord.VoiceChannel, user: discord.User):
        self.url = url
        self.info = info
        self.channel = channel
        self.user = user

    async def play_song(self):
        ydl = YoutubeDL(data.config["ydl_options"])
        info = ydl.extract_info(self.url)
        url = info["formats"][0]["url"]
        vc = get(data.bot.voice_clients, guild=self.channel.guild)
        if vc is None or not vc.is_connected():
            vc = await self.channel.connect()
        if vc.is_playing():
            vc.stop()
        vc.play(discord.FFmpegPCMAudio(url, **data.config["ffmpeg_options"]), after=lambda err: data.bot.loop.create_task(song_finish()))
        await data.bot.change_presence(
            activity=discord.Activity(type=discord.ActivityType.listening, name=info['title']))


async def song_finish():
    if len(data.queue) != 0:
        finished_song = data.queue[0]
        data.queue.pop(0)
    if len(data.queue) > 0:
        await data.queue[0].play_song()
    elif datetime.now().weekday() == data.config["toad_day"]:
        vc = get(data.bot.voice_clients, guild=data.general.guild)
        if vc is None or not vc.is_connected():
            vc = await data.general.connect()
        if vc.is_playing():
            vc.stop()
        vc.play(discord.FFmpegPCMAudio(data.toad_info["formats"][0]["url"], **data.config["ffmpeg_options"]),
                after=lambda err: data.bot.loop.create_task(song_finish()))
    else:
        await data.bot.change_presence(
            activity=discord.Activity(type=discord.ActivityType.listening, name="Nothing! Play something with /play"))
        vc = get(data.bot.voice_clients, guild=data.general.guild)
        vc.disconnect()
