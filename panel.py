"""Comando y envío automático del embed tipo Panel."""

import discord
from discord.ext import commands

from config import PANEL_AUTO_SEND, PANEL_CHANNEL_ID, PANEL_COLOR, PANEL_TITULO, PANEL_ITEMS
from utils import storage
from utils.embeds import crear


def construir_embed() -> discord.Embed:
    embed = crear(PANEL_TITULO, "", PANEL_COLOR)
    for nombre, url in PANEL_ITEMS:
        embed.add_field(name=nombre, value=url, inline=False)
    return embed


class Panel(commands.Cog, name="Panel"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        if not PANEL_AUTO_SEND or not PANEL_CHANNEL_ID:
            return
        try:
            channel_id = int(PANEL_CHANNEL_ID)
        except ValueError:
            return

        canal = self.bot.get_channel(channel_id)
        if canal is None:
            try:
                canal = await self.bot.fetch_channel(channel_id)
            except Exception:
                return

        if not isinstance(
            canal, (discord.TextChannel, discord.VoiceChannel, discord.ForumChannel)
        ):
            return

        datos = storage.cargar("panel", {})
        mensaje_id = datos.get("mensaje_id")

        embed = construir_embed()

        try:
            if mensaje_id:
                try:
                    mensaje = await canal.fetch_message(mensaje_id)
                    await mensaje.edit(embed=embed)
                    return
                except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                    pass

            mensaje = await canal.send(embed=embed)
            storage.guardar("panel", {"mensaje_id": mensaje.id})
        except (discord.Forbidden, discord.HTTPException):
            pass

    @commands.hybrid_command(
        name="panel",
        aliases=["requerimientos", "req"],
        description="Envía el embed de requerimientos del panel",
    )
    async def panel(self, ctx: commands.Context) -> None:
        embed = construir_embed()

        if ctx.message is not None and ctx.interaction is None:
            try:
                await ctx.message.delete()
            except (discord.Forbidden, discord.NotFound):
                pass

        await ctx.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Panel(bot))
