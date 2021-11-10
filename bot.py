from discord.ext import commands, tasks
from discord import utils, File

from dotenv import dotenv_values

import os, sys, time

from code.monitor import Monitor
from code.data import RarityGetter 
from code.__init__ import PROJECT_PATH



config = dotenv_values(sys.path[0] + '\\.env')
CHANNEL = config['channel']
BOT_KEY = config['bot_key']
MAINLOOP_TIME = config['mainloop_time']

client = commands.Bot(command_prefix='.')
monitors = []
images = {}



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


async def create_monitor(ctxt, collection, **filters):
    monitor = Monitor(collection, **filters)
    monitors.append(monitor)

    await ctxt.send(f'Monitor wiht id: `{len(monitors) - 1}` **created**')


async def delete_monitor(ctxt, id):
    if not id in range(monitors.len()):
        await ctxt.send(f'ID: `{id}` is out of bounds (0-{monitors.len()})')
        return
    
    monitors.pop(id)
    await ctxt.send(f'Monitor wiht id: `{len(monitors) - 1}` **removed**')


async def load_images():
    for dir in os.listdir(f'{PROJECT_PATH}\\Graphs\\'):
        for img in os.listdir(f'{PROJECT_PATH}\\Graphs\\{dir}'):
            if not dir in images.keys():
                images[dir] = []
            
            image = None
            with open(f'{PROJECT_PATH}\\Graphs\\{dir}\\{img}', 'rb') as f:
                image = File(f)

            images[dir].append(image)


# async def show_graph(ctxt, collection, *args):
#     rarities = RarityGetter(collection)

#     attribs = args

#     if 'all' in args:
#         attribs = ['Background', 'Brain', 'Plant', 'Body', 'Neck', 'Arms', 'Face', 'Eyes', 'Headwear', 'Mask']

#     for attrib in range(len(attribs)):
#         filepath = f'{PROJECT_PATH}\\Graphs\\{collection}\\{attrib}.png'

#         # async with open(filepath, 'rb') as f:
#         #     picture = File(f)
#         #     await ctxt.send(file=picture)

#         await ctxt.send(file=images[collection][attrib])

#         rarities.plot_attribs(attrib, 'save', 'hide')

#         # with open(f'{PROJECT_PATH}\\Graphs\\{collection}\\{attrib}.png', 'r') as f:
#         #     await ctxt.send(file=File(f, 'new_filename.png'))


async def update(channel):
    filtered_data = {}

    for i, monitor in enumerate(monitors):
        filtered = monitor.update()
        if filtered:
            filtered_data[i] = filtered

    for key, value in filtered_data.items():
        await channel.send(f'Monitor {key} found this:')
        
        for time in value.keys():
            await channel.send(f'`{time}`') 

            for nft in value[time]:
                nft_data = nft['data']
                await channel.send(f'```{nft_data}```')

        print(value)
#endregion



# Biding
#region
@client.event
async def on_ready():
    print('Bot ready')  

    # await load_images()

    channel = utils.get(client.get_all_channels(), name=CHANNEL)
    main_loop.start(channel)


@client.command(help=': check bot\'s latency')
async def ping(ctxt):
    await ctxt.send(f'{int(client.latency * 1e3)}ms')  


@client.command(help=''': Create monitor''', aliases=['c'])
async def create(ctxt, collection, *args,):
    kwargs = parse_kwargs(args)
    await create_monitor(ctxt, collection, **kwargs)


@client.command(help=''': Remove monitor''', aliases=['r', 'd'])
async def delete(ctxt, id):
    await delete_monitor(ctxt, int(id))


@client.command()
async def show_graph(ctxt, collection, *args):
    await show_graph(ctxt, collection, *args)


@tasks.loop(seconds=int(MAINLOOP_TIME))
async def main_loop(channel):
    await update(channel)
    print(f'Loop done {time.asctime()}')
#endregion

client.run(BOT_KEY)

