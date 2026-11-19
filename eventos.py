"""Manejadores de eventos y errores."""

import logging

import discord
from discord.ext import commands

from utils.embeds import fallo

log = logging.getLogger("eventos")


class Eventos(commands.Cog, name="Eventos"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        if isinstance(error, commands.CommandNotFound):
            return

        if isinstance(error, commands.MissingRequiredArgument):
            mensaje = "Falta un argumento. Usa `/ayuda` para ver cómo se llama el comando."
        elif isinstance(error, commands.BadArgument):
            mensaje = "Uno de los argumentos no es válido."
        elif isinstance(error, commands.MissingPermissions):
            mensaje = "No tienes los permisos necesarios para este comando."
        elif isinstance(error, commands.BotMissingPermissions):
            mensaje = "No tengo los permisos necesarios para hacer eso."
        elif isinstance(error, commands.CommandOnCooldown):
            mensaje = f"Este comando está en enfriamiento. Espera {error.retry_after:.1f} s."
        else:
            log.error("Error en comando %s: %s", ctx.command, error)
            mensaje = "Ocurrió un error inesperado."

        await ctx.send(embed=fallo("Error", mensaje))

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Eventos(bot))
