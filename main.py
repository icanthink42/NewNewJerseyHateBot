import random
import subprocess
import time
from io import BytesIO

import discord
import requests
from Deepfry import deepfry
from discord import NotFound, Permissions
from discord.ext import tasks
from discord.utils import get
from PIL import Image
from youtube_dl import YoutubeDL

import basic_functions
import data
import playlist_song
from classes import MathQuestion, Ratio, RatioButtons
from playlist_song import PlaylistSong

intents = discord.Intents.default()
intents.message_content = True
data.bot = discord.Bot(intents=intents)

data.reload_config()


with YoutubeDL(data.config["ydl_options"]) as ydl:
    data.toad_info = ydl.extract_info(data.config["toad_url"], download=False)

data.load_save_data()
data.fix_data()


@data.bot.event
async def on_ready():
    data.general = await data.bot.fetch_channel(data.local_config["general_id"])
    data.vc_text = await data.bot.fetch_channel(data.local_config["vc_text_id"])
    data.cole = await data.bot.fetch_user(data.local_config["cole_id"])
    if "math_questions" not in data.save_data:
        data.save_data["math_questions"] = {}
    if "ratios" not in data.save_data:
        data.save_data["ratios"] = {}
    if "ratio_count" not in data.save_data:
        data.save_data["ratio_count"] = {}
    if "trumpet_index" not in data.save_data:
        data.save_data["trumpet_index"] = 0
    if "trumpet_channels" not in data.save_data:
        data.save_data["trumpet_channels"] = {}
    print(f"We have logged in as {data.bot.user}")
    hate_nj_vc_loop.start()
    update_loop.start()


@data.bot.event
async def on_message(message: discord.Message):
    if message.author.bot:  # This might be funny to remove
        return
    if (
        isinstance(message.channel, discord.channel.DMChannel)
        and message.author.id == data.local_config["cole_id"]
    ):
        if message.reference is None:
            await message.reply("Reply to a question to answer it!")
            return
        elif message.reference.message_id not in data.save_data["math_questions"]:
            await message.reply("This question has already been answered!")
        else:
            q = data.save_data["math_questions"][message.reference.message_id]
            u = await data.bot.fetch_user(q.asker)
            await u.send(
                '**Math question "' + q.question + '" answered:**\n' + message.content
            )
            del data.save_data["math_questions"][message.reference.message_id]

    if message.channel.id not in data.local_config["channel_whitelist"]:
        return

    if (
        message.attachments
        and message.attachments[0].content_type
        in ("image/jpeg", "image/jpg", "image/png")
        and message.content == "fry"
    ):
        img_bytes = BytesIO(await message.attachments[0].read())
        img = Image.open(img_bytes)
        img.save("before-deepfry.png")
        deepfry.deepfry("before-deepfry.png", "deepfry.png")
        await message.reply("fry", file=discord.File("deepfry.png"))
    if basic_functions.contains_nj(message.content):
        if message.guild.id == 925208758370590820:
            await message.add_reaction(await get_emoji(message.guild, "shut"))
        await message.reply(random.choice(data.config["nj_insults"]))
    if basic_functions.contains_civ_e(message.content):
        await message.reply(random.choice(data.config["civ_e_insults"]))
    if (
        message.content.startswith(")")
        or message.content.startswith(">")
        or message.content.startswith("<@964331688832417802>")
    ):
        await message.reply(
            "Imagine not using slash commands. So lame! Use the new slash commands by typing /"
        )

    if basic_functions.contains_1984(message.content):
        await message.reply(random.choice(data.config["1984_posts"]))
    if "math" in message.content.lower():
        await message.reply("<@352106212109713408> someone mentioned math!")
    if "plant" in message.content.lower() and message.author.id != 367834268535226370:
        await message.reply("<@367834268535226370> someone mentioned plants!")
    if "ratio" in message.content.lower() and message.reference is not None:
        m = await message.reply("Ratio Vote! (0)", view=RatioButtons())
        target_m = await message.channel.fetch_message(message.reference.message_id)
        data.save_data["ratios"][m.id] = Ratio(
            m.id, m.channel.id, target_m.author.id, message.author.id, time.time()
        )
    if ("shut" in message.content.lower() and "up" in message.content.lower()) or (
        "fuck" in message.content.lower() and "off" in message.content.lower()
    ):
        if "ratio" in message.content.lower():
            await message.reply(
                "I don't delete ratio votes to be fair to both sides. Jack will make this feature work better when its not 3:15am"
            )
        else:
            m = await message.channel.fetch_message(message.reference.message_id)
            await m.delete()
    if message.content == "mmmkick":
        await message.author.kick()
    if message.content.lower().startswith("!d "):
        await message.reply("It's d20 not d 20")
        return
    if message.content.lower().startswith("!d"):
        if message.content[2:].isnumeric():
            await message.reply(str(random.randrange(int(message.content[2:]) + 1)))
        else:
            await message.reply(random.choice(message.content[2:]))
    if "shsh" in message.content.lower().replace("e", "").split(" "):
        await message.reply(
            "https://images-ext-1.discordapp.net/external/khYpnieTJ8i4m3xrwmPNNEv0Qw5C1srsD3YX-1KkQtY/https/media.tenor.com/jH7aam4YoDIAAAPo/sheesh-shee.mp4"
        )


async def trumpet_message():
    if "trumpet_channel" not in data.save_data:
        for g_id in data.local_config["guilds"]:
            c = None
            g = await data.bot.fetch_guild(g_id)
            if g_id in data.save_data["trumpet_channels"]:
                try:
                    c = await g.fetch_channel(data.save_data["trumpet_channels"][g_id])
                except:
                    c = None
            if c is None:
                try:
                    c = await g.create_text_channel("🎺")
                except:
                    c = None
            if c is None:
                continue
            data.save_data["trumpet_channels"][g_id] = c.id
            x = requests.get(
                "https://serpapi.com/search.json?q=Trumpet&tbm=isch&ijn=0&api_key="
                + data.local_config["serpapi_key"]
            ).json()
            data.save_data["trumpet_index"] += 1
            if len(x["images_results"]) < data.save_data["trumpet_index"]:
                data.save_data["trumpet_index"] = 0
            if c is not None:
                await c.send(
                    x["images_results"][data.save_data["trumpet_index"]]["original"]
                )


@tasks.loop(hours=1)
async def hate_nj_vc_loop():
    await trumpet_message()
    await vc_insult_nj()
    data.save_save_data()


@tasks.loop(seconds=10)
async def update_loop():
    if (
        time.time()
        > data.save_data["last_birthday_wish"] + data.config["birthday_frequency"]
    ):
        await data.vc_text.send("Happy Birthday <@955141074161111072>!")
        data.save_data["last_birthday_wish"] = time.time()
    r_delete = []
    for r_id in data.save_data["ratios"]:
        r = data.save_data["ratios"][r_id]
        if r.time_sent + data.config["ratio_time"] > time.time():
            continue
        c = await data.bot.fetch_channel(r.channel_id)
        try:
            m = await c.fetch_message(r.message_id)
        except NotFound:
            return
        r_delete.append(m.id)
        if len(r.votes) < 2:
            await m.reply("Not enough votes to determine an outcome!")
            continue
        if r.count_votes() > 0:
            data.add_ratio_score(r.target_id, 1)
            await m.reply("Ratio was successful")
            continue
        elif r.count_votes() < 0:
            data.add_ratio_score(r.accuser_id, 1)
            await m.reply("Ratio failed")
            continue
        elif r.count_votes() == 0:
            await m.reply("Ratio tied")
            continue
    for d in r_delete:
        del data.save_data["ratios"][d]

    data.save_save_data()


@data.bot.slash_command(
    guild_ids=data.local_config["guilds"], description="Ping the bot"
)
async def ping(ctx):
    await ctx.respond(f"Pong! ({data.bot.latency * 100}ms)", ephemeral=True)


@data.bot.slash_command(
    guild_ids=data.local_config["guilds"], description="Runs a sandboxed command"
)
async def exec(ctx, command: str):
    process = subprocess.run(
        ["docker", "container", "exec", "trustsandbox"] + command.split(" "),
        capture_output=True,
        text=True,
    )
    if process.stdout.strip() == "":
        await ctx.respond("(empty response)")
    else:
        await ctx.respond(f"```{process.stdout}```")


@data.bot.slash_command(
    guild_ids=data.local_config["guilds"], description="Play a song on the bot"
)
async def play(ctx, url: str, channel: discord.VoiceChannel):
    if data.toad_mode:
        url = data.config["toad_url"]
    if data.honky_mode:
        url = data.config["honky_url"]
    try:
        with YoutubeDL(data.config["ydl_options"]) as ydl:
            info = ydl.extract_info(url, download=False)
    except:
        await ctx.respond(
            "Something went wrong while attempting to get the video!", ephemeral=True
        )
        return
    if info["duration"] > data.config["max_song_length"]:
        await ctx.respond("Video is too long!", ephemeral=True)
        return
    if basic_functions.contains_nj(info["title"]):
        await ctx.respond(
            "I don't play songs that contain the slander of new jersey!", ephemeral=True
        )
        return
    if "static" in info["title"].lower():
        await ctx.respond("bad toby", ephemeral=True)
        return
    if "toby" in ctx.author.display_name.lower():
        await ctx.respond(
            'I\'m very sorry but because your name contains "toby" you cannot play music. Please contact <@343545158140428289> if this is a mistake!',
            ephemeral=True,
        )
        return
    song = PlaylistSong(url, info, channel, ctx.author)
    data.queue.append(song)
    if len(data.queue) > 1:
        if data.queue[0].toad:
            await ctx.respond(f"Playing {info['title']}...", ephemeral=True)
            await skip_song()
        else:
            await ctx.respond(f"Added {info['title']} to the queue", ephemeral=True)
    else:
        await ctx.respond(f"Playing {info['title']}...", ephemeral=True)
        await song.play_song()


@data.bot.slash_command(
    guild_ids=data.local_config["guilds"], description="Skip the current song playing"
)
async def skip(ctx):
    if len(data.queue) == 0:
        await ctx.respond("The queue is empty!", ephemeral=True)
        return
    await skip_song()
    await ctx.respond("Skipped song!", ephemeral=True)


@data.bot.slash_command(
    guild_ids=data.local_config["guilds"], description="Shows the current song queue"
)
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
            embed.add_field(
                name="Current Song Playing: " + data.queue[0].info["title"],
                value=f"Played by {data.queue[0].user.display_name} in <#{data.queue[0].channel.id}>.",
                inline=True,
            )
        else:
            embed.add_field(
                name=str(index) + ". " + song.info["title"],
                value=f"Queued to <#{song.channel.id}> by {song.user.display_name}.",
            )
        index += 1
    if (
        data.queue[0].info["thumbnails"] is not None
        and len(data.queue[0].info["thumbnails"]) != 0
    ):
        embed.set_image(url=data.queue[0].info["thumbnails"][0]["url"])
    await ctx.respond(embed=embed, ephemeral=True)


@data.bot.slash_command(guild_ids=data.local_config["guilds"], description="TOAD")
async def toad(ctx):
    data.toad_mode = not data.toad_mode
    await ctx.respond("Toad mode set to " + str(data.toad_mode), ephemeral=True)


@data.bot.slash_command(
    guild_ids=data.local_config["guilds"], description="Musical Excellence"
)
async def honky(ctx):
    data.honky_mode = not data.honky_mode
    await ctx.respond("Honky mode set to " + str(data.honky_mode), ephemeral=True)


@data.bot.slash_command(
    guild_ids=data.local_config["guilds"], description="Reloads the bots config"
)
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


@data.bot.slash_command(
    guild_ids=data.local_config["guilds"], description="Use the bots calculator"
)
async def calculator(ctx, question: str):
    m = await data.cole.send("**Math question to solve!**\n" + question)
    data.save_data["math_questions"][m.id] = MathQuestion(question, m.id, ctx.author.id)
    await ctx.respond(
        "Using advanced algorithms to solve... You will receive the answer as a DM.",
        ephemeral=True,
    )


@data.bot.slash_command(
    guild_ids=data.local_config["guilds"],
    description="See a list of how many times everyone has been ratiod",
)
async def ratios(ctx):
    o = ""
    for u_id in data.save_data["ratio_count"]:
        count = data.save_data["ratio_count"][u_id]
        o += "<@" + str(u_id) + ">: " + str(count) + "\n"
    await ctx.respond(o, ephemeral=True)


async def get_emoji(guild: discord.Guild, arg):
    return get(guild.emojis, name=arg)


async def skip_song():
    vc = get(data.bot.voice_clients, guild=data.general.guild)
    if vc is None or not vc.is_connected():
        data.queue = []
        return
    if len(data.queue) == 0:
        return
    if (
        vc.is_playing()
    ):  # Length of queue must be checked before and after because stopping audio changes the queues
        vc.stop()
    if len(data.queue) == 0:
        return


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
    vc.play(
        discord.FFmpegPCMAudio(file),
        after=lambda err: data.bot.loop.create_task(playlist_song.song_finish(False)),
    )


data.bot.run(data.local_config["token"])
