import asyncio
import discord
import pytz
from creds import *
from datetime import datetime, timedelta
from discord.ext import commands, tasks
from sheet_transformer import SheetTransformer

lab_open = True
client = commands.Bot(command_prefix='.', help_command=None)
labhour_msg = None

# Colors for embeds
color = 0xffbb00
error_color = 0xff0000

# If the message already exists, no need to create it again
async def join_roles_announcement():
    text = "React to this message with your project's emoji to be assigned that role! Unreact to reverse it.\n" \
           "You'll get access to a project-specific text channel."
    role_channel = client.get_channel(ROLE_CHANNEL_ID)
    if role_channel:
        message = await role_channel.send(text)
        await message.add_reaction(emoji=client.get_emoji(OPS_EMOJI))
        await message.add_reaction(emoji=client.get_emoji(MM_EMOJI))
        await message.add_reaction(emoji=client.get_emoji(AIR_EMOJI))
        await message.add_reaction(emoji=client.get_emoji(DAV_EMOJI))
        await message.add_reaction(emoji=client.get_emoji(WRAP_EMOJI))

@client.event
async def on_ready():
    print(f'SparkIEEE has logged in as {client.user}')
    await client.change_presence(activity=discord.Game(name=f'what is love? 🤖 | {client.command_prefix}help'))
    # await join_roles_announcement()

@client.event
async def on_raw_reaction_add(payload):
    if payload.message_id != REACT_MSG_ID:
        return
    member = payload.member
    guild = member.guild

    role = None
    if payload.emoji == client.get_emoji(OPS_EMOJI):
        role = discord.utils.get(guild.roles, name="OPS")
    if payload.emoji == client.get_emoji(MM_EMOJI):
        role = discord.utils.get(guild.roles, name="Micromouse")
    if payload.emoji == client.get_emoji(AIR_EMOJI):
        role = discord.utils.get(guild.roles, name="Aircopter")
    if payload.emoji == client.get_emoji(DAV_EMOJI):
        role = discord.utils.get(guild.roles, name="DAV")
    if payload.emoji == client.get_emoji(WRAP_EMOJI):
        role = discord.utils.get(guild.roles, name="WRAP")
    if role:
        await member.add_roles(role)

@client.event
async def on_raw_reaction_remove(payload):
    if payload.message_id != REACT_MSG_ID:
        return
    guild = await client.fetch_guild(payload.guild_id)
    member = await guild.fetch_member(payload.user_id)

    role = None
    if payload.emoji == client.get_emoji(OPS_EMOJI):
        role = discord.utils.get(guild.roles, name="OPS")
    if payload.emoji == client.get_emoji(MM_EMOJI):
        role = discord.utils.get(guild.roles, name="Micromouse")
    if payload.emoji == client.get_emoji(AIR_EMOJI):
        role = discord.utils.get(guild.roles, name="Aircopter")
    if payload.emoji == client.get_emoji(DAV_EMOJI):
        role = discord.utils.get(guild.roles, name="DAV")
    if payload.emoji == client.get_emoji(WRAP_EMOJI):
        role = discord.utils.get(guild.roles, name="WRAP")
    if role:
        await member.remove_roles(role)

@client.command()
async def help(ctx):
    prefix = client.command_prefix
    description = 'Hello! I am **SparkIEEE**, an IEEE Discord bot created by Bryan Wong. \n' \
         f'To run a command, type in `{prefix}[command]`.\n' \
         f'For fields with multiple words (e.g. names), use quotation marks `""`\n\n'
    # Make new embed with description
    embed = discord.Embed(title='Help', description=description, color=color)

    commands_msg = f'```ahk\n\n' \
        f'[1] projects - Directory of current active projects\n' \
        f'[2] project p - Deadlines, contact info, links, and more for project p\n' \
        f'[3] status p u - Project completion status in project p for member u\n' \
        f'[4] labhours - Check whose lab hours it is right now\n' \
        f'[5] labhours o - Look up lab hours for officer o\n```'
    # Add commands as new field to embed
    embed.add_field(name='Commands', value=commands_msg, inline=False)

    project_leads_msg = f'```ahk\n\n' \
        f'[1] checkoff p a u [v] - Check off user u for project p, assignment a. v is the new value; the default value is "x".\n' \
        f'To add notes, {prefix}checkoff p a u "checkpoint 1"\n' \
        f'[2] addassign p a d - Add assignment a, due on date d, to project p\n' \
        f'[3] extend p a d - Change deadline to d for assignment a in project p\n' \
        f'[4] closelab - Disable lab hours reminders for the day\n' \
        f'[5] openlab - Reenable lab hours reminders, starting tomorrow```\n'
    
    # Only show these commands when executed by an officer!
    if is_officer(ctx):
        # Add project leads commands field to the embed
       embed.add_field(name='Project Lead Commands', value=project_leads_msg, inline=False)
    
    # Can turn this into a 2nd embed if you want thumbnails
    embed.add_field(name='IEEE at UCLA Website', value='[Website](http://ieeebruins.com/)', inline=True)
    embed.add_field(name='IEEE Linktree', value='[Linktree](https://linktr.ee/uclaieee)', inline=True)
    embed.add_field(name='SparkIEEE on Github', value='[Github](https://github.com/bryanjwong/sparkieee)', inline=True)

    await ctx.send(embed=embed)


@client.command()
async def projects(ctx):
    msg = 'Here is a list of our currently active projects:\n' \
          f'```\n{fmt_projects()}```\n' \
          f'For more info about a particular project, use the `{client.command_prefix}project project_name` command.'
    embed = discord.Embed(title='Projects', description=msg, color=color)
    await ctx.send(embed=embed)

@client.command()
async def project(ctx, *args):
    if len(args) == 0:
        err_msg = 'Please supply the command with a project argument.\n' \
                  f'For example, `{client.command_prefix}project OPS` or `{client.command_prefix}project Micromouse`.'
        await ctx.send(err_msg)
    elif args[0].upper() not in PROJECTS.keys():
        err_msg = f'`{args[0]}` is not a valid project.\n' \
                  'Here is a list of our currently active projects:\n' \
                  f'```{fmt_projects()}```\n'
        await ctx.send(err_msg)
    else:
        info = PROJECTS[args[0].upper()]
        projects = ''
        if 'SPREAD_ID' in info:
            try:
                projects = f'```\n{sheets.lookup(info["SPREAD_ID"])}```'
            except Exception as e:
                await ctx.send(e)
        nl = '\n- '
        leads = '\n'.join([f'{name}: @{id}\n'
                           f'- {nl.join(sheets.get_lab_hours_by_name(LAB_HOURS, name))}\n'
                           for name, id in info['LEADS'].items()])

        project_full_name = PROJECTS[args[0].upper()]["FULL_NAME"]
        # Only show the full name of the project if it's not an abbreviation
        description = project_full_name if args[0].upper() != project_full_name else '' 

        # Embed for a specific project
        embed = discord.Embed(title=f'{args[0]} Information', description=PROJECTS[args[0].upper()]["FULL_NAME"], color=color)
        if 'SPREAD_ID' in info:
            embed.add_field(name=f'{args[0]} Projects:', value=f'{projects}', inline=False)
        embed.add_field(name=f'{args[0]} Project Leads:', value=f'```{leads}```', inline=False)
        embed.add_field(name='Links', value=f'[{args[0]} Facebook Group]({info["FB_GROUP"]})', inline=False)
    
        await ctx.send(embed=embed)

@client.command()
async def status(ctx, *args):
    if len(args) < 2:
        err_msg = 'Please supply the command with project and member name arguments.\n' \
            f'For example, `{client.command_prefix}status OPS "Kathy Daniels"` or ' \
            f'`{client.command_prefix}status Micromouse 1`.'
        await ctx.send(err_msg)
    elif is_invalid_name(args[1]) or args[0].upper() not in PROJECTS.keys():
        err_msg = f'`{args[0]}`` is not a valid project.\n'
        await ctx.send(err_msg)
        await projects(ctx)
    else:
        info = PROJECTS[args[0].upper()]
        if 'SPREAD_ID' in info:
            try:
                # Turn everything starting from the 1st argument into a string
                name = get_name_from_args(args[1:])

                title = f'**{name}\'s {args[0].upper()} Project Status:**'
                description = f'```\n{sheets.lookup(info["SPREAD_ID"], name=name)}```'
                embed = discord.Embed(title=title, description=description, color=color)
                await ctx.send(embed=embed)
            except Exception as e:
                await ctx.send(e)
        else:
            msg = f'{args[0]} does not currently have a checkoff sheet.'
            await ctx.send(msg)

@client.command()
async def labhours(ctx, *args):
    if len(args) == 0:
        if not lab_open:
            await ctx.send('The Lab is closed today. For a full list of lab hours, visit our lab website http://ieeebruins.com/lab.')
            return
        try:
            date = datetime.now(tz=pytz.utc)
            date = date.astimezone(pytz.timezone('US/Pacific'))
            shift_str, officers = sheets.get_lab_hours_by_time(LAB_HOURS, date)
            # msg = f'These officers have Lab Hours for **{shift_str}**:\n' \
            #       f'```{officers}```'

            # Lab hours embed for all officers
            title = f"Lab Hours for {shift_str}"
            description = f'```{officers}```'
            embed = discord.Embed(title=title, description=description, color=color)
            
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(e)
    else:
        try:
            # This command is buggy when multiple officers with same first name.
            #     Ex: labhours David returns lab hours of BOTH Davids
            hours = sheets.get_lab_hours_by_name(LAB_HOURS, args[0])
            if not is_invalid_name(args[0]) and hours:
                hours_string = '\n'.join(hours)

                # Lab hours embed for an officer
                title = f"{args[0]}'s Lab Hours"
                description = f'```{hours_string}```'
                embed = discord.Embed(title=title, description=description, color=color)

                await ctx.send(embed=embed)
            else:
                msg = f'**{args[0]}** is either not an officer or does not have lab hours.\n' \
                      'A full list of lab hours can be found at our lab website http://ieeebruins.com/lab.'
                await ctx.send(msg)
        except Exception as e:
            await ctx.send(e)

@client.command()
@commands.has_role("officers")
async def checkoff(ctx, *args):
    if len(args) < 3:
        err_msg = 'Please supply the command with project, member name, and assignment arguments.\n' \
            f'For example, `{client.command_prefix}checkoff Aircopter "Lab 1" "Jay Park"`.'
        await ctx.send(err_msg)
    elif args[0].upper() not in PROJECTS.keys():
        err_msg = f'`{args[0]}` is not a valid project.\n' \
            'Here is a list of our currently active projects:\n' \
            f'```{fmt_projects()}```\n'
        await ctx.send(err_msg)
    else:
        info = PROJECTS[args[0].upper()]
        new_val = 'x' if len(args) < 4 else args[3]
        msg = ''
        if 'SPREAD_ID' in info:
            # try:
            # All arguments including the third arg and after are counted as the name
            name = get_name_from_args(args[2:])
            old_val = sheets.checkoff(info["SPREAD_ID"], assignment=args[1], name=name, val=new_val)
            if old_val == 'x':
                msg = f'**{name}** has already been checked off for **{args[0]} {args[1]}**.\n'
            else:
                # Successful check off embed
                title = f"Checked off {name}"
                description = f'**{name}** has been checked off for **{args[0]} {args[1]}**!\n' \
                      f'```Value changed from "{old_val}" to "{new_val}"```'
                embed = discord.Embed(title=title, description=description, color=color)
                
                # Set msg variable to be the embed
                msg = embed

            # except Exception as e:
            #     await ctx.send(e)
        else:
            msg = f'{args[0]} does not currently have a checkoff sheet.'
        
        # Check if it's a string or embed
        if (type(msg) is str):
            await ctx.send(msg)
        else:
            await ctx.send(embed=embed)

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
            f'```{fmt_projects()}```\n'
        await ctx.send(err_msg)
    else:
        info = PROJECTS[args[0].upper()]
        msg = ''
        if 'SPREAD_ID' in info:
            try:
                sheets.add_assignment(info["SPREAD_ID"], args[1], args[2])
                msg = f'Successfully added assignment **{args[1]}** to the **{args[0]}** spreadsheet, due **{args[2]}**'
            except Exception as e:
                await ctx.send(e)
                return
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
            f'```{fmt_projects()}```\n'
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

@tasks.loop(hours=1)
async def lab_hours_reminder():
    global labhour_msg
    date = datetime.now(tz=pytz.utc)
    date = date.astimezone(pytz.timezone('US/Pacific'))

    if not lab_open or date.weekday() >= 5:  # weekend
        return
    if date.hour < 10 or date.hour > 19:
        return
    try:
        if labhour_msg:
            await labhour_msg.delete()
        if date.hour == 18:
            msg = f'Lab Hours have officially ended. For a full list of lab hours, visit http://ieeebruins.com/lab.'
        else:
            shift_str, officers = sheets.get_lab_hours_by_time(LAB_HOURS, date)
            if not officers:
                officers = 'None'
            # Lab hours embed for all officers
            title = f"Lab Hours for {shift_str}"
            description = f'```{officers}```'
            embed = discord.Embed(title=title, description=description, color=color)

            # Somewhat confusing, but the message to be displayed is set to the embed
            msg = embed

        lab_channel = client.get_channel(LAB_CHANNEL_ID)
        if lab_channel:
            # Check if it's a rich embed or not
            if type(msg) is str:
                labhour_msg = await lab_channel.send(msg)
            else:
                labhour_msg = await lab_channel.send(embed=msg)
    except Exception as e:
        print(e)

@lab_hours_reminder.before_loop
async def before():
    await client.wait_until_ready()
    date = datetime.now(tz=pytz.utc)
    date = date.astimezone(pytz.timezone('US/Pacific'))

    if date.hour == 23:
        future = pytz.timezone('US/Pacific').localize(datetime(date.year, date.month, date.day, LAB_HOURS_START_TIME, 0))
        future += timedelta(days=1)
    else:
        future = pytz.timezone('US/Pacific').localize(datetime(date.year, date.month, date.day, date.hour + 1, 0))
    wait_period = (future - date).total_seconds()
    print(f'Waiting until {future} before starting lab hour reminders ({wait_period} seconds).')
    await asyncio.sleep(wait_period)
    print("Beginning Lab Hours scheduled reminders")


# Helper functions added by Raj

# Simple error embed
def error_embed(msg):
    return discord.Embed(title='Error', description=msg, color=error_color)

# Better formatting for .projects
def fmt_projects():
  res = ''
  for project_name in PROJECTS.keys():
    # If it's 4 letters or less, we assume it's an abbreviation
    if len(project_name) < 5:
      res += project_name
    else:
      res += project_name.lower().capitalize()
    # Separate each entry w/ newline
    res += '\n'
  return res.strip()

# Capitalize each line on a new line
def capitalize_on_separator(some_str, separator):
    # Split at each newline to turn the string into a list
    some_list = some_str.split(separator)
    # Capitalize each line, turn map into a list           
    some_list = list(map(lambda line: line.capitalize(), some_list))
    # Turn the list into a string separated by the separator

    return separator.join(some_list)

# Prevents bug with detecting row numbers or column labels as a name
# If it's 2 characters or smaller it's illegal
def is_invalid_name(some_str):
    return len(some_str.strip()) < 2

# Check if user has officer role
# Needed for checking inside of a function
def is_officer(ctx):
    role_names = [role.name for role in ctx.message.author.roles]
    if 'officers' in role_names:
        return True
    return False

# TO-DO: Come up with a better name for this function?
# If we do .status OPS Joe Schmoe, this just captures Joe Schmoe as its own string
# No need to use quotes anymore with this
def get_name_from_args(args):
    name = ''
    for i in range(0, len(args)):
        name += " " + args[i]
    return name.strip()

sheets = SheetTransformer()
lab_hours_reminder.start()
client.run(BOT_TOKEN)
