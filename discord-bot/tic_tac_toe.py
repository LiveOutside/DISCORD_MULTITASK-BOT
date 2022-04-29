from discord.ext import commands
import discord
from discord_components import DiscordComponents, Button, Select, SelectOption
from random import randint


# CREATING SIMPLE MINI-GAME FOR BOT
class TicTacToeCog(commands.Cog):
    def __init__(self, client):
        self.client = client

        self.count = 0
        self.player1 = ""
        self.player2 = ""
        self.players_turn = ""

        self.game_over = True
        self.game_board = []
        self.end_line = [2, 5, 8]

        self.winning = [
            [0, 1, 2],
            [3, 4, 5],
            [6, 7, 8],
            [3, 4, 5],
            [0, 3, 6],
            [1, 4, 7],
            [2, 5, 8],
            [0, 4, 8],
            [2, 4, 6]
        ]

    # CHECKS FOR THE WINNING CONDITIONS ON A CURRENT BOARD
    def check_winner(self, winning_cond, mark):
        for cond in winning_cond:
            if self.game_board[cond[0]] == mark and \
                    self.game_board[cond[1]] == mark and self.game_board[cond[2]] == mark:
                self.game_over = True

    # COMMAND WHICH DISPLAYS INFO ABOUT MINI-GAME COMMANDS
    @commands.command(name='tictactoehelp', aliases=['ttthelp'])
    async def tic_tac_toe_help(self, ctx):
        await ctx.send("""**
```

🎲 TicTacToe Help
    
    📖 Commands info
        
        ➥ !tictactoe (!ttt) <@member1> <@member2> - creates a game of TicTacToe.
        ➥ !tictactoeend (!tttend) - forcibly ends an existing game of TicTacToe.
        ➥ !place (!pl) <int> - places a marked tile.

```
        **""")

    # COMMAND TO FORCIBLY END AN EXISTING GAME
    @commands.command(name='tictactoeend', aliases=['tttend'])
    async def tic_tac_toe_end(self, ctx):
        if self.game_over is False:
            await ctx.send("""
```diff
-GAME OVER
    ➥ The game was forcibly ended!
```
            """)
            await self.client.change_presence(status=discord.Status.idle,
                                              activity=discord.Game('Waiting...'))
            self.game_over = True
        else:
            await ctx.send("""
```diff
-Error
    ➥ There is no game to end.
```         """)

    # CREATES A GAME OF TIC TAC TOE BY PINGING TO GUILD.MEMBERS
    @commands.command(name='tictactoe', aliases=['ttt'])
    async def tic_tac_toe(self, ctx, p1: discord.Member, p2: discord.Member):
        if self.game_over is True:
            await self.client.change_presence(status=discord.Status.idle, activity=discord.Game('TicTacToe'))
            self.game_board = [":white_large_square:", ":white_large_square:", ":white_large_square:",
                               ":white_large_square:", ":white_large_square:", ":white_large_square:",
                               ":white_large_square:", ":white_large_square:", ":white_large_square:"]
            self.players_turn = ""
            self.game_over = False
            self.count = 0

            self.player1 = p1
            self.player2 = p2

            line = ""
            for tile in range(len(self.game_board)):
                if tile in self.end_line:
                    line += " " + self.game_board[tile]
                    await ctx.send(line)
                    line = ""
                else:
                    line += " " + self.game_board[tile]

            starter = randint(1, 2)
            if starter == 1:
                self.players_turn = self.player1
                await ctx.send("It is <@" + str(self.player1.id) + ">'s turn!")
            else:
                self.players_turn = self.player2
                await ctx.send("It is <@" + str(self.player2.id) + ">'s turn!")
        else:
            await ctx.send("""
```diff
-Error
    ➥ Finish your current game before staring a new one!
```
            """)

    # COMMAND WHICH GIVES PLAYER AN ABILITY TO SET HIS MARK ON THE FIELD
    @commands.command(name='place', aliases=['pl'])
    async def place(self, ctx, pos: int):
        if self.game_over is False:
            mark = ""
            if self.players_turn == ctx.author:
                if self.players_turn == self.player1:
                    mark = ":regional_indicator_x:"
                elif self.players_turn == self.player2:
                    mark = ":o2:"
                if 0 < pos < 10 and self.game_board[pos - 1] == ":white_large_square:":
                    self.game_board[pos - 1] = mark
                    self.count += 1

                    line = ""
                    for tile in range(len(self.game_board)):
                        if tile in self.end_line:
                            line += " " + self.game_board[tile]
                            await ctx.send(line)
                            line = ""
                        else:
                            line += " " + self.game_board[tile]

                    self.check_winner(self.winning, mark)
                    if self.game_over is True:
                        if mark == ":regional_indicator_x:":
                            await ctx.send("""
```yaml
-Rules
    ➥ X Wins! Good game.
```
                            """)
                        elif mark == ":o2:":
                            await ctx.send("""
```yaml
-Rules
    ➥ O Wins! Good game.
```
                            """)
                        await self.client.change_presence(status=discord.Status.idle,
                                                          activity=discord.Game('Waiting...'))
                        self.game_over = True
                    elif self.count >= 9:
                        await ctx.send("""
```yaml
-Rules
    ➥ No one wins! It's a tie!
```
                        """)
                        await self.client.change_presence(status=discord.Status.idle,
                                                          activity=discord.Game('Waiting...'))
                        self.game_over = True

                    if self.players_turn == self.player1:
                        self.players_turn = self.player2
                    elif self.players_turn == self.player2:
                        self.players_turn = self.player1

                else:
                    await ctx.send("""
```fix
-Miss
    ➥ Please choose an unmarked tile between 1 and 9!
```
                    """)
            else:
                await ctx.send("""
```yaml
-Rules
    ➥ Wait for the opponent, it's not your turn!
```
                    """)
        else:
            await ctx.send("""
```diff
-Error
    ➥ Start a TicTacToe game (!ttt) before using the place command!
```
            """)

    # WORKING WITH ERRORS
    @tic_tac_toe.error
    async def tic_tac_toe_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("""
```fix
-Miss
    ➥ Please mention 2 players to use the command!
```
            """)
        elif isinstance(error, commands.BadArgument):
            await ctx.send("""
```fix
-Miss
    ➥ Please mention to ping both players.
```
            """)

    # WORKING WITH ERRORS
    @place.error
    async def place_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("""
```diff
-Error
    ➥ Please mark available position!
```
            """)
        elif isinstance(error, commands.BadArgument):
            await ctx.send("""
```fix
-Miss
    ➥ Please make sure to enter an integer!
```
            """)
