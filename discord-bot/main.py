import discord
from discord.ext import commands
from help_cog import HelpCog
from music_cog import MusicCog
from tic_tac_toe import TicTacToeCog

client = commands.Bot(command_prefix='!')

TOKEN = ''
client.remove_command('help')
client.add_cog(HelpCog(client))
client.add_cog(MusicCog(client))
client.add_cog(TicTacToeCog(client))


# CHECKING THE ACTIVATION (SUPPORT FUNC) / SETTING THE IDLE STATUS
@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.idle, activity=discord.Game('Waiting...'))
    print(f'{client.user} is ready!')


# CAUSES AN ERROR, BECAUSE SELF.VC IS NONE TYPE OBJECT IN MUSIC COG
# (AT FIRST - THAN IT BECOMES AUTHOR.VC (NON NONE TYPE OBJECT)); NEVERTHELESS, EVERYTHING WORKS HOW IT SHOULD.
@client.event
async def on_voice_state_update(member, prev, current):
    if client.user in prev.channel.members and len([m for m in prev.channel.members if not m.bot]) == 0:
        channel = discord.utils.get(client.voice_clients, channel=prev.channel)
        await client.change_presence(status=discord.Status.idle, activity=discord.Game('Waiting...'))
        await channel.disconnect()


client.run(TOKEN)
