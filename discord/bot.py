# bot.py
import os
import discord
from discord import File
import random
import time
from datetime import datetime
import re
import math
import threading, queue

from discord.ext import commands
from discord.ext.commands import Bot
from discord import FFmpegPCMAudio
from discord.utils import get
from discord.voice_client import VoiceClient

from os import listdir
from os.path import isfile, join

import asyncio
import requests


TOKEN = 'NzIzODA2MjcwNTI3NzY2NjM5.XwTr8Q.VWzJTrGVZDNK3c76PabdtV7b1g8'
GUILD = 657034208052510720

TEXT_CHANNEL_ID = 730172538600292455
VOICE_CHANNEL_ID = 700431433142894592

CMD_PREFIX = "!!"

client = discord.Client()
bot = commands.Bot(command_prefix=CMD_PREFIX)

queue = queue.Queue()

current_track_title = ""

global PLAYLIST_PATH
PLAYLIST_PATH = 'playlists/default/'

start_time = datetime.now()

def get_time():
    global start_time

    current_time = datetime.now()
    time_elapsed = current_time - start_time

    # ie 0:02:44.626317 -> 0:02:44
    return str(time_elapsed).split('.')[0]

def reset_time():
    global start_time
    start_time = datetime.now()


from tinytag import TinyTag
from ffprobe import FFProbe

def get_track_length(file_path):
    try:
        track_title = file_path.split('/')[-1]

        dir_path = os.path.dirname(os.path.realpath(file_path))
        full_path = dir_path+'/'+track_title
        print(full_path)

        tag = TinyTag.get('playlists/default/joe-rogan-sam-harris.mp3')
        print('It is %f seconds long.' % tag.duration)

        meta = FFProbe('playlists/default/joe-rogan-sam-harris.mp3')
        print(meta.metadata['Duration'])

        assert full_path.endswith('.mp3')


        # print("Track length for {file_path}: {length}".format(file_path=file_path, length=str(audio.info.length)))

    except:
        print("Error")


podcast_length = 1800



import nest_asyncio
nest_asyncio.apply()

async def periodic():
    while True:
    #while get_time() < podcast_length:
        time = get_time()
        print(time)
        r = requests.get('http://localhost:6969/comments/'+current_track_title+'/'+time)
        await asyncio.sleep(1)

def stop():
    task.cancel()

#@bot.command()
#async def start_asyncio(ctx):

def start_event_loop():
    global task

    loop = asyncio.get_event_loop()
    loop.call_later(100, stop)
    task = loop.create_task(periodic())

    try:
        loop.run_until_complete(task)
    except asyncio.CancelledError:
        pass



def populate_playlist():
    global PLAYLIST_PATH

    files = []

    for file in os.listdir(PLAYLIST_PATH):
        if file.endswith(".mp3"):
            files.append(os.path.join(PLAYLIST_PATH, file))

    print("Populating playlist..")

    for file in files:
        print(file)
        queue.put(file)


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')


@bot.event
async def on_ready():
    global text_channel
    text_channel = bot.get_channel(TEXT_CHANNEL_ID)
    await text_channel.send('The bot is online.')

    populate_playlist()

    global KEEP_PLAYING
    KEEP_PLAYING = 1


def play_next(ctx):
    reset_time()
    voice = get(bot.voice_clients, guild=ctx.guild)

    player = voice.stop()

    if KEEP_PLAYING is 0:
        return

    if queue.empty() is True:
        populate_playlist()

    file_path = queue.get()

    print("Playing: " + file_path)

    lam = lambda e: (
        queue.task_done(),
        play_next(ctx)
    )

    source = FFmpegPCMAudio(file_path)
    player = voice.play(source, after=lam)


@bot.command()
async def clear_songs(ctx):
    global queue

    queue.queue.clear()


@bot.command()
async def change_playlist(ctx, arg1):
    global PLAYLIST_PATH

    if arg1 == 'elevator':
        PLAYLIST_PATH = 'playlists/elevator/'
    elif arg1 == 'intermission':
        PLAYLIST_PATH = 'playlists/intermission/'
    elif arg1 == 'goodbye':
        PLAYLIST_PATH = 'playlists/goodbye/'
    else:
        PLAYLIST_PATH = 'playlists/default'


@bot.command()
async def get_playlist(ctx):
    global PLAYLIST_PATH
    print (PLAYLIST_PATH)


@bot.command()
async def gettime(ctx):
    time = get_time()
    print(time)


def store_message(user, message, time):
    if current_track_title == '':
        return

    payload = {
        'podcast_title': current_track_title,
        'user': user,
        'comment_body' : message,
        'time' : time
    }
    r = requests.post('http://localhost:6969/comment/joe-rogan-sam-harris', data=payload)


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # keep bot commands running
    # https://stackoverflow.com/questions/49331096/why-does-on-message-stop-commands-from-working
    await bot.process_commands(message)

    if message.content.startswith(CMD_PREFIX):
        return

    channel = message.channel

    store_message(message.author, message.content, get_time())


@bot.command()
async def start(ctx):
    await play(ctx)

@bot.command()
async def play(ctx):
    channel = ctx.message.author.voice.channel

    if not channel:
        await ctx.send("You are not connected to a voice channel")
        return

    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()

    if queue.empty() is not True:
        file_path = queue.get()
    else:
        populate_playlist()
        file_path = queue.get()

    global current_track_title
    current_track_title = file_path.split('/')[-1]
    if current_track_title.endswith('.mp3'):
        current_track_title = current_track_title[:-4]

    print("Playing: " + file_path)
    await text_channel.send("Playing: " + file_path)

    reset_time()

    get_track_length(file_path)

    lam = lambda e: (
        queue.task_done(),
        play_next(ctx)
    )

    source = FFmpegPCMAudio(file_path)
    player = voice.play(source, after=lam)


@bot.command()
async def stop(ctx):
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)

    global KEEP_PLAYING
    KEEP_PLAYING = 0
    player = voice.stop()


@bot.command()
async def next(ctx):
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)

    global KEEP_PLAYING
    KEEP_PLAYING = 1
    player = voice.stop()


### + CRAIG + ###


@bot.command()
async def rec(ctx):
    channel = ctx.message.author.voice.channel

    await text_channel.send(':craig:, join')


@bot.command()
async def stop_rec(ctx):
    channel = ctx.message.author.voice.channel

    await text_channel.send(':craig:, leave')


### - CRAIG - ###



#client.run(TOKEN)
bot.run(TOKEN)
