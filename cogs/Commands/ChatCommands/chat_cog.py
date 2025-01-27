import discord
from discord.ext import commands
from discord import app_commands
from GPT_stories import getStoryByRole
from utils.gpt import generate_gpt_response
from utils.message_utils import send_message_in_chunks
from config.config import SERVERS

DEFAULT_ROLE = "bread"
GPT_MODEL = "gpt-4o"

class ChatCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def process_askbread(self, user_id: int, user_input: str, role: str = DEFAULT_ROLE) -> str:
        """Process the GPT request and return the response message."""
        try:
            story = getStoryByRole(role, user_id)
            response_message = await generate_gpt_response(GPT_MODEL, story, user_input)
            return response_message
        except Exception as e:
            return f"Failed to process GPT request: {e}"

    @commands.command(name="ask_bread", help="Ask a question and provide a role.")
    async def askbread_chat(self, ctx: commands.Context, user_input: str, role: str = DEFAULT_ROLE):
        """Handle the ask_bread command."""
        async with ctx.typing():
            response_message = await self.process_askbread(ctx.author.id, user_input, role)
        await ctx.send(response_message)

    @app_commands.command(name="ask_bread", description="Ask a question and provide a role.")
    @app_commands.guilds(*SERVERS)
    async def askbread(self, interaction: discord.Interaction, user_input: str, role: str = DEFAULT_ROLE):
        """Handle the ask_bread slash command."""
        await interaction.response.defer()
        response_message = await self.process_askbread(interaction.user.id, user_input, role)
        await send_message_in_chunks(response_message, interaction)

async def setup(bot: commands.Bot):
    """Set up the ChatCog."""
    await bot.add_cog(ChatCog(bot))