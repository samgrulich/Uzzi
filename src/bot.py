from discord.ext import commands, tasks
from discord import utils, Embed

from dotenv import dotenv_values

import os
import sys
import time
import random

from monitor import Monitor


config = dotenv_values(sys.path[0] + '\\.env')
CHANNEL = config['channel']
BOT_KEY = config['bot_key']
MAINLOOP_TIME = config['mainloop_time']

client = commands.Bot(command_prefix='.')
monitors = []


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


def create_monitor(collection, **filters) -> str:
    monitor = Monitor(collection, **filters)

    text = f'{collection} is not valid'

    # if monitor.valid:
    monitors.append(monitor)
    text = f'Monitor **created** at `{len(monitors) - 1}`'

    return text


def delete_monitor(id) -> str:
    text = f'`{id}` out of bounds (0-{len(monitors)})'

    id = int(id)
    text = len(monitors)

    if id in range(len(monitors)):
        monitors.pop(id)
        text = f'Monitor at `{id}` **deleted**'

    return text


async def update(channel):
    for monitor in monitors:
        nfts = monitor.update()

        if not nfts:
            return 

        for nft in nfts:
            nft = nft.vars()

            # BUG: token parsing may not work for solanart
            info_string = f'''\
Rank: **{nft['rank']}** ([{monitor.collection.rank_tuple.supported_page.id}]({monitor.collection.rank_tuple.supported_page.get_nft_url(nft['id'])})) \
                        ([{monitor.collection.collection_tuple.supported_page.id}]({monitor.collection.collection_tuple.supported_page.get_nft_url(nft['token'])}))\n\
Name: {nft['name']} | ID: {nft['id']} \n\
Price: **{nft['price']}** SOL | Token: {nft['token']}\n\
Attributes: \n'''

            for key, att_type in nft['atts'].items():
                info_string += f' \t - {key}: {att_type} \n'

            embed = Embed()
            embed.set_author(name=f"Rank: {nft['rank']}; Price {nft['price']} SOL")
            # embed.set_thumbnail(url=nft['img'])
            embed.set_image(url=nft['img'])
            embed.description = info_string

            await channel.send(embed=embed)

# endregion


# Biding
# region
@client.event
async def on_ready():
    print('Bot ready')

    channel = utils.get(client.get_all_channels(), name=CHANNEL)

    seconds = int(time.time()) % 10
    time.sleep(seconds)

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
        if choice < 1:
            await ctxt.send('I don\'t think i will')
        else:
            await ctxt.send('No.')
        return

    if len(monitors) == 0:
        await ctxt.send('No monitors!')
        return

    for i, monitor in enumerate(monitors):
        # status = 'Active' if monitor.valid else 'Not supported'
        status = 'Active'

        text = f'Monitor at {i}, coll: {monitor.collection.id}, status: {status}, \n filters: '
        for filter_, value in monitor.filters.items():
            text += f'\n\t - {filter_}: {value}'


        await ctxt.send(f'```{text}```')


@client.group(pass_context=True, aliases=['m'])
async def monitor(ctxt):
    if ctxt.invoked_subcommand is None:
        await ctxt.send('Invalid sub command...  😕')


@monitor.command(help=': Create monitor', aliases=['c'])
async def create(ctxt, collection, *args):
    await ctxt.send('On it!')

    kwargs = parse_kwargs(args)
    text = create_monitor(collection, **kwargs)

    await ctxt.send(text)


@monitor.command(help=''': Remove monitor''', aliases=['r', 'd'])
async def delete(ctxt, id):
    text = delete_monitor(id)
    await ctxt.send(text)


@monitor.command(help=''': Change filters''', aliases=['change'])
async def set(ctxt, id, *args):
    kwargs = parse_kwargs(args)

    id = int(id)

    monitors[id].set_filters(**kwargs)

    text = f'New filters for {id} are: '
    for filter_, value in monitors[id].filters.items():
        text += f'\n - {filter_}: {value}'

    await ctxt.send(f'```{text}```')


@tasks.loop(seconds=int(MAINLOOP_TIME))
async def main_loop(channel):
    await update(channel)
    print(f'Loop done {time.asctime()}')
# endregion

client.run(BOT_KEY)
