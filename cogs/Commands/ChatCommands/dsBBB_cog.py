import discord
from discord.ext import commands
from discord import app_commands
from GPT_stories import getStoryByRole
from utils.deepseek import generate_deepseek_response
from utils.message_utils import send_message_in_chunks
from config.config import SERVERS

DEEPSEEK_MODEL = "deepseek-chat"
DEFAULT_ROLE = "bread"

class DsBBBCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def process_dsBBB(self, user_id: int, user_input: str, role: str = DEFAULT_ROLE) -> str:
        """Process the deepseek request and return the response message."""
        try:
            story = getStoryByRole(role, user_id)
            response_message = await generate_deepseek_response(DEEPSEEK_MODEL, story, user_input)
            return response_message
        except Exception as e:
            return f"Failed to process deepseek request: {e}"

    @commands.command(name="dsbbb", help="Ask a question and provide a role using deepseek.")
    async def askbread_chat(self, ctx: commands.Context, user_input: str, role: str = DEFAULT_ROLE):
        """Handle the dsBBB command."""
        async with ctx.typing():
            response_message = await self.process_dsBBB(ctx.author.id, user_input, role)
        await ctx.send(response_message)

    @app_commands.command(name="dsbbb", description="Ask a question and provide a role using deepseek.")
    @app_commands.guilds(*SERVERS)
    async def askbread(self, interaction: discord.Interaction, user_input: str, role: str = DEFAULT_ROLE):
        """Handle the dsBBB slash command."""
        await interaction.response.defer()
        response_message = await self.process_dsBBB(interaction.user.id, user_input, role)
        await send_message_in_chunks(response_message, interaction)

async def setup(bot: commands.Bot):
    """Set up the dsBBBCog."""
    await bot.add_cog(DsBBBCog(bot))