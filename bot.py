
import os
import discord
from discord.ext import commands

TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"ST4RCO SERVER TOOL online: {bot.user}")


def admin_only():
    async def predicate(ctx):
        return (
            ctx.guild is not None
            and ctx.author.guild_permissions.administrator
        )
    return commands.check(predicate)


@bot.command()
@admin_only()
async def channels(ctx):
    """List server text and voice channels."""
    lines = [
        f"{c.id} | {c.name} | {c.type}"
        for c in ctx.guild.channels
    ]
    await ctx.send(
        "\n".join(lines[:40]) or "No channels found."
    )


@bot.command()
@admin_only()
async def roles(ctx):
    """List server roles."""
    lines = [
        f"{r.id} | {r.name}"
        for r in ctx.guild.roles
        if not r.is_default()
    ]
    await ctx.send(
        "\n".join(lines[:40]) or "No roles found."
    )


@bot.command()
@admin_only()
async def makechannel(ctx, *, name: str):
    """Create a text channel."""
    if len(name) > 100:
        await ctx.send("Channel name is too long.")
        return

    channel = await ctx.guild.create_text_channel(
        name=name,
        reason=f"Requested by {ctx.author}"
    )
    await ctx.send(f"Created channel: {channel.mention}")


@bot.command()
@admin_only()
async def makerole(ctx, *, name: str):
    """Create a basic role without elevated permissions."""
    if len(name) > 100:
        await ctx.send("Role name is too long.")
        return

    role = await ctx.guild.create_role(
        name=name,
        permissions=discord.Permissions.none(),
        reason=f"Requested by {ctx.author}"
    )
    await ctx.send(f"Created role: {role.name} (ID: {role.id})")


@bot.command()
@admin_only()
async def deletechannel(ctx, channel_id: int, confirm: str = ""):
    """Delete one channel by ID after explicit confirmation."""
    if confirm.lower() != "confirm":
        await ctx.send(
            f"This will delete ONE channel (ID {channel_id}).\n"
            f"Run `!deletechannel {channel_id} confirm` to proceed."
        )
        return

    channel = ctx.guild.get_channel(channel_id)
    if channel is None:
        await ctx.send("Channel not found in this server.")
        return

    name = channel.name
    await channel.delete(reason=f"Confirmed by {ctx.author}")
    await ctx.send(f"Deleted channel: {name}")


@bot.command()
@admin_only()
async def deleterole(ctx, role_id: int, confirm: str = ""):
    """Delete one role by ID after explicit confirmation."""
    if confirm.lower() != "confirm":
        await ctx.send(
            f"This will delete ONE role (ID {role_id}).\n"
            f"Run `!deleterole {role_id} confirm` to proceed."
        )
        return

    role = ctx.guild.get_role(role_id)
    if role is None or role.is_default():
        await ctx.send("Role not found or cannot be deleted.")
        return

    if role.managed or role >= ctx.guild.me.top_role:
        await ctx.send(
            "Cannot delete a managed role or a role at/above "
            "the bot's highest role."
        )
        return

    name = role.name
    await role.delete(reason=f"Confirmed by {ctx.author}")
    await ctx.send(f"Deleted role: {name}")


@bot.command()
async def helpst4rco(ctx):
    await ctx.send(
        "**ST4RCO SERVER TOOL**\n"
        "`!channels` — list channels\n"
        "`!roles` — list roles\n"
        "`!makechannel name` — create a text channel\n"
        "`!makerole name` — create a basic role\n"
        "`!deletechannel ID` — preview one channel deletion\n"
        "`!deleterole ID` — preview one role deletion"
    )


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("Administrator permission is required.")
    elif isinstance(error, commands.CommandNotFound):
        return
    else:
        print(f"Command error: {error}")
        await ctx.send(
            "Command failed. Check the bot permissions and logs."
        )


if not TOKEN:
    raise RuntimeError("Set the DISCORD_BOT_TOKEN environment secret.")

bot.run(TOKEN)
