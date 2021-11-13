from discord.ext import commands, tasks
from discord import utils, Embed

from dotenv import dotenv_values

import os, sys, time
import random

from monitor import Monitor



config = dotenv_values(sys.path[0] + '\\.env')
CHANNEL = config['channel']
BOT_KEY = config['bot_key']
MAINLOOP_TIME = config['mainloop_time']

client = commands.Bot(command_prefix='.')
monitors = []



# Functions
#region
def parse_kwargs(args) -> dict:
    kwargs = {}
    
    for arg in args:
        string = str(arg)

        if '=' in string:
            key, value = string.split('=', 1)
            kwargs[key] = value

    return kwargs


def create_monitor(collection, **filters) -> str:
    monitor = Monitor(collection, **filters)
    
    text = f'{collection} is not valid'

    if monitor.valid:
        monitors.append(monitor)
        text = f'Monitor **created** at `{len(monitors) - 1}`'

    return text


def delete_monitor(id) -> str:
    text = f'`{id}` out of bounds (0-{len(monitors)})'

    id = int(id)
    text = len(monitors)

    if id in range(len(monitors)):
        monitors.pop(id)
        text = f'Monitor at `{id}` **removed**'

    return text


async def update(channel):
    all_nfts = []

    for i, monitor in enumerate(monitors):
        nfts = monitor.update()
        if nfts:
            all_nfts += nfts

    for nft in all_nfts:
        await channel.send(embed=Embed().set_image(url=nft['img']))
        await channel.send(
            f'''```\
Rank: **{nft['rank']}**\n\
Name: {nft['name']} | ID: {nft['id']} \n\
Price: {nft['price']} SOL | Token: {nft['token']}\n\
Attributes: {nft['atts']}
            ```''')

#endregion



# Biding
#region
@client.event
async def on_ready():
    print('Bot ready')  

    channel = utils.get(client.get_all_channels(), name=CHANNEL)
    main_loop.start(channel)


@client.command(help=': Check bot\'s latency')
async def ping(ctxt):
    ping_choices = [
        'Pong',
        'Whabam',
        'I am speed',
        'Bang'
    ]

    await ctxt.send(f'{random.choice(ping_choices)}! {int(client.latency * 1e3)}ms')  


@client.command(help=': Bot will repeat your text')
async def say(ctxt, text):
    choice = random.randrange(0, 100)

    if choice < 5:
        text = 'Exactly!'

    if 'gay' in text.lower():
        text = 'True'

    await ctxt.send(text)


@client.command(help=': List of all monitors', aliases=['a, al, am'])
async def all(ctxt):
    choice = random.randrange(0, 100)

    if choice < 5:
        await ctxt.send('No')
        return
    
    if len(monitors) == 0:
        await ctxt.send('No monitors!')
        return

    for i, monitor in enumerate(monitors):
        status = 'Active' if monitor.valid else 'Not supported'
        await ctxt.send(f'`Monitor at {i}, coll: {monitor.collection}, status: {status}`')


@client.group(pass_context=True, aliases=['m'])
async def monitor(ctxt):
    if ctxt.invoked_subcommand is None:
        await ctxt.send('Invalid sub command...  😕')


@monitor.command(help=': Create monitor', aliases=['c'])
async def create(ctxt, collection, *args):
    kwargs = parse_kwargs(args)
    text = create_monitor(collection, **kwargs)

    await ctxt.send(text)


@monitor.command(help=''': Remove monitor''', aliases=['r', 'd'])
async def delete(ctxt, id):
    text = delete_monitor(id)
    await ctxt.send(text)


@tasks.loop(seconds=int(MAINLOOP_TIME))
async def main_loop(channel):
    await update(channel)
    print(f'Loop done {time.asctime()}')
#endregion

client.run(BOT_KEY)

