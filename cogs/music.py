import asyncio, re, streamrip, os, subprocess, requests, shutil, discord
from discord.ext import tasks, commands
from datetime import datetime, timedelta
from time import gmtime, strftime

class Music(commands.Cog, name="music"):
    tidal_regex = re.compile("(http(s)?:\/\/)?(store\.|www\.)?tidal\.com\/([a-z]{2}\/|browse\/)?(album|track|playlist)\/([a-zA-Z0-9\-]+)")
    
    def __init__(self, bot):
        self.bot = bot
        self.download_folder = os.path.abspath(self.bot.config['bot_settings']['download_folder'])
        self.request_channel = self.bot.get_channel(self.bot.config['server_settings']['request_channel'])
        self.upload_channel = self.bot.get_channel(self.bot.config['server_settings']['upload_channel'])
        self.clean_loop.start()
    
    @tasks.loop(minutes=7.5)
    async def clean_loop(self):
        async for message in self.upload_channel.history(limit=200):
            if datetime.now()-timedelta(hours=72) >= message.created_at:
                await message.delete()
    
    @commands.command(name="dl")
    async def dl(self, ctx, tidal_link_param):
        """
        Downloads music from tidal.
        1. Find a track/album at https://tidal-search.cdnbcn.codes/
        2. Copy the link from the URL bar
        3. Run the command like so with your link
            $dl [LINK]
        e.g. $dl https://store.tidal.com/ca/album/91642504
        """

        if ctx.channel == self.request_channel:
            print(f'Message from {ctx.message.author}: {ctx.message.content}')
            tidal_link_match = self.tidal_regex.search(tidal_link_param)
            if tidal_link_match is not None:
                tidal_link = tidal_link_match.group(0)
                tidal_type = tidal_link_match.group(5)
                tidal_id = tidal_link_match.group(6)

                match tidal_type:
                    case 'album':
                        media = streamrip.media.Album(client=self.bot.tidal_client, id=tidal_id)
                    case 'track':
                        media = streamrip.media.Track(client=self.bot.tidal_client, id=tidal_id)
                    case 'playlist':
                        media = streamrip.media.Playlist(client=self.bot.tidal_client, id=tidal_id)
                    case _:
                        msg = await ctx.send("<:error:958548776073719838> **Invalid Link**\nMake sure you used a valid Tidal link.\nPlease ensure you are using https://tidal-search.cdnbcn.codes/ to get the link")
                        return;

                media.load_meta()

                await self.request_channel.set_permissions(ctx.guild.default_role, send_messages=False)
                info_message = await ctx.send(f":lock: Channel locked until requested item is finished downloading.")

                try:
                    media.download(concurrent_downloads=True, max_connections=3, quality=2, parent_folder=self.download_folder, progress_bar=True, add_singles_to_folder=False)
                    _, dirs, files = next(os.walk(self.download_folder), ([],[],[]))
                    try:
                        folder_name = dirs[0]
                        zip_file = f"{folder_name}_{strftime('%Y-%m-%d_%H%M%S', gmtime())}.zip"
                    except:
                        file_name = files[0]
                        zip_file = f"{file_name}_{strftime('%Y-%m-%d_%H%M%S', gmtime())}.zip"
                    subprocess.run(["7z", "a", "-mx0", "-tzip", f"{self.download_folder}/{zip_file}", "-r", f'{self.download_folder}/*.*'])
                    resp = requests.post("https://litterbox.catbox.moe/resources/internals/api.php",
                        files={'fileToUpload': open(f'{self.download_folder}/{zip_file}','rb')},
                        data={'reqtype': 'fileupload', 'time': '72h'})
                    file_link = resp.content.decode("utf-8")

                    shutil.rmtree(self.download_folder)

                    tidal_embed = discord.Embed(
                        title=f"**{media.title}**",
                        description=f"**{'Album' if tidal_type is 'album' else 'Track'}**",
                        color=0x20e84f
                    )

                    tidal_embed.add_field(name="Download Link", value=file_link, inline=False)
                    tidal_embed.add_field(name="Tidal Link", value=tidal_link, inline=False)
                    tidal_embed.set_footer(text=f"Requested by {ctx.message.author}")

                    await self.upload_channel.send(f"{ctx.author.mention}", embed=tidal_embed)
                    await info_message.edit(content=f":unlock: Channel Unlocked\n**{media.title}** finished downloading to <#{self.upload_channel.id}>")
                except Exception as e:
                    await info_message.edit(content="<:error:958548776073719838> **Error while downloading**\nThe following Song/Album isn't available to download because of Geo Restriction or Internal Error.\nPlease ensure you are using https://tidal-search.cdnbcn.codes/ to get the link.")
                    print("An exception has occured: " + str(e))
                finally:
                    await self.request_channel.set_permissions(ctx.guild.default_role, send_messages=True)

            else:
                msg = await ctx.send("<:error:958548776073719838> **Invalid Link**\nMake sure you used a valid Tidal link.\nPlease ensure you are using https://tidal-search.cdnbcn.codes/ to get the link")
        else:
            await ctx.message.delete()
            msg = await ctx.send(f"This command can only be used in <#{self.request_channel.id}>")
            await asyncio.sleep(3)
            await msg.delete()


def setup(bot):
    bot.add_cog(Music(bot))