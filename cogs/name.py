import discord
from discord.ext import commands

class Names(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command()
    async def add_emoji(self, ctx, target: discord.Member, emoji_str: str):
        # Ensure the emoji is in the correct custom emoji format
        if not (emoji_str.startswith("<:") and emoji_str.endswith(">")):
            await ctx.respond("Please provide a valid custom emoji in the format <:emoji_name:emoji_id>!")
            return

        try:
            # Modify the member's nickname, ensuring it's not too long
            new_nickname = f"{emoji_str} {target.display_name[:29]}"  # Max length is 32 chars

            # Edit the member's nickname
            await target.edit(nick=new_nickname)
            await ctx.respond(f"Updated {target.display_name}'s nickname to {new_nickname}")
        
        except discord.Forbidden:
            await ctx.respond("I don't have permission to change that user's nickname. Please check my role and permissions.")
        except discord.HTTPException as e:
            await ctx.respond(f"Failed to change the nickname due to an HTTP error: {str(e)}")
        except Exception as e:
            await ctx.respond(f"An unexpected error occurred: {str(e)}")

# Add this cog to your bot in the main bot file
# bot.add_cog(Names(bot))


def setup(bot):
	bot.add_cog(Names(bot))
