import creds
import discord
from creds import *
from discord.ext import commands

client = commands.Bot(command_prefix='.')

@client.event
async def on_ready():
    print(f'SparkIEEE has logged in as {client.user}')

@client.command()
async def projects(ctx):
    msg = 'Here is a list of our currently active projects:\n' \
          f'```{list(PROJECTS.keys())}```\n' \
          f'For more info about a particular project, use the `{client.command_prefix}project project_name` command.'
    await ctx.send(msg)

@client.command()
async def project(ctx, *args):
    if len(args) == 0:
        err_msg = 'Please supply the command with a project argument.\n' \
                  f'For example, `{client.command_prefix}project OPS` or `{client.command_prefix}project Micromouse`.'
        await ctx.send(err_msg)
    elif args[0].upper() not in PROJECTS.keys():
        err_msg = f'`{args[0]}` is not a valid project.\n' \
                  'Here is a list of our currently active projects:\n' \
                  f'```{list(PROJECTS.keys())}```\n'
        await ctx.send(err_msg)
    else:
        info = PROJECTS[args[0].upper()]
        leads = '\n'.join([f'{name}: @{id}' for name, id in info['LEADS'].items()])
        msg = f'**{args[0]} Project Leads:**\n' \
              f'```{leads}```' \
              f'**{args[0]} Links:**'
        e = discord.Embed(title=f'{args[0]} Facebook Group',
                          url=f'{info["FB_GROUP"]}')
        await ctx.send(msg, embed=e)

client.run(BOT_TOKEN)

