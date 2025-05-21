import os
from discord import Colour
from discord.ext import commands, tasks
import responses
import sqlite3
from dotenv import load_dotenv
import random
from datetime import datetime, timezone, timedelta
import asyncio



def run_discord_bot(discord):
    load_dotenv()
    TOKEN = os.getenv('BOT_KEY')

    
    app_commands = discord.app_commands
    bot = commands.Bot(command_prefix="%", intents=discord.Intents.all())
    bot.remove_command("help")
    connection = sqlite3.connect("mydata.db")
    cursor = connection.cursor()

    @bot.event
    async def on_ready():
        print(f"{bot.user} is ready")
        try:
            synced = await bot.tree.sync()
        except Exception as e:
            print(e)

        


    


    @bot.event
    async def on_message(message):
        global chat
        
        if message.author != bot.user:
            username = str(message.author)
            user_message = str(message.content)
            channel = str(message.channel)

            print(f"{username} said: '{user_message}' ({channel})")
            
            await bot.process_commands(message)
                

    @bot.command()
    async def hostRandomScrim(ctx, minutes: float = 5):
        wait_seconds = int(minutes * 60)
        host = ctx.author

        # DM the host to ask for a link
        try:
            await host.send("Please send me the link you'd like to share with the players (you have 2 minutes).")
        except discord.Forbidden:
            await ctx.send(f"{host.mention}, I couldn't DM you. Please enable DMs from server members and try again.")
            return

        def dm_check(m):
            return m.author == host and isinstance(m.channel, discord.DMChannel)

        try:
            dm_msg = await bot.wait_for('message', timeout=120.0, check=dm_check)
            shared_link = dm_msg.content.strip()
        except asyncio.TimeoutError:
            await host.send("You didn't send a link in time. Canceling the command.")
            return

        # Send the message and add reaction
        reaction_msg = await ctx.send(f"{host.mention} is hosting a scrim! React with ✅ within {minutes:.1f} minute(s) to join!")
        await reaction_msg.add_reaction("✅")

        def reaction_check(reaction, user):
            return (
                reaction.message.id == reaction_msg.id and
                str(reaction.emoji) == "✅" and
                not user.bot
            )

        reacted_users = set()

        # Collect reactions
        try:
            while True:
                reaction, user = await bot.wait_for("reaction_add", timeout=wait_seconds, check=reaction_check)
                reacted_users.add(user)
        except asyncio.TimeoutError:
            pass

        players = list(reacted_users)
        random.shuffle(players)

        team1 = players[:5]
        team2 = players[5:10]
        subs = players[10:] if len(players) > 10 else []

        def format_team(name, members):
            if not members:
                return f"**{name}**: _(no players)_"
            return f"**{name}**:\n" + "\n".join(user.mention for user in members)

        result = [
            format_team("Home Team", team1),
            format_team("Away Team", team2)
        ]

        if subs:
            result.append("**Substitutes:**\n" + "\n".join(user.mention for user in subs))

        await ctx.send("Players have been dmed the private server link. Here are the teams:\n\n" + "\n\n".join(result))

        # Send link via DM to all participants
        all_players = team1 + team2 + subs
        for user in all_players:
            try:
                await user.send(f"You were added to a team! Here's the link from the host:\n{shared_link}")
            except discord.Forbidden:
                await ctx.send(f"Couldn't DM {user.mention}.")




    @bot.command()
    async def help(ctx):
        await ctx.message.reply("YOU'RE NOT GETTING ANY HELP FOR THIS ONE")


    
    bot.run(TOKEN)
