import asyncio
import discord
import pytz
from creds import *
from datetime import datetime, timedelta
from discord.ext import commands, tasks
from sheet_transformer import SheetTransformer

lab_open = True
client = commands.Bot(command_prefix='.', help_command=None)

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name=f'what is love? 🤖 | {client.command_prefix}help'))
    print(f'SparkIEEE has logged in as {client.user}')

@client.command()
async def help(ctx):
    msg = 'Hello! I am **SparkIEEE**, an IEEE Discord bot created by Bryan Wong. \n' \
         f'To run a command, type in `{client.command_prefix}[command]`.\n' \
         f'For fields with multiple words (e.g. names), use quotation marks `""`\n\n' \
         f'**Commands:** \n' \
          '```projects             directory of current active projects\n\n' \
          'project p            lookup project deadlines, contact info, links, and more\n\n' \
          'status p u           lookup project completion status of member u in project p\n\n' \
          'labhours             whose lab hours is it right now?\n\n' \
          'labhours o           lookup lab hours for officer o\n```\n' \
          '**Project Lead Commands:**\n' \
          '```checkoff p a u [v]   checkoff user u for project p, assignment a\n' \
          '                     v is the new value, by default it\'s "x"\n' \
         f'                     to add notes, {client.command_prefix}checkoff p a u "checkpoint 1"\n\n' \
          'addassign p a d      add assignment a, due on date d, to project p\n\n' \
          'extend p a d         change project p\'s assignment a deadline to d\n\n' \
          'closelab             disable lab hours reminders for the day\n\n' \
          'openlab              reenable lab hours reminders, starting tomorrow```\n' \
          '**Links:**\n'

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
        projects = ''
        if 'SPREAD_ID' in info:
            try:
                projects = f'**{args[0]} Projects:**'\
                           f'```{sheets.lookup(info["SPREAD_ID"])}```'
            except Exception as e:
                await ctx.send(e)
        nl = '\n- '
        leads = '\n'.join([f'{name}: @{id}\n'
                           f'- {nl.join(sheets.get_lab_hours_by_name(LAB_HOURS, name))}\n'
                           for name, id in info['LEADS'].items()])
        msg = f'{projects}\n' \
              f'**{args[0]} Project Leads:**\n' \
              f'```{leads}```\n' \
              f'**{args[0]} Links:**'
        e = discord.Embed(title=f'{args[0]} Facebook Group',
                          url=f'{info["FB_GROUP"]}')
        await ctx.send(msg, embed=e)

@client.command()
async def status(ctx, *args):
    if len(args) < 2:
        err_msg = 'Please supply the command with project and member name arguments.\n' \
            f'For example, `{client.command_prefix}status OPS "Kathy Daniels"` or ' \
            f'`{client.command_prefix}status Micromouse "Justin Jianto"`.'
        await ctx.send(err_msg)
    elif args[0].upper() not in PROJECTS.keys():
        err_msg = f'`{args[0]}` is not a valid project.\n' \
            'Here is a list of our currently active projects:\n' \
            f'```{list(PROJECTS.keys())}```\n'
        await ctx.send(err_msg)
    else:
        info = PROJECTS[args[0].upper()]
        if 'SPREAD_ID' in info:
            try:
                msg = f'**{args[1]}\'s {args[0]} Project Status:**' \
                    f'```{sheets.lookup(info["SPREAD_ID"], name=args[1])}```'
            except Exception as e:
                await ctx.send(e)
        else:
            msg = f'{args[0]} does not currently have a checkoff sheet.'
        await ctx.send(msg)

@client.command()
async def labhours(ctx, *args):
    if len(args) == 0:
        if not lab_open:
            await ctx.send('The Lab is closed today. For a full list of lab hours, visit http://ieeebruins.com/lab.')
            return
        try:
            date = datetime.now(tz=pytz.utc)
            date = date.astimezone(pytz.timezone('US/Pacific'))
            shift_str, officers = sheets.get_lab_hours_by_time(LAB_HOURS, date)
            msg = f'These officers have Lab Hours for **{shift_str}**:\n' \
                  f'```{officers}```'
            await ctx.send(msg)
        except Exception as e:
            await ctx.send(e)
    else:
        try:
            # This command is buggy when multiple officers with same first name.
            #     Ex: labhours David returns lab hours of BOTH Davids
            hours = sheets.get_lab_hours_by_name(LAB_HOURS, args[0])
            if hours:
                hours_string = '\n'.join(hours)
                msg = f'Here are **{args[0]}**\'s Lab Hours:\n' \
                      f'```{hours_string}```'
            else:
                msg = f'**{args[0]}** is either not an officer or does not have lab hours.\n' \
                      'A full list of lab hours can be found at http://ieeebruins.com/lab'
            await ctx.send(msg)
        except Exception as e:
            await ctx.send(e)

@client.command()
@commands.has_role("officers")
async def checkoff(ctx, *args):
    if len(args) < 3:
        err_msg = 'Please supply the command with project, member name, and assignment arguments.\n' \
            f'For example, `{client.command_prefix}checkoff Aircopter "Jay Park" "Lab 1"` or ' \
            f'`{client.command_prefix}checkoff DAV "Fred Chu" "Deposit"`.'
        await ctx.send(err_msg)
    elif args[0].upper() not in PROJECTS.keys():
        err_msg = f'`{args[0]}` is not a valid project.\n' \
            'Here is a list of our currently active projects:\n' \
            f'```{list(PROJECTS.keys())}```\n'
        await ctx.send(err_msg)
    else:
        info = PROJECTS[args[0].upper()]
        new_val = 'x' if len(args) < 4 else args[3]
        msg = ''
        if 'SPREAD_ID' in info:
            try:
                old_val = sheets.checkoff(info["SPREAD_ID"], assignment=args[1], name=args[2], val=new_val)
                if old_val == 'x':
                    msg = f'**{args[2]}** has already been checked off for **{args[0]} {args[1]}**.\n'
                else:
                    msg = f'**{args[2]}** has been checked off for **{args[0]} {args[1]}**!\n' \
                          f'```Value changed from "{old_val}" to "{new_val}"```'
            except Exception as e:
                await ctx.send(e)
        else:
            msg = f'{args[0]} does not currently have a checkoff sheet.'
        await ctx.send(msg)

@client.command()
@commands.has_role("officers")
async def addassign(ctx, *args):
    if len(args) < 3:
        err_msg = 'Please supply the command with project, assignment, and deadline arguments.\n' \
            f'For example, `{client.command_prefix}addassign WRAP "Project 1" "2/11/2020"`'
        await ctx.send(err_msg)
    elif args[0].upper() not in PROJECTS.keys():
        err_msg = f'`{args[0]}` is not a valid project.\n' \
            'Here is a list of our currently active projects:\n' \
            f'```{list(PROJECTS.keys())}```\n'
        await ctx.send(err_msg)
    else:
        info = PROJECTS[args[0].upper()]
        msg = ''
        if 'SPREAD_ID' in info:
            # try:
            sheets.add_assignment(info["SPREAD_ID"], args[1], args[2])
            msg = f'Successfully added assignment **{args[1]}** to the **{args[0]}** spreadsheet, due **{args[2]}**'
            # except Exception as e:
            #     await ctx.send(e)
            #     return
        else:
            msg = f'{args[0]} does not currently have a checkoff sheet.'
        await ctx.send(msg)

@client.command()
@commands.has_role("officers")
async def extend(ctx, *args):
    if len(args) < 3:
        err_msg = 'Please supply the command with project, assignment, and new deadline arguments.\n' \
            f'For example, `{client.command_prefix}extend OPS "Project 1" "10/11/2020"`'
        await ctx.send(err_msg)
    elif args[0].upper() not in PROJECTS.keys():
        err_msg = f'`{args[0]}` is not a valid project.\n' \
            'Here is a list of our currently active projects:\n' \
            f'```{list(PROJECTS.keys())}```\n'
        await ctx.send(err_msg)
    else:
        info = PROJECTS[args[0].upper()]
        if 'SPREAD_ID' in info:
            try:
                old_deadline = sheets.change_deadline(info["SPREAD_ID"], args[1], args[2])
                msg = f'Successfully changed **{args[0]}** assignment **{args[1]}** deadline ' \
                      f'from **{old_deadline}** to **{args[2]}**'
            except Exception as e:
                await ctx.send(e)
        else:
            msg = f'{args[0]} does not currently have a checkoff sheet.'
        await ctx.send(msg)

@client.command()
@commands.has_role("officers")
async def closelab(ctx):
    global lab_open
    lab_open = False
    await ctx.send(f'The lab is now closed. Lab Hours reminders will cease until '
             f'the `{client.command_prefix}openlab` command is used to reopen it.')


@client.command()
@commands.has_role("officers")
async def openlab(ctx):
    global lab_open
    lab_open = True
    await ctx.send(f'The lab is now reopened. Lab Hours reminders will restart tomorrow.')

@tasks.loop(hours=1, count=9)
async def lab_hours_reminder():
    date = datetime.now(tz=pytz.utc)
    date = date.astimezone(pytz.timezone('US/Pacific'))
    if not lab_open or date.weekday() >= 5:  # weekend
        return
    try:
        if date.hour == 18:
            msg = f'Lab Hours have officially ended. For a full list of lab hours, visit http://ieeebruins.com/lab.'
        else:
            shift_str, officers = sheets.get_lab_hours_by_time(LAB_HOURS, date)
            msg = f'These officers have Lab Hours for **{shift_str}**:\n' \
                  f'```{officers}```'
        lab_channel = client.get_channel(LAB_CHANNEL_ID)
        if lab_channel:
            await lab_channel.send(msg)
    except Exception as e:
        print(e)

@lab_hours_reminder.before_loop
async def before():
    await client.wait_until_ready()
    date = datetime.today()
    future = datetime(date.year, date.month, date.day, LAB_HOURS_START_TIME, 0) # Lab Hours start at 10 am
    if date.hour >= LAB_HOURS_START_TIME:
        future += timedelta(days=1)
    wait_period = (future - date).total_seconds()
    print(f'Waiting until {future} before starting lab hour reminders.')
    await asyncio.sleep(wait_period)
    print("Beginning Lab Hours scheduled reminders")
    lab_channel = client.get_channel(LAB_CHANNEL_ID)
    if lab_channel and lab_open:
        await lab_channel.send('Good Morning! Lab Hours have begun!')

sheets = SheetTransformer()
lab_hours_reminder.start()
client.run(BOT_TOKEN)