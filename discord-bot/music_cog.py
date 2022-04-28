import discord
from discord.ext import commands
from youtube_dl import YoutubeDL


class MusicCog(commands.Cog):
    def __init__(self, client):
        self.client = client

        self.is_playing = False
        self.is_paused = False

        self.music_queue = []
        self.song = ''
        self.YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                               'options': '-vn'}

        self.vc = None

    # SEARCHING FOR THE MUSIC ON YT
    def search_yt(self, item):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info("ytsearch:%s" % item, download=False)['entries'][0]
            except Exception as error:
                return error

        return {'source': info['formats'][0]['url'], 'title': info['title']}

    # PLAYING NEXT SONG FROM THE QUEUE
    def play_next(self):
        if len(self.music_queue) > 0:
            self.is_playing = True

            m_url = self.music_queue[0][0]['source']

            self.music_queue.pop(0)

            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
        else:
            self.is_playing = False

    # MOVING TO VC
    async def play_music(self, ctx):
        if len(self.music_queue) > 0:
            self.is_playing = True
            m_url = self.music_queue[0][0]['source']

            if self.vc is None or not self.vc.is_connected():
                self.vc = await self.music_queue[0][1].connect()

                if self.vc is None:
                    await ctx.send("""
```diff
-Error
    ➥ Unable to reach the voice channel right now.
```
                    """)
                    return

            else:
                await self.vc.move_to(self.music_queue[0][1])

            self.music_queue.pop(0)
            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
            await self.client.change_presence(status=discord.Status.idle, activity=discord.Game(self.song))

        else:
            self.is_playing = False

    # SETTING VC
    @commands.command(name="play", aliases=["p"])
    async def play(self, ctx, *args):
        query = " ".join(args)
        voice_channel = ctx.author.voice.channel

        if voice_channel is None:
            await ctx.send("""
```diff
-Error
    ➥ You're currently not connected to a voice channel
```
            """)
        elif self.is_paused:
            self.vc.resume()
        else:
            song = self.search_yt(query)

            if type(song) == type(True):
                await ctx.send("""
```diff
-Error
    ➥ Unable to find the song.
```
                """)

            else:
                await ctx.send(f"""
```yaml
-Music
    ➥ {song['title']} added to the queue.
```
                """)

                self.music_queue.append([song, voice_channel])
                self.song = song['title']

                if self.is_playing is False:
                    await self.play_music(ctx)

    # COMMAND TO PAUSE A SONG
    @commands.command(name="pause", aliases=['un'])
    async def pause(self, ctx, *args):
        if self.is_playing:
            self.is_playing = False
            self.is_paused = True
            self.vc.pause()
        elif self.is_paused:
            self.vc.resume()

    # COMMAND TO RESUME A SONG
    @commands.command(name="resume", aliases=["r"])
    async def resume(self, ctx, *args):
        if self.is_paused:
            self.vc.resume()
            self.is_playing = True
            self.is_paused = False

    # COMMAND TO SKIP A SONG
    @commands.command(name="skip", aliases=["s"])
    async def skip(self, ctx):
        if self.vc is not None and self.vc:
            self.vc.stop()
            await self.play_music(ctx)

    # COMMAND TO VIEW THE LIST OF SONGS IN THE QUEUE
    @commands.command(name="queue", aliases=["q"])
    async def queue(self, ctx):
        params = ""

        for i in range(0, len(self.music_queue)):
            if i > 4:
                break
            params += f"    ➥ {i + 1}. " + self.music_queue[i][0]['title'] + "\n"
        if params != "":
            await ctx.send(f"""
```yaml
-Queue
{params}
```
            """)
        else:
            await ctx.send("""
```yaml
-Queue
    ➥ There is no music in the queue right now.
```
            """)

    # COMMAND TO CLEAR THE QUEUE
    @commands.command(name="clear", aliases=["cl"])
    async def clear(self, ctx):
        if self.vc is not None and self.is_playing:
            self.vc.stop()
        await self.client.change_presence(status=discord.Status.idle, activity=discord.Game('Waiting...'))
        self.music_queue = []
        await ctx.send("""
```yaml
-Queue
    ➥ The music queue was successfully cleared.
```
        """)

    # COMMAND TO FORCIBLY LEAVE THE VC
    @commands.command(name="leave", aliases=["disconnect", "l"])
    async def leave(self, ctx):
        self.is_playing = False
        self.is_paused = False
        await self.client.change_presence(status=discord.Status.idle, activity=discord.Game('Waiting...'))
        await self.vc.disconnect()
        await ctx.send(f"""
```diff
-BOT DISCONNECTED
    ➥ Bot disconnected from the channel.
```
        """)
