import asyncio
import pytest
from unittest.mock import AsyncMock, patch
from discord.ext import commands
import discord
from cogs.Commands.CurrencyCommands.admin_add_currency_cog import AdminAddCurrencyCog
from utils.users import UNBUTTERED_BAGEL_ID

@pytest.mark.asyncio
async def test_is_owner_true(setup_bot):
    bot, cog, interaction = await setup_bot(AdminAddCurrencyCog)

    interaction = AsyncMock(spec=discord.Interaction)
    interaction.user.id = UNBUTTERED_BAGEL_ID

    predicate = cog.is_owner()

    assert await predicate(interaction) == True

@pytest.mark.asyncio
async def test_is_owner_false(setup_bot):
    bot, cog, interaction = await setup_bot(AdminAddCurrencyCog)

    interaction = AsyncMock(spec=discord.Interaction)
    interaction.user.id = 123456789

    predicate = cog.is_owner()

    assert await predicate(interaction) == False