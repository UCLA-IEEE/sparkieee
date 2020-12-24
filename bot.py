import creds
import discord
from creds import *
from discord.ext import commands

client = commands.Bot(command_prefix='.', help_command=None)

@client.event
async def on_ready():
    print(f'SparkIEEE has logged in as {client.user}')

@client.command()
async def help(ctx):
    msg = 'Hello! I am **SparkIEEE**, an IEEE Discord bot created by Bryan Wong. \n' \
          'I can assist you with checking off project completion and more!\n\n' \
          f'**Commands:**\n' \
          '```projects          directory of current active projects\n' \
          'project p         look up project lead info, deadlines, links, and more for p```' \
          f'To run a command, type in `{client.command_prefix}[command]`.\n\n' \
          '**Links:**\n' \

    # todo: add image urls/descriptions
    ieee_website = discord.Embed(title='IEEE at UCLA Website',
                              url='https://ieeebruins.com/')
    ieee_linktree = discord.Embed(title='IEEE Linktree',
                                 url='https://linktr.ee/uclaieee')
    github = discord.Embed(title='SparkIEEE on Github',
                              url='https://github.com/bryanjwong/sparkieee')

    await ctx.send(msg)
    await ctx.send(embed=ieee_website)
    await ctx.send(embed=ieee_linktree)
    await ctx.send(embed=github)

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

