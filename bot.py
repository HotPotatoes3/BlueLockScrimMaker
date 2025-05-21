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

        # Step 1: DM the host to get the link
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
            await host.send("You didn’t send a link in time. Canceling the command.")
            return

        # Step 2: Post the reaction message
        scrim_embed = discord.Embed(
        title="🎮 New Scrim Hosted!",
        description=f"{host.mention} is hosting a scrim!\n\nReact with ✅ within **{minutes:.1f} minute(s)** to join!",
        color=discord.Color.blue()
        )
        scrim_embed.set_footer(text="Get in quick or miss out!")

        reaction_msg = await ctx.send(embed=scrim_embed)
        await reaction_msg.add_reaction("✅")

        # Step 3: Track reactions and removals
        reacted_users = set()
        reaction_end = asyncio.Event()

        def reaction_check(reaction, user):
            return (
                reaction.message.id == reaction_msg.id and
                str(reaction.emoji) == "✅" and
                not user.bot
            )

        def reaction_remove_check(reaction, user):
            return reaction_check(reaction, user)

        async def collect_reactions():
            try:
                while not reaction_end.is_set():
                    reaction, user = await bot.wait_for("reaction_add", timeout=wait_seconds, check=reaction_check)
                    reacted_users.add(user)
            except asyncio.TimeoutError:
                reaction_end.set()

        async def remove_reactions():
            try:
                while not reaction_end.is_set():
                    reaction, user = await bot.wait_for("reaction_remove", timeout=wait_seconds, check=reaction_remove_check)
                    reacted_users.discard(user)
            except asyncio.TimeoutError:
                pass

        # Step 4: Run collectors in parallel
        await asyncio.gather(collect_reactions(), remove_reactions())

        # Step 5: Form teams
        players = list(reacted_users)
        random.shuffle(players)

        if len(players) <= 10:
            mid = len(players) // 2
            team1 = players[:mid]
            team2 = players[mid:]
            subs = []
        else:
            team1 = players[:5]
            team2 = players[5:10]
            subs = players[10:]

        def format_team(name, members):
            if not members:
                return f"**{name}**: _(no players)_"
            return f"**{name}**:\n" + "\n".join(user.mention for user in members)

        result_embed = discord.Embed(
            title="🏆 Scrim Teams Ready!",
            description="Players have been DMed the private server link. Here are the teams:",
            color=discord.Color.green()
        )

        result_embed.add_field(name="Home Team 🔵", value=format_team("Home Team", team1), inline=False)
        result_embed.add_field(name="Away Team ⚪", value=format_team("Away Team", team2), inline=False)

        if subs:
            result_embed.add_field(name="Substitutes 🪑", value="\n".join(user.mention for user in subs), inline=False)

        result_embed.set_image(url="https://cdn.discordapp.com/attachments/1373052932655939734/1374236632986943558/blgif-ezgif.com-crop.gif?ex=682f4b59&is=682df9d9&hm=a8ebf9968d99c2d2fdc42594c27873a0895c9493e383e6ae461d65915996573b&")
        result_embed.set_footer(text="Good luck, have fun!")

        await ctx.send(embed=result_embed)

        # Step 6: DM everyone the link
        for user in team1 + team2 + subs:
            try:
                await user.send(f"You were added to a team! Here's the link from the host:\n{shared_link}")
            except discord.Forbidden:
                await ctx.send(f"Couldn't DM {user.mention}.")




    @bot.command()
    async def help(ctx):
        embed = discord.Embed(
            title="🎮 Scrim Bot Help",
            description="Here's how to host a random scrim using the bot:",
            color=discord.Color.green()
        )

        embed.add_field(
            name="📌 Command",
            value="`$hostRandomScrim [minutes]`",
            inline=False
        )

        embed.add_field(
            name="🕒 Time Limit",
            value="Sets how long (in minutes) players have to react with ✅ to join. Example: `!hostRandomScrim 5` waits for 5 minutes.",
            inline=False
        )

        embed.add_field(
            name="📩 Host Input",
            value="After running the command, the bot will DM **you (the host)** asking for a link (e.g., server IP, match lobby, etc.). You have 2 minutes to reply.",
            inline=False
        )

        embed.add_field(
            name="✅ Joining the Scrim",
            value="Players must react with ✅ to the bot’s message to join. If they unreact, they will be removed.",
            inline=False
        )

        embed.add_field(
            name="🤖 Team Assignment",
            value=(
                "- Players are randomly split into two even teams (up to 5v5).\n"
                "- If more than 10 players react, extras are listed as **substitutes**."
            ),
            inline=False
        )

        embed.add_field(
            name="📬 DM Delivery",
            value="All participants will receive the host’s link in their DMs when the teams are announced.",
            inline=False
        )

        embed.set_footer(text="Questions? Contact a server admin or the bot dev.")
        await ctx.send(embed=embed)


    
    bot.run(TOKEN)
