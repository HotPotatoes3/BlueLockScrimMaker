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
        
        check_inactive_channels.start()
        gay_loop.start()



    gay_gifs = ["https://tenor.com/view/girl-anime-kiss-i-love-you-gif-2024647334029262493", "https://tenor.com/view/sono-hanabira-ni-kuchizuke-wo-anime-yuri-kiss-gif-19434907", "https://tenor.com/view/wow-gif-25687305", "https://tenor.com/view/yuri-gif-24238090", "https://tenor.com/view/bloom-into-you-yagate-kimi-ni-naru-yuri-kiss-gif-21637575", "https://tenor.com/view/neighbors-gif-7743851900177201494", "https://tenor.com/view/anime-girl-hug-lesbians-anime-lesbian-anime-girl-anime-girl-kiss-gif-10007048051271758348"]

    @tasks.loop(minutes=0.01)
    async def gay_loop():
        for i in gay_channels:
            rand = random.randint(1, 100)
            print (rand)
            if rand <= 8:
                channel = bot.get_channel(i)
                await channel.send(random.choice(gay_gifs))
    
    
    @bot.command()
    @commands.has_permissions(manage_channels=True)
    async def lesbomode(ctx):
        
        if ctx.channel.id not in gay_channels:
            gay_channels.append(ctx.channel.id)
            await ctx.send(f"This channel is now LESBIAN")
        else:
            gay_channels.remove(ctx.channel.id)
            await ctx.send(f"This channel is STRAIGHT 🥀")
    
    
        
    global chat
    chat = responses.create_chat()
    
    @tasks.loop(minutes=20)
    async def check_inactive_channels():
        now = datetime.now(timezone.utc)
        for guild_id, last_message_time in monitored_guilds.items():
            if now - last_message_time > timedelta(minutes=120):
                global chat
                chat = responses.create_chat()

    monitored_guilds = {}
    restricted_channels = []
    gay_channels = []

    @bot.event
    async def on_message(message):
        global chat
        
        if message.author != bot.user:
            username = str(message.author)
            user_message = str(message.content)
            channel = str(message.channel)

            print(f"{username} said: '{user_message}' ({channel})")
            
            if user_message[0] != '%' and message.channel.id not in restricted_channels:
                if bot.user in message.mentions:
                    resp = chat.send_message(f"Respond relevantly to this chat message from a chatter,{username}, talking to you (<@1374806045276508291> is your ping, ignore it and avoid using it in your message): {user_message}").text
                    await message.reply(resp)
                elif message.reference is not None:
                    replied_message = await message.channel.fetch_message(message.reference.message_id)
                    if replied_message.author == bot.user:
                        resp = chat.send_message(f"Respond relevantly to this chat message from a chatter, {username}, talking to you): {user_message}").text
                        await message.reply(resp)
                elif message.guild is None:
                    resp = chat.send_message(f"Respond relevantly to this chat message (it's a dm to you): {user_message}").text
                    await message.author.send(resp)
            else:
                await bot.process_commands(message)
                
        monitored_guilds[message.guild.id] = datetime.now(timezone.utc)
                

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
            while not reaction_end.is_set():
                try:
                    reaction, user = await bot.wait_for("reaction_add", timeout=1, check=reaction_check)
                    reacted_users.add(user)
                except asyncio.TimeoutError:
                    continue

        async def remove_reactions():
            while not reaction_end.is_set():
                try:
                    reaction, user = await bot.wait_for("reaction_remove", timeout=1, check=reaction_remove_check)
                    reacted_users.discard(user)
                except asyncio.TimeoutError:
                    continue

        # Run collectors and wait for the total time
        collect_task = asyncio.create_task(collect_reactions())
        remove_task = asyncio.create_task(remove_reactions())
        await asyncio.sleep(wait_seconds)
        reaction_end.set()
        await asyncio.gather(collect_task, remove_task)


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

        result_embed.set_footer(text="Good luck, have fun!")

        await ctx.send("https://cdn.discordapp.com/attachments/1373052932655939734/1374236632986943558/blgif-ezgif.com-crop.gif")
        await ctx.send(
            embed=result_embed
        )

        # Step 6: DM everyone the link
        for user in team1 + team2 + subs:
            try:
                await user.send(f"You were added to a team! Here's the link from the host:\n{shared_link}")
                
            except discord.Forbidden:
                await ctx.send(f"Couldn't DM {user.mention}.")

    @bot.command()
    @commands.has_permissions(manage_channels=True)
    async def restrictAI(ctx):
        
        if ctx.channel.id not in restricted_channels:
            restricted_channels.append(ctx.channel.id)
            await ctx.send(f"I won't talk here.")
            
    @bot.command()
    @commands.has_permissions(manage_channels=True)
    async def unrestrictAI(ctx):
        
        if ctx.channel.id in restricted_channels:
            restricted_channels.remove(ctx.channel.id)
            await ctx.send(f"I can talk here now.")
            

    @bot.command()
    
    
    

    @bot.command()
    async def help(ctx):
        embed = discord.Embed(
            title="🎮 Scrim Bot Help",
            description="Here's how to use the bot to host scrims and interact with the AI features:",
            color=discord.Color.green()
        )

        embed.add_field(
            name="📌 Scrim Command",
            value="`%hostRandomScrim [minutes]` - Starts a random scrim sign-up.",
            inline=False
        )

        embed.add_field(
            name="🕒 Time Limit",
            value="Sets how long (in minutes) players have to react with ✅ to join. Example: `%hostRandomScrim 5` waits for 5 minutes.",
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
        embed.add_field(
                name="👩‍❤️‍💋‍👩 Lesbian Mode",
                value="`%lesbomode` - Makes channel lesbian. Requires `Manage Channels` permission.",
                inline=False
            )
        
        embed.add_field(
            name="🚫 Restrict AI",
            value="`%restrictAI` - Restricts the bot from responding with AI messages in the current channel. Requires `Manage Channels` permission.",
            inline=False
        )

        embed.add_field(
            name="✅ Unrestrict AI",
            value="`%unrestrictAI` - Allows the bot to resume AI responses in the current channel. Requires `Manage Channels` permission.",
            inline=False
        )

        embed.add_field(
            name="💡 AI Interaction",
            value="The bot may respond with AI-generated messages if you reply to its messages, ping it, or DM it.",
            inline=False
        )

        embed.set_footer(text="Questions? Contact a server admin or the bot dev.")
        await ctx.send(embed=embed)

    
    bot.run(TOKEN)
