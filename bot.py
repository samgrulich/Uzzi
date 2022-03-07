from discord.ext import commands, tasks
from discord import utils, Embed

from dotenv import dotenv_values

import os
import sys
import time
import random

if not os.path.exists("src/"):
    raise Exception("Uzzi module not found")

sys.path.append("src/")

import meden
from monitor import Monitor
from crossplatform import core_exceptions as errors
from crossplatform import core_types


config = dotenv_values(sys.path[0] + '/.env')
BOT_KEY = config['key']
CHANNEL = config['channel']
MAINLOOP_TIME = config['interval']

client = commands.Bot(command_prefix='.')

magiceden = meden.Magiceden()
monitor = Monitor(magiceden)



# Functions
# region
def parse_kwargs(args) -> dict:
    kwargs = {}

    for arg in args:
        string = str(arg)

        if '=' in string:
            key, value = string.split('=', 1)
            kwargs[key] = value

    return kwargs


def create_monitor(collectionId: str, rankId: str, **filters) -> str:
    try:
        monitor.add_collection(collectionId, rankId, **filters)
    except errors.NotValidQuerry:
        return f'Not valid collection' # not valid collection
    
    monitor.update()

    return f'Monitor for `{collectionId}` **created**, `{len(monitor.collections)}` collections'


def delete_monitor(id: str) -> str:
    try:
        monitor.remove_collection(id)
    except errors.NotValidQuerry:
        return f'' # not valid collection

    return f'Monitor for `{id}` **deleted**'


async def update(channel):
    try:
        snapshots = monitor.update()
    except errors.General as e:
        return
    except errors.NetworkError as e:
        e.print()
        return

    if not snapshots:
        return

    for collectionId, snapshot in snapshots.items():
        for nft in snapshot.list:
            info_string = f'''\
(Magiceden)[{monitor.marketPage.apis[core_types.MarketPageAPIs.nft_querry](nft.token)}]
Rank: {nft.rank}
Name: {nft.name}
Price: **{nft.price}** SOL 
Attributes: \n'''

            for att_pair in nft.atts:
                key = att_pair["trait_type"]
                att_type = att_pair["value"]

                info_string += f' \t - {key}: {att_type} \n'

            embed = Embed()
            embed.set_author(name=f"Rank; Price {nft.price} SOL")
            # embed.set_thumbnail(url=nft['img'])
            embed.set_image(url=nft.img)
            embed.description = info_string.replace("\\", "")

            await channel.send(embed=embed)

# endregion


# Biding
# region
@client.event
async def on_ready():
    print('Bot ready')

    channel = utils.get(client.get_all_channels(), name=CHANNEL)

    seconds = int(time.time()) % 10
    time.sleep(10 - seconds)

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


@client.command(help=': List all monitors', aliases=['a, al, am, all, lall, list'])
async def all(ctxt):
    choice = random.randrange(0, 100)

    if choice < 5:
        if choice < 1:
            await ctxt.send('I don\'t think i will')
        else:
            await ctxt.send('No.')
        return

    if len(monitor.collections) == 0:
        await ctxt.send('No monitors!')
        return

    for i, collection in enumerate(monitor.collections):
        text = f'Monitor at {i}, coll: {collection.id}, \n filters: '
        for filterType in collection.filterData.data.keys():
            text += f'{filterType}, '

        await ctxt.send(f'```{text}```')


@client.group(pass_context=True, aliases=['m'])
async def monitorCMD(ctxt):
    if ctxt.invoked_subcommand is None:
        await ctxt.send('Invalid sub command...  😕')


@monitorCMD.command(help=': Create monitor', aliases=['c'])
async def create(ctxt, collectionId: str, rankId: str, *args):
    await ctxt.send('On it!')

    kwargs = parse_kwargs(args)
    text = create_monitor(collectionId, rankId, **kwargs)

    await ctxt.send(text)


@monitorCMD.command(help=''': Remove monitor''', aliases=['r', 'd', 'remove'])
async def delete(ctxt, id: str):
    text = delete_monitor(id)
    await ctxt.send(text)


# @monitorCMD.command(help=''': Change filters''', aliases=['change'])
# async def set(ctxt, id, *args):
#     kwargs = parse_kwargs(args)

#     id = int(id)

#     monitors[id].set_filters(**kwargs)

#     text = f'New filters for {id} are: '
#     for filter_, value in monitors[id].filters.items():
#         text += f'\n - {filter_}: {value}'

#     await ctxt.send(f'```{text}```')


@tasks.loop(seconds=int(MAINLOOP_TIME))
async def main_loop(channel):
    await update(channel)
    print(f'Loop done {time.asctime()}')
# endregion

client.run(BOT_KEY)
