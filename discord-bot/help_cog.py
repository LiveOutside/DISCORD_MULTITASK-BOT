from discord.ext import commands


# DISPLAYING AVAILABLE COMMANDS / SENDING THEM TO ALL VCS AFTER 1-ST BOT ACTIVATION ON A CERTAIN SERVER
class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.help_message = """
```

🧠 Available commands

    🎶 Music
    
        ➥ !help
        ➥ !play (!p) <text>
        ➥ !queue (!q)
        ➥ !skip (!s)
        ➥ !clear (!cl)
        ➥ !pause (!un)
        ➥ !resume (!r)
        ➥ !leave (!l or !disconnect)
    
    🎮 Mini-games
        
        ➥ !tictactoe (!ttt):
        
            ➥ !tictactoehelp (!ttthelp)
            ➥ !tictactoeend (!tttend)
            ➥ !place (!pl) <int>
    
    💡 Other
        
        ➥ !credits
```
"""
        self.text_channel_list = []

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            for channel in guild.text_channels:
                self.text_channel_list.append(channel)

        await self.send_to_all(f'**{self.help_message}**')

    @commands.command(name="help")
    async def help(self, ctx):
        await ctx.send(self.help_message)

    async def send_to_all(self, msg):
        for text_channel in self.text_channel_list:
            await text_channel.send(f'**{msg}**')

    @commands.command(name='credits')
    async def author_credits(self, ctx):
        await ctx.send("""
```ini
[Credits]
    ➥ GITHUB: https://github.com/LiveOutside
    ➥ Discord: shmackonthedesktop#1010
```
        """)
