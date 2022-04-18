import asyncio

import discord
from discord.ext import commands

class Help(commands.Cog, name="help"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help(self, context):
        """
        List all commands from every Cog the bot has loaded.
        """
        embed = discord.Embed(title="Help", description="List of available commands:", color=0x42F56C)
        for i in self.bot.cogs:
            if i.capitalize() == "Help":
                continue
            cog = self.bot.get_cog(i.lower())
            commands = cog.get_commands()
            command_list = [command.name for command in commands]
            command_description = [command.help for command in commands]
            help_text = '\n'.join(f'{self.bot.command_prefix}{n} - {h}' for n, h in zip(command_list, command_description))
            embed.add_field(name=i.capitalize(), value=f'```{help_text}```', inline=False)
        await context.send(embed=embed)

    @commands.command(pass_context=True)
    @commands.has_permissions(administrator=True)
    async def clean(self, ctx, limit: int):
        await ctx.message.delete()
        await ctx.channel.purge(limit=limit)
        msg = await ctx.send('Cleared by {}'.format(ctx.author.mention))
        await asyncio.sleep(3)
        await msg.delete()

def setup(bot):
    bot.add_cog(Help(bot))
