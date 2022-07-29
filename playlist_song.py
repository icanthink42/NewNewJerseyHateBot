from datetime import datetime

import discord
from discord.utils import get

import data


class PlaylistSong:
    def __init__(self, url: str, info, channel: discord.VoiceChannel, user: discord.User, toad=False):
        self.url = url
        self.info = info
        self.channel = channel
        self.user = user
        self.toad = toad

    async def play_song(self):
        await play(self.info, self.channel)
        await data.bot.change_presence(
            activity=discord.Activity(type=discord.ActivityType.listening, name=self.info['title']))


async def song_finish(queue):
    if len(data.queue) != 0 and queue:
        data.queue.pop(0)
    if datetime.now().weekday() == data.config["toad_day"] and len(data.queue) == 0:
        data.queue.append(PlaylistSong(data.config["toad_url"], data.toad_info, data.general, await data.bot.fetch_user(423563404003770369), True))
    if len(data.queue) > 0:
        await data.queue[0].play_song()
    else:
        await data.bot.change_presence(
            activity=discord.Activity(type=discord.ActivityType.listening, name="Nothing! Play something with /play"))


async def play(info, channel: discord.VoiceChannel) -> bool:
    vc = get(data.bot.voice_clients, guild=channel.guild)
    if vc is None or not vc.is_connected():
        vc = await channel.connect()
    if vc.is_playing():
        return False
    vc.play(discord.FFmpegPCMAudio(info["formats"][0]["url"], **data.config["ffmpeg_options"]), after=lambda err: data.bot.loop.create_task(song_finish(True)))
    return True
