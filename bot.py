from os.path import exists
import os, time, sys, streamrip
import discord, toml, json
from discord.ext import commands, tasks

config = toml.load("./config.toml")
blacklisted_users = []

class TiDLBot(discord.ext.commands.Bot):
    def __init__(self, config, command_prefix, activity, intents):
        self.config = config
        self.tidal_client = streamrip.clients.TidalClient()
        failures = 0
        while not self.tidal_client.logged_in:
            if exists('tidal.json'):
                with open('tidal.json') as json_file:
                    self.tidal_data = json.load(json_file)
                    self.tidal_client.login(user_id=self.tidal_data['user_id'], country_code=self.tidal_data['country_code'], access_token=self.tidal_data['access_token'],
                        token_expiry=self.tidal_data['token_expiry'], refresh_token=self.tidal_data['refresh_token'])
                    if not self.tidal_client.logged_in:
                        self.tidal_client.login()
            else:
                self.tidal_client.login()
            if not self.tidal_client.logged_in:
                failures = failures+1
            if failures >= 5:
                print("Failed to login with Tidal")
                sys.exit(1)
        
        self.tidal_data = self.tidal_client.get_tokens()

        with open('tidal.json', 'w') as outfile:
            json.dump(self.tidal_data, outfile)
        super().__init__(command_prefix=config['bot_settings']['bot_prefix'], activity=discord.Activity(type=discord.ActivityType[config['bot_settings']['activity']['type']],
            name=config['bot_settings']['activity']['name']), intents=discord.Intents.default())

    async def on_ready(self):
        print(f'Logged on as {self.user}!')
        if __name__ == "__main__":
            for file in os.listdir("./cogs"):
                if file.endswith(".py"):
                    extension = file[:-3]
                    try:
                        self.load_extension(f"cogs.{extension}")
                        print(f"Loaded extension '{extension}'")
                    except Exception as e:
                        exception = f"{type(e).__name__}: {e}"
                        print(f"Failed to load extension {extension}\n{exception}")

    async def on_message(self, message):
        if message.author == self.user or message.author.bot or message.author.id in blacklisted_users:
            return
        await self.process_commands(message)

    async def on_command_completion(self, ctx):
        print(f"Executed {ctx.command.name} command in {ctx.guild.name} (ID: {ctx.message.guild.id}) by {ctx.message.author} (ID: {ctx.message.author.id}))")

    async def on_command_error(context, error):
        if isinstance(error, commands.CommandOnCooldown):
            minutes, seconds = divmod(error.retry_after, 60)
            hours, minutes = divmod(minutes, 60)
            hours = hours % 24
            embed = discord.Embed(
                title="Hey, please slow down!",
                description=f"You can use this command again in {f'{round(hours)} hours' if round(hours) > 0 else ''} {f'{round(minutes)} minutes' if round(minutes) > 0 else ''} {f'{round(seconds)} seconds' if round(seconds) > 0 else ''}.",
                color=0xE02B2B
            )
            await context.send(embed=embed)
        elif isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title="Error!",
                description="You are missing the permission `" + ", ".join(
                error.missing_perms) + "` to execute this command!",
                color=0xE02B2B
            )
            await context.send(embed=embed)
        elif isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                title="Error!",
                description=str(error).capitalize(),
                # We need to capitalize because the command arguments have no capital letter in the code.
                color=0xE02B2B
            )
            await context.send(embed=embed)
        elif isinstance(error, commands.MaxConcurrencyReached):
            embed = discord.Embed(
                title="Error!",
                description="Please wait for the previous job to finish!\nTry Again later.",
                color=0xE02B2B
            )
            embed.set_footer(text=f"Requested by {context.message.author}.")
            await context.send(embed=embed)
        raise error

client = TiDLBot(config=config, command_prefix=config['bot_settings']['bot_prefix'], activity=discord.Activity(type=discord.ActivityType[config['bot_settings']['activity']['type']],
            name=config['bot_settings']['activity']['name']), intents=discord.Intents.default())

client.remove_command("help") # Remove default bot help command



client.run(config['bot_settings']['token'])