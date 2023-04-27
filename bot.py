import asyncio
import discord
import pytz
from creds import *
from datetime import datetime, timedelta
from discord.ext import commands, tasks
from sheet_transformer import SheetTransformer
from firebase_api import FirebaseManager, ErrorCodes
import structlog

log = structlog.get_logger()

lab_open = True
client = commands.Bot(command_prefix=".", help_command=None)
labhour_msg = None

officer_title = "officers 2022-2023"
old_officer_title = "officers 2021-2022"
lab_buck_title = "lab buck admin"

# Colors for embeds
color = 0xFFBB00
error_color = 0xFF0000


# If the message already exists, no need to create it again
async def join_roles_announcement():
    text = (
        "React to this message with your project's emoji to be assigned that role! Unreact to reverse it.\n"
        "You'll get access to a project-specific text channel."
    )
    role_channel = client.get_channel(ROLE_CHANNEL_ID)
    if role_channel:
        message = await role_channel.send(text)
        await message.add_reaction(emoji=client.get_emoji(OPS_EMOJI))
        await message.add_reaction(emoji=client.get_emoji(MM_EMOJI))
        await message.add_reaction(emoji=client.get_emoji(PR_EMOJI))
        await message.add_reaction(emoji=client.get_emoji(DAV_EMOJI))
        await message.add_reaction(emoji=client.get_emoji(WRAP_EMOJI))


async def choose_pronouns_announcement():
    text = (
        "React to this message to assign yourself your pronouns! Unreact to reverse it.\n"
        "React with 🐢 for he/him\n"
        "React with 🦎 for he/they\n"
        "React with 🐬 for they/them\n"
        "React with 🦑 for she/they\n"
        "React with 🐙 for she/her\n"
        "React with 🐠 for any pronouns\n"
        "React with 🦀 for ask for my pronouns\n"
    )
    role_channel = client.get_channel(ROLE_CHANNEL_ID)
    if role_channel:
        message = await role_channel.send(text)
        await message.add_reaction(emoji="🐢")
        await message.add_reaction(emoji="🦎")
        await message.add_reaction(emoji="🐬")
        await message.add_reaction(emoji="🦑")
        await message.add_reaction(emoji="🐙")
        await message.add_reaction(emoji="🐠")
        await message.add_reaction(emoji="🦀")


async def join_outreach_announcement():
    text = "React to this message to join the ECE Outreach Committee channels.\n"
    role_channel = client.get_channel(ROLE_CHANNEL_ID)
    if role_channel:
        message = await role_channel.send(text)
        await message.add_reaction(emoji=client.get_emoji(OUTREACH_EMOJI))


async def join_amp_announcement():
    text = "React to this message to join the IEEE Alumni Mentorship Program (AMP) channels.\n"
    role_channel = client.get_channel(ROLE_CHANNEL_ID)
    if role_channel:
        message = await role_channel.send(text)
        await message.add_reaction(emoji="👥")


@client.event
async def on_ready():
    log.info(f"SparkIEEE has logged in as {client.user}")
    await client.change_presence(
        activity=discord.Game(
            name=f"taller than ASME duck 🦆 | {client.command_prefix}help"
        )
    )
    # await join_roles_announcement()
    # await choose_pronouns_announcement()
    # await join_outreach_announcement()
    # await join_amp_announcement()


@client.event
async def on_raw_reaction_add(payload):
    if (
        payload.message_id != PRONOUN_MSG_ID
        and payload.message_id != PROJECT_MSG_ID
        and payload.message_id != OUTREACH_MSG_ID
        and payload.message_id != AMP_MSG_ID
    ):
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
    if payload.emoji == client.get_emoji(PR_EMOJI):
        role = discord.utils.get(guild.roles, name="Pocket Racers")
    if payload.emoji.name == "🐢":
        role = discord.utils.get(guild.roles, name="he/him")
    if payload.emoji.name == "🦎":
        role = discord.utils.get(guild.roles, name="he/they")
    if payload.emoji.name == "🐬":
        role = discord.utils.get(guild.roles, name="they/them")
    if payload.emoji.name == "🦑":
        role = discord.utils.get(guild.roles, name="she/they")
    if payload.emoji.name == "🐙":
        role = discord.utils.get(guild.roles, name="she/her")
    if payload.emoji.name == "🐠":
        role = discord.utils.get(guild.roles, name="any pronouns")
    if payload.emoji.name == "🦀":
        role = discord.utils.get(guild.roles, name="ask for my pronouns")
    if payload.emoji == client.get_emoji(OUTREACH_EMOJI):
        role = discord.utils.get(guild.roles, name="Outreach Committee")
    if payload.emoji.name == "👥":
        role = discord.utils.get(guild.roles, name="Alumni Mentorship Program")
    if role:
        await member.add_roles(role)


@client.event
async def on_raw_reaction_remove(payload):
    if (
        payload.message_id != PRONOUN_MSG_ID
        and payload.message_id != PROJECT_MSG_ID
        and payload.message_id != OUTREACH_MSG_ID
        and payload.message_id != AMP_MSG_ID
    ):
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
    if payload.emoji == client.get_emoji(PR_EMOJI):
        role = discord.utils.get(guild.roles, name="Pocket Racers")
    if payload.emoji.name == "🐢":
        role = discord.utils.get(guild.roles, name="he/him")
    if payload.emoji.name == "🦎":
        role = discord.utils.get(guild.roles, name="he/they")
    if payload.emoji.name == "🐬":
        role = discord.utils.get(guild.roles, name="they/them")
    if payload.emoji.name == "🦑":
        role = discord.utils.get(guild.roles, name="she/they")
    if payload.emoji.name == "🐙":
        role = discord.utils.get(guild.roles, name="she/her")
    if payload.emoji.name == "🐠":
        role = discord.utils.get(guild.roles, name="any pronouns")
    if payload.emoji.name == "🦀":
        role = discord.utils.get(guild.roles, name="ask for my pronouns")
    if payload.emoji == client.get_emoji(OUTREACH_EMOJI):
        role = discord.utils.get(guild.roles, name="Outreach Committee")
    if payload.emoji.name == "👥":
        role = discord.utils.get(guild.roles, name="Alumni Mentorship Program")
    if role:
        await member.remove_roles(role)


@client.command()
async def help(ctx):
    prefix = client.command_prefix
    description = (
        "Hello! I am **SparkIEEE**, an IEEE Discord bot created by Bryan Wong. \n"
        "Special thanks to the following contributors: Raj Piskala, Bradley Schulz, Brandon Le.\n"
        f"To run a command, type in `{prefix}[command]`.\n"
        f'For fields with multiple words (e.g. names), use quotation marks `""`\n\n'
    )
    # Make new embed with description
    embed = discord.Embed(title="Help", description=description, color=color)

    commands_msg = (
        "```ahk\n\n"
        "[1] projects - Directory of current active projects\n"
        "[2] project p - Deadlines, contact info, links, and more for project p\n"
        "[3] status p u - Project completion status in project p for member u\n"
        "[4] labhours - Check whose lab hours it is right now\n"
        "[5] labhours o - Look up lab hours for officer o\n"
        "[6] balance p - Current lab buck balance for person p\n"
        "[7] transactions p - List of lab buck transactions for person p\n```"
    )
    # Add commands as new field to embed
    embed.add_field(name="Commands", value=commands_msg, inline=False)

    project_leads_msg = (
        f"```ahk\n\n"
        f'[1] checkoff p a u [v] - Check off user u for project p, assignment a. v is the new value; the default value is "1".\n'
        f'To add notes, {prefix}checkoff p a u "checkpoint 1"\n'
        f"[2] addassign p a d - Add assignment a, due on date d, to project p\n"
        f"[3] extend p a d - Change deadline to d for assignment a in project p\n"
        f"[4] paydeposit p u - Mark on Treasurer sheet that member u has paid deposit for project p\n"
        f"[4] returndeposit p u - Mark on Treasurer sheet that member u has been returned their deposit for project p\n"
        f"[6] closelab - Disable lab hours reminders for the day\n"
        f"[7] openlab - Reenable lab hours reminders, starting tomorrow```\n"
    )

    lab_buck_msg = (
        "```ahk\n\n"
        "[1] pay a [p] - Give person/people p lab bucks. Pay either with the name of a reward or a monetary value\n"
        "[2] spend a [p] - Spend lab bucks of person/people p for reward a\n"
        "[3] balance p - Get current lab buck balance of person p\n"
        "[4] transactions p - Get all lab buck transactions made by person p\n"
        "[3] rewards p - Get rewards associated with project p (or all rewards if no project is specified)\n"
        "[4] prizes - Get list of prizes and their prices \n"
        "[5] price p - Get price of prize p```\n"
    )

    # Only show these commands when executed by an officer!
    if is_officer(ctx):
        # Add project leads commands field to the embed
        embed.add_field(
            name="Project Lead Commands", value=project_leads_msg, inline=False
        )
        embed.add_field(name="Lab Buck Management", value=lab_buck_msg, inline=False)

    # Can turn this into a 2nd embed if you want thumbnails
    embed.add_field(
        name="IEEE at UCLA Website",
        value="[Website](https://ieeebruins.com/)",
        inline=True,
    )
    embed.add_field(
        name="IEEE Linktree",
        value="[Linktree](https://linktr.ee/uclaieee)",
        inline=True,
    )
    embed.add_field(
        name="SparkIEEE on Github",
        value="[Github](https://github.com/UCLA-IEEE/sparkieee)",
        inline=True,
    )

    await ctx.send(embed=embed)


@client.command()
async def projects(ctx):
    msg = (
        "Here is a list of our currently active projects:\n"
        f"```\n{fmt_projects()}```\n"
        f"For more info about a particular project, use the `{client.command_prefix}project project_name` command."
    )
    embed = discord.Embed(title="Projects", description=msg, color=color)
    await ctx.send(embed=embed)


@client.command()
async def project(ctx, *args):
    if len(args) == 0:
        err_msg = (
            "Please supply the command with a project argument.\n"
            f"For example, `{client.command_prefix}project OPS` or `{client.command_prefix}project Micromouse`."
        )
        await ctx.send(err_msg)
    elif args[0].upper() not in PROJECTS.keys():
        err_msg = (
            f"`{args[0]}` is not a valid project.\n"
            "Here is a list of our currently active projects:\n"
            f"```{fmt_projects()}```\n"
        )
        await ctx.send(err_msg)
    else:
        info = PROJECTS[args[0].upper()]
        projects = ""
        if "SPREAD_ID" in info:
            try:
                projects = f'```\n{sheets.lookup(info["SPREAD_ID"])}```'
            except Exception as e:
                log.info("Could not look up projects spreadsheet", args=args)
                await ctx.send(e)

        if projects == "":
            projects = f"{args[0]} has no projects yet\n"

        nl_with_dash = "\n- "
        nl = "\n"
        # Use iterator to grab the first (and only) value from the dictionary
        leads = "\n".join(
            [
                f"{name}: @{id}\n"
                f"- {next (iter( sheets.get_lab_hours_by_name(LAB_HOURS, name).values() ) ) .replace(nl, nl_with_dash)}\n"
                for name, id in info["LEADS"].items()
            ]
        )

        project_full_name = PROJECTS[args[0].upper()]["FULL_NAME"]

        # Only show the full name of the project if it's not an abbreviation
        description = (
            project_full_name if args[0].upper() != project_full_name.upper() else ""
        )

        # Embed for a specific project
        embed = discord.Embed(
            title=f"{args[0]} Information", description=description, color=color
        )
        if "SPREAD_ID" in info:
            embed.add_field(
                name=f"{args[0]} Projects:", value=f"{projects}", inline=False
            )
        embed.add_field(
            name=f"{args[0]} Project Leads:", value=f"```{leads}```", inline=False
        )
        if "FB_GROUP" in info:
            embed.add_field(
                name="Links",
                value=f'[{args[0]} Facebook Group]({info["FB_GROUP"]})',
                inline=False,
            )

        await ctx.send(embed=embed)


@client.command()
async def status(ctx, *args):
    if len(args) < 2:
        err_msg = (
            "Please supply the command with project and member name arguments.\n"
            f'For example, `{client.command_prefix}status OPS "Kathy Daniels"` or '
            f"`{client.command_prefix}status Micromouse 1`."
        )
        await ctx.send(err_msg)
    elif is_invalid_name(args[1]) or args[0].upper() not in PROJECTS.keys():
        err_msg = f"`{args[0]}` is not a valid project.\n"
        await ctx.send(err_msg)
        await projects(ctx)
    else:
        info = PROJECTS[args[0].upper()]
        if "SPREAD_ID" in info:
            try:
                # Turn everything starting from the 1st argument into a string
                name = get_name_from_args(args[1:])

                title = f"**{name}'s {args[0].upper()} Project Status:**"
                description = f'```\n{sheets.lookup(info["SPREAD_ID"], name=name)}```'
                embed = discord.Embed(title=title, description=description, color=color)
                await ctx.send(embed=embed)
            except Exception as e:
                log.info("Failed reading spreadsheet", args=args)
                await ctx.send(e)
        else:
            msg = f"{args[0]} does not currently have a checkoff sheet."
            await ctx.send(msg)


@client.command()
async def labhours(ctx, *args):
    if len(args) == 0:
        if not lab_open:
            await ctx.send(
                "The Lab is closed today. For a full list of lab hours, visit our lab website https://ieeebruins.com/lab."
            )
            return
        try:
            date = datetime.now(tz=pytz.utc)
            date = date.astimezone(pytz.timezone("US/Pacific"))
            shift_str, officers = sheets.get_lab_hours_by_time(LAB_HOURS, date)
            special_hours = sheets.get_lab_special_by_time(LAB_HOURS, date)

            # Lab hours embed for all officers
            title = f"Lab Hours for {shift_str}"
            description = f"```\n{officers}```"
            if special_hours:
                description = (
                    description + f"\n**Special Lab Hours!**:\n{special_hours}"
                )
            embed = discord.Embed(title=title, description=description, color=color)

            await ctx.send(embed=embed)
        except Exception as e:
            log.info("Failed showing all lab hours", args=args)
            await ctx.send(e)
    else:
        try:
            hours = sheets.get_lab_hours_by_name(LAB_HOURS, args[0])
            if not is_invalid_name(args[0]) and hours:
                # In case anyone abuses this command, replace for loop with this code
                """
                if len(hours) > 1:
                    title = f"{args[0]}'s Lab Hours"
                    description = f'Did you mean: ```{", ".join(hours.keys())}```'
                    embed = discord.Embed(title=title, description=description, color=color)
                    await ctx.send(embed=embed)
                """

                for officer_name, hours_string in hours.items():
                    # Lab hours embed for an officer
                    title = f"{officer_name}'s Lab Hours"
                    description = f"```\n{hours_string}```"
                    embed = discord.Embed(
                        title=title, description=description, color=color
                    )

                    await ctx.send(embed=embed)
            else:
                msg = (
                    f"**{args[0]}** is either not an officer or does not have lab hours.\n"
                    "A full list of lab hours can be found at our lab website https://ieeebruins.com/lab."
                )
                await ctx.send(msg)
        except Exception as e:
            log.info("Failed showing lab hours for a specific officer", args=args)
            await ctx.send(e)


@client.command()
@commands.has_any_role(officer_title, old_officer_title)
async def paydeposit(ctx, *args):
    if len(args) < 2:
        err_msg = (
            "Please supply the command with project, member name, and assignment arguments.\n"
            f'For example, `{client.command_prefix}paydeposit Aircopter "Jay Park"'
        )
        await ctx.send(err_msg)
    elif args[0].upper() not in PROJECTS.keys():
        err_msg = (
            f"`{args[0]}` is not a valid project.\n"
            "Here is a list of our currently active projects:\n"
            f"```{fmt_projects()}```\n"
        )
        await ctx.send(err_msg)
    else:
        info = PROJECTS[args[0].upper()]
        new_val = True

        name = get_name_from_args(args[1:])
        try:
            old_val = sheets.paydeposit(
                TREASURER_SHEET,
                name=name,
                val=new_val,
                sheet_index=info["TREASURER_IND"],
            )
        except Exception as e:
            log.info("Failed paying deposit", args=args)
            await ctx.send(e)
            return
        if old_val == "TRUE":
            msg = f"**{name}** has already paid their deposit for **{args[0]}**.\n"
            await ctx.send(msg)
        else:
            # Successful check off embed
            title = f"Deposit payment for {name}"
            description = f"**{name}** has paid their deposit for **{args[0]}**!\n"
            embed = discord.Embed(title=title, description=description, color=color)
            await ctx.send(embed=embed)


@client.command()
@commands.has_any_role(officer_title, old_officer_title)
async def returndeposit(ctx, *args):
    if len(args) < 2:
        err_msg = (
            "Please supply the command with project, and member name.\n"
            f'For example, `{client.command_prefix}returndeposit Aircopter "Jay Park"'
        )
        await ctx.send(err_msg)
    elif args[0].upper() not in PROJECTS.keys():
        err_msg = (
            f"`{args[0]}` is not a valid project.\n"
            "Here is a list of our currently active projects:\n"
            f"```{fmt_projects()}```\n"
        )
        await ctx.send(err_msg)
    else:
        info = PROJECTS[args[0].upper()]
        new_val = True

        name = get_name_from_args(args[1:])
        try:
            old_val = sheets.returndeposit(
                TREASURER_SHEET,
                name=name,
                val=new_val,
                sheet_index=info["TREASURER_IND"],
            )
        except Exception as e:
            log.info("Failed returning deposit", args=args)
            await ctx.send(e)
            return
        if old_val == "TRUE":
            msg = f"**{name}** has already received their deposit for **{args[0]}**.\n"
            await ctx.send(msg)
        else:
            # Successful check off embed
            title = f"Deposit payment for {name}"
            description = f"**{name}** has received their deposit for **{args[0]}**!\n"
            embed = discord.Embed(title=title, description=description, color=color)
            await ctx.send(embed=embed)


@client.command()
@commands.has_any_role(officer_title, old_officer_title)
async def checkoff(ctx, *args):
    if len(args) < 3:
        err_msg = (
            "Please supply the command with project, member name, and assignment arguments.\n"
            f'For example, `{client.command_prefix}checkoff Aircopter "Lab 1" "Jay Park"`.'
        )
        await ctx.send(err_msg)
    elif args[0].upper() not in PROJECTS.keys():
        err_msg = (
            f"`{args[0]}` is not a valid project.\n"
            "Here is a list of our currently active projects:\n"
            f"```{fmt_projects()}```\n"
        )
        await ctx.send(err_msg)
    else:
        info = PROJECTS[args[0].upper()]
        new_val = "1" if len(args) < 4 else args[3]
        # use slicing to pass arr of strings to helper function
        name = get_name_from_args(args[2:3])
        if "SPREAD_ID" in info:
            try:
                old_val = sheets.checkoff(
                    info["SPREAD_ID"], assignment=args[1], name=name, val=new_val
                )
            except Exception as e:
                log.info("Failed checkoff", args=args)
                await ctx.send(e)
                return
            if old_val == new_val:
                msg = f"**{name}** has already been checked off for **{args[0]} {args[1]}**.\n"
                await ctx.send(msg)
            else:
                # Successful check off embed
                title = f"Checked off {name}"
                description = (
                    f"**{name}** has been checked off for **{args[0]} {args[1]}**!\n"
                    f'```Value changed from "{old_val}" to "{new_val}"```'
                )
                embed = discord.Embed(title=title, description=description, color=color)
                await ctx.send(embed=embed)
        else:
            msg = f"{args[0]} does not currently have a checkoff sheet."
            await ctx.send(msg)

        await checkoff_treasurer_subroutine(
            ctx, args[0], args[1], name, new_val, info["TREASURER_IND"]
        )


async def checkoff_treasurer_subroutine(
    ctx, project, assignment, name, new_val, treasurer_index
):
    try:
        old_val = sheets.checkoff(
            TREASURER_SHEET,
            assignment=assignment,
            name=name,
            val=new_val,
            sheet_index=treasurer_index,
        )
    except Exception as e:
        log.info("Failed treasurer checkoff", project, assignment, name)
        await ctx.send(e)
        return
    if old_val == new_val:
        msg = f"**{name}** has already been checked off for **{project} {assignment} on the Treasurer Sheet**.\n"
        await ctx.send(msg)
    else:
        # Successful check off embed
        title = f"Checked off {name}"
        description = (
            f"**{name}** has been checked off for **{project} {assignment}** on the Treasurer Sheet!\n"
            f'```Value changed from "{old_val}" to "{new_val}" on the Treasurer Sheet```'
        )
        embed = discord.Embed(title=title, description=description, color=color)
        await ctx.send(embed=embed)


@client.command()
@commands.has_any_role(officer_title, old_officer_title)
async def addassign(ctx, *args):
    if len(args) < 3:
        err_msg = (
            "Please supply the command with project, assignment, and deadline arguments.\n"
            f'For example, `{client.command_prefix}addassign WRAP "Project 1" "2/11/2020"`'
        )
        await ctx.send(err_msg)
    elif args[0].upper() not in PROJECTS.keys():
        err_msg = (
            f"`{args[0]}` is not a valid project.\n"
            "Here is a list of our currently active projects:\n"
            f"```{fmt_projects()}```\n"
        )
        await ctx.send(err_msg)
    else:
        info = PROJECTS[args[0].upper()]
        msg = ""
        if "SPREAD_ID" in info:
            try:
                sheets.add_assignment(info["SPREAD_ID"], args[1], args[2])
                msg = f"Successfully added assignment **{args[1]}** to the **{args[0]}** spreadsheet, due **{args[2]}**"
            except Exception as e:
                log.info("Failed project assignment", args=args)
                await ctx.send(e)
                return
        else:
            msg = f"{args[0]} does not currently have a checkoff sheet."

        await ctx.send(msg)

    await addassign_treasurer_subroutine(ctx, args[0], args[1], info["TREASURER_IND"])


async def addassign_treasurer_subroutine(ctx, project, assignment, treasurer_index):
    # Add assignment to treasurer sheet
    try:
        num_assignments = sheets.add_treasurer_assignment(assignment, treasurer_index)
        msg = f"Successfully added assignment **{assignment}** to the Treasurer spreadsheet.\n"
        msg += f"{project} leads: please update weights on Treasurer sheet.\n"
        msg += f"There are {num_assignments} total assignments\n"
    except Exception as e:
        log.info("Failed assigning to Treasurer spreadsheet", project, assignment)
        await ctx.send(e)
        return

    await ctx.send(msg)


@client.command()
@commands.has_any_role(officer_title, old_officer_title)
async def extend(ctx, *args):
    if len(args) < 3:
        err_msg = (
            "Please supply the command with project, assignment, and new deadline arguments.\n"
            f'For example, `{client.command_prefix}extend OPS "Project 1" "10/11/2020"`'
        )
        await ctx.send(err_msg)
    elif args[0].upper() not in PROJECTS.keys():
        err_msg = (
            f"`{args[0]}` is not a valid project.\n"
            "Here is a list of our currently active projects:\n"
            f"```{fmt_projects()}```\n"
        )
        await ctx.send(err_msg)
    else:
        info = PROJECTS[args[0].upper()]
        if "SPREAD_ID" in info:
            try:
                old_deadline = sheets.change_deadline(
                    info["SPREAD_ID"], args[1], args[2]
                )
                msg = (
                    f"Successfully changed **{args[0]}** assignment **{args[1]}** deadline "
                    f"from **{old_deadline}** to **{args[2]}**"
                )
            except Exception as e:
                log.info("Failed extending deadline", args=args)
                await ctx.send(e)
        else:
            msg = f"{args[0]} does not currently have a checkoff sheet."
        await ctx.send(msg)


@client.command()
@commands.has_any_role(officer_title, old_officer_title)
async def closelab(ctx):
    global lab_open
    lab_open = False
    await ctx.send(
        f"The lab is now closed. Lab Hours reminders will cease until "
        f"the `{client.command_prefix}openlab` command is used to reopen it."
    )


@client.command()
@commands.has_any_role(officer_title, old_officer_title)
async def openlab(ctx):
    global lab_open
    lab_open = True
    await ctx.send(
        "The lab is now reopened. Lab Hours reminders will restart tomorrow."
    )


@client.command()
async def torch(ctx):
    # Make new embed with description
    embed = discord.Embed(title="UCLA IEEE 2020-2021", color=color)

    embed.add_field(name="President", value="Bryan Wong", inline=True)
    embed.add_field(name="IVP", value="Kathy Daniels", inline=True)
    embed.add_field(name="EVP", value="Albert Han, Jay Park", inline=True)
    embed.add_field(name="Treasurer", value="Erica Xie", inline=True)
    embed.add_field(name="Corporate Relations", value="Pranav Srinivasan", inline=True)
    embed.add_field(name="Secretary", value="Achinthya Poduval", inline=True)
    embed.add_field(name="Publicity", value="Solaine Zhao", inline=True)
    embed.add_field(name="Events Coordinator", value="Grace Ma", inline=True)
    embed.add_field(
        name="Projects and Lab Manager",
        value="Caleb Terrill, Chester Hulse",
        inline=True,
    )
    embed.add_field(name="R&D", value="David Baum", inline=True)
    embed.add_field(name="Webmaster", value="Robert Peralta", inline=True)
    embed.add_field(
        name="Micromouse Lead", value="Bradley Schulz, Tyler Price", inline=True
    )
    embed.add_field(name="Aircopter Lead", value="Aaron Kuo, Eric Tang", inline=True)
    embed.add_field(name="DAV Lead", value="Brandon Le, David Kao", inline=True)
    embed.add_field(
        name="Workshops Manager", value="Jackie Lam, Travis Graening", inline=True
    )
    embed.add_field(name="OPS Lead", value="Ryeder Geyer, Taylor Chung", inline=True)
    embed.set_image(
        url="https://media3.giphy.com/media/E4Xf4Qy3Cd4b97pKoQ/giphy.gif?cid=790b761124a9b3ec6f873d62a688fb6d49f6990e6450b97e&rid=giphy.gif&ct=g"
    )

    await ctx.send(embed=embed)


@tasks.loop(hours=1)
async def lab_hours_reminder():
    global labhour_msg
    date = datetime.now(tz=pytz.utc)
    date = date.astimezone(pytz.timezone("US/Pacific"))

    if not lab_open or date.weekday() >= 5:  # weekend
        return
    if date.hour < 10 or date.hour > 19:
        return

    lab_channel = client.get_channel(LAB_CHANNEL_ID)
    if not lab_channel:
        return

    try:
        if labhour_msg:
            try:
                await labhour_msg.delete()
                log.debug(
                    "Deleted a lab hours reminder message", labhour_msg=labhour_msg
                )
            except discord.NotFound:
                log.exception(
                    "Could not find a lab hours reminder message to delete",
                    labhour_msg=labhour_msg,
                )

        if date.hour == 18:
            msg = "Lab Hours have officially ended. For a full list of lab hours, visit https://ieeebruins.com/lab."
            await lab_channel.send(msg)
        else:
            shift_str, officers = sheets.get_lab_hours_by_time(LAB_HOURS, date)
            special_hours = sheets.get_lab_special_by_time(LAB_HOURS, date)

            title = f"Lab Hours for {shift_str}"
            description = f'```\n{officers if officers else "None"}```'
            if special_hours:
                description += f"\n**Special Lab Hours!**:\n{special_hours}"
            embed = discord.Embed(title=title, description=description, color=color)

            if lab_channel:
                labhour_msg = await lab_channel.send(embed=embed)
                log.debug(
                    "Successfully sent hourly lab hours message",
                    labhour_msg=labhour_msg,
                    lab_channel=lab_channel,
                )
    except Exception:
        log.exception("Lab hours reminder failed", labhour_msg=labhour_msg)


@lab_hours_reminder.before_loop
async def before():
    await client.wait_until_ready()
    date = datetime.now(tz=pytz.utc)
    date = date.astimezone(pytz.timezone("US/Pacific"))

    if date.hour == 23:
        future = pytz.timezone("US/Pacific").localize(
            datetime(date.year, date.month, date.day, LAB_HOURS_START_TIME, 0)
        )
        future += timedelta(days=1)
    else:
        future = pytz.timezone("US/Pacific").localize(
            datetime(date.year, date.month, date.day, date.hour + 1, 0)
        )
    wait_period = (future - date).total_seconds()
    log.info(
        f"Waiting until {future} before starting lab hour reminders "
        f"({wait_period} seconds)."
    )
    await asyncio.sleep(wait_period)
    log.info("Beginning Lab Hours scheduled reminders")


# Helper functions added by Raj


# Simple error embed
def error_embed(msg):
    return discord.Embed(title="Error", description=msg, color=error_color)


# Better formatting for .projects
def fmt_projects():
    res = ""
    for project_name in PROJECTS.keys():
        # If it's 4 letters or less, we assume it's an abbreviation
        if len(project_name) < 5:
            res += project_name
        else:
            res += project_name.lower().capitalize()
        # Separate each entry w/ newline
        res += "\n"
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
    return any("officers" in role.name for role in ctx.message.author.roles)


# TO-DO: Come up with a better name for this function?
# If we do .status OPS Joe Schmoe, this just captures Joe Schmoe as its own string
# No need to use quotes anymore with this


def get_name_from_args(args):
    name = ""
    for i in range(0, len(args)):
        name += " " + args[i]
    return name.strip()


####### LAB BUCK COMMANDS #######
# Finds the closest matching name from firebase
def find_name(name: str, group: str = None) -> list:
    user_list = firebase.get_members(group)
    name = name.lower()
    possible_names = []
    for user in user_list:
        if name in user.lower() or user.lower() in name:
            possible_names.append(user)
    return possible_names


def replacement_name_str(name: str, group: str = None) -> str:
    replacements = find_name(name, group)
    msg = ""
    if replacements:
        msg += (
            "Closest matches: \n```"
            if len(replacements) > 1
            else "Closest match is: \n```"
        )
        msg += "\n".join(replacements).title() + "```"
    return msg


# Give lab bucks
# Can either give an amount or a reward
# First put reward then a list of names
# Each name must have quotes around it
@client.command()
@commands.has_any_role(officer_title, old_officer_title)
async def pay(ctx, *args):
    if len(args) > 1:
        reward = args[0]
        names = args[1:]
        for name in names:
            if type(name) != str:
                msg = "Invalid name"
            else:
                # give reward
                if reward.isnumeric():
                    # Specific amount
                    if lab_buck_title in [
                        role.name for role in ctx.message.author.roles
                    ]:
                        amt = firebase.add_lb(name, int(reward))
                    else:
                        amt = ErrorCodes.PermissionError
                else:
                    # Name of a reward
                    amt = firebase.give_reward(name, reward)
                # decode result from firebase command
                if amt == ErrorCodes.GenericError:
                    msg = "Error giving lab bucks to " + name
                elif amt == ErrorCodes.UserNotFound:
                    msg = (
                        name
                        + " not found in lab buck database\n"
                        + replacement_name_str(name)
                    )
                elif amt == ErrorCodes.DuplicateReward:
                    msg = name + " already received this reward"
                elif amt == ErrorCodes.InvalidReward:
                    msg = "Invalid reward for " + name
                elif amt == ErrorCodes.PermissionError:
                    msg = "You do not have permission to pay a numeric amount"
                else:
                    msg = name + " has received " + str(amt) + " lab bucks"
            await ctx.send(msg)
    else:
        await ctx.send("Invalid arguments")


# Use lab bucks
# First provide prize and then a list of names
@client.command()
@commands.has_any_role(officer_title, old_officer_title)
async def spend(ctx, *args):
    if len(args) > 1:
        prize = args[0]
        names = args[1:]
        for name in names:
            amt = firebase.use_lb(name, prize)
            if amt == ErrorCodes.UserNotFound:
                msg = (
                    name
                    + " not found in lab buck database\n"
                    + replacement_name_str(name)
                )
            elif amt == ErrorCodes.InvalidPrize:
                msg = prize + " is not a valid prize"
            elif amt < 0:
                msg = name + " needs " + str(-amt) + " more lab bucks for " + prize
            else:
                msg = name + " redeemed " + str(amt) + " lab bucks for " + prize
            msg += (
                "\n"
                + name
                + " now has "
                + str(firebase.get_balance(name))
                + " lab bucks"
            )
            await ctx.send(msg)
    else:
        await ctx.send("Invalid arguments")


# Get lab buck transaction history for a user
@client.command()
async def transactions(ctx, *args):
    if len(args) == 1:
        name = args[0]
        history = firebase.get_transaction_history(name)
        if history:
            msg = "Transactions for " + name + ":"
            for transaction in history:
                if transaction:
                    msg += "\n\t" + transaction
        else:
            msg = (
                "Unable to find history for " + name + "\n" + replacement_name_str(name)
            )
        await ctx.send(msg)
    else:
        await ctx.send("Invalid arguments")


# Get current lab buck balance for a user
@client.command()
async def balance(ctx, *args):
    if len(args) == 1:
        name = args[0]
        current_balance = firebase.get_balance(name)
        if current_balance == ErrorCodes.UserNotFound:
            msg = name.title() + " not found in database"
        elif current_balance >= 0:
            msg = name + " currently has " + str(current_balance) + " lab bucks"
        else:
            msg = (
                "Unable to find balance for " + name + "\n" + replacement_name_str(name)
            )
        await ctx.send(msg)
    else:
        await ctx.send("Invalid arguments")


# Get available rewards
@client.command()
async def rewards(ctx, *args):
    if len(args) <= 1:
        # Get all prizes
        if len(args) == 0:
            rewards_dict = firebase.get_rewards()
            msg = "Available rewards```\n"
        # Get prizes for a specific category
        elif len(args) == 1:
            rewards_dict = firebase.get_rewards(args[0].lower())
            msg = "Available rewards for " + args[0] + "```\n"
        if rewards_dict:
            msg += "\n".join(
                [
                    (reward.title() + ": " + str(value))
                    for reward, value in rewards_dict.items()
                ]
            )
            msg += "```"
        else:
            msg = "Invalid project"
    else:
        msg = "Invalid arguments"
    await ctx.send(msg)


# Gets available prizes
@client.command()
async def prizes(ctx, *args):
    # Get all prizes
    prize_dict = firebase.get_prizes()
    msg = "Prize list with prices:```\n"
    # Format output with prize list in order of increasing price
    msg += "\n".join(
        [
            (reward.title() + ": " + str(value))
            for reward, value in sorted(prize_dict.items(), key=lambda item: item[1])
        ]
    )
    msg += "```"
    await ctx.send(msg)


# Get price of a specific prize
@client.command()
async def price(ctx, *args):
    if len(args) == 1:
        prize = args[0]
        p = firebase.get_price(prize.lower())
        if p == ErrorCodes.InvalidPrize:
            msg = prize.title() + " is not a valid prize"
        else:
            msg = "```" + prize.title() + " costs " + str(p) + " lab bucks```"
    else:
        msg = "Invalid arguments"
    await ctx.send(msg)


sheets = SheetTransformer()
firebase = FirebaseManager()
lab_hours_reminder.start()
client.run(SPARKIEEE_TOKEN)
