import json
import random

import discord
from discord.ext import tasks
from discord.utils import get
from youtube_dl import YoutubeDL

import basic_functions
import data
from playlist_song import PlaylistSong

intents = discord.Intents.default()
intents.message_content = True
data.bot = discord.Bot(intents=intents)

data.reload_config()


@data.bot.event
async def on_ready():
    data.general = data.bot.get_channel(data.local_config["general_id"])
    print(f"We have logged in as {data.bot.user}")
    hate_nj_vc_loop.start()


@data.bot.event
async def on_message(message: discord.Message):
    if message.author.bot:  # This might be funny to remove
        return
    if basic_functions.contains_nj(message.content):
        await message.add_reaction(await get_emoji(message.guild, "shut"))
        await message.reply(random.choice(data.config["nj_insults"]))
    if basic_functions.contains_civ_e(message.content):
        await message.reply(random.choice(data.config["civ_e_insults"]))
    if message.content.startswith(")") or message.content.startswith(">") or message.content.startswith("<@964331688832417802>"):
        await message.reply("Imagine not using slash commands. So lame! Use the new slash commands by typing /")
    im_index = basic_functions.im_index(message.content)
    if im_index != -1:
        await message.reply(f"Hi {message.content[im_index:]}, I'm the New Jersey Hate Bot!")



@tasks.loop(hours=1)
async def hate_nj_vc_loop():
    await vc_insult_nj()


@data.bot.slash_command(guild_ids=data.local_config["guilds"], description="Ping the bot")
async def ping(ctx):
    await ctx.respond(f"Pong! ({data.bot.latency * 100}ms)", ephemeral=True)


@data.bot.slash_command(guild_ids=data.local_config["guilds"], description="Play a song on the bot")
async def play(ctx, url: str, channel: discord.VoiceChannel):
    try:
        with YoutubeDL(data.config["ydl_options"]) as ydl:
            info = ydl.extract_info(url, download=False)
    except:
        await ctx.respond("Something went wrong while attempting to get the video!", ephemeral=True)
        return
    if info["duration"] > data.config["max_song_length"]:
        await ctx.respond("Video is too long!", ephemeral=True)
        return
    if basic_functions.contains_nj(info["title"]):
        await ctx.respond("I don't play songs that contain the slander of new jersey!", ephemeral=True)
        return
    if "static" in info["title"].lower():
        await ctx.respond("bad toby", ephemeral=True)
        return
    if "toby" in ctx.author.display_name.lower():
        await ctx.respond(
            "I'm very sorry but because your name contains \"toby\" you cannot play music. Please contact <@343545158140428289> if this is a mistake!",
            ephemeral=True)
        return
    song = PlaylistSong(url, info, channel, ctx.author)
    data.queue.append(song)
    if len(data.queue) > 1:
        await ctx.respond(f"Added {info['title']} to the queue", ephemeral=True)
    else:
        await ctx.respond(f"Playing {info['title']}...", ephemeral=True)
        await song.play_song()


@data.bot.slash_command(guild_ids=data.local_config["guilds"], description="Skip the current song playing")
async def skip(ctx):
    if len(data.queue) == 0:
        await ctx.respond("The queue is empty!", ephemeral=True)
        return
    await skip_song()
    await ctx.respond("Skipped song!", ephemeral=True)


@data.bot.slash_command(guild_ids=data.local_config["guilds"], description="Shows the current song queue")
async def queue(ctx):
    embed = discord.Embed(
        title="Current Song Queue",
        description="",
        color=discord.Color.blurple(),
    )
    if len(data.queue) == 0:
        embed.add_field(name="Queue is empty!", value="Play something with /play")
        await ctx.respond(embed=embed, ephemeral=True)
        return
    index = 0
    for song in data.queue:
        if index == 0:
            embed.add_field(name="Current Song Playing: " + data.queue[0].info["title"],
                            value=f"Played by {data.queue[0].user.display_name} in <#{data.queue[0].channel.id}>.",
                            inline=True)
        else:
            embed.add_field(name=str(index) + ". " + song.info["title"],
                            value=f"Queued to <#{song.channel.id}> by {song.user.display_name}.")
        index += 1
    if data.queue[0].info["thumbnails"] is not None and len(data.queue[0].info["thumbnails"]) != 0:
        embed.set_image(url=data.queue[0].info["thumbnails"][0]["url"])
    await ctx.respond(embed=embed, ephemeral=True)


@data.bot.slash_command(guild_ids=data.local_config["guilds"], description="Reloads the bots config")
async def reload(ctx):
    if ctx.author.id not in data.config["mods"]:
        await ctx.respond("You are not on the mods list!", ephemeral=True)
        return
    try:
        data.reload_config()
    except:
        await ctx.respond("Error reloading config file!", ephemeral=True)
        return
    await ctx.respond("Config reloaded!", ephemeral=True)


async def get_emoji(guild: discord.Guild, arg):
    return get(guild.emojis, name=arg)


async def skip_song():
    vc = get(data.bot.voice_clients, guild=data.general.guild)
    if vc is None or not vc.is_connected():
        return
    if len(data.queue) != 0:
        data.queue.pop(0)
    if len(data.queue) == 0:
        await vc.disconnect()
        return
    if vc.is_playing():
        await vc.stop()
    await data.queue[0].play_song()


async def vc_insult_nj():
    vc = get(data.bot.voice_clients, guild=data.general.guild)
    if vc is None or not vc.is_connected():
        vc = await data.general.connect()
    if vc.is_playing():
        vc.stop()
    if vc.channel.id != data.general.id:
        await vc.disconnect()
        data.general.connect()
    file = basic_functions.random_file(data.config["audio_files_dir"])
    vc.play(discord.FFmpegPCMAudio(file), after=lambda err: data.bot.loop.create_task(skip_song()))


data.bot.run(data.local_config["token"])
