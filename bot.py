"""Punto de entrada del bot de Discord."""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path

import discord
from discord import app_commands
from discord.ext import commands

from config import COMMAND_PREFIX, DESCRIPCION_BOT, TEST_GUILD_ID, TOKEN, OWNER_ID

log = logging.getLogger("bot")

BASE_DIR = Path(__file__).resolve().parent
COGS_DIR = BASE_DIR / "cogs"


class MiBot(commands.Bot):
    """Bot principal: carga automática de cogs y sincronización de comandos."""

    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        super().__init__(
            command_prefix=commands.when_mentioned_or(COMMAND_PREFIX),
            intents=intents,
            description=DESCRIPCION_BOT,
            help_command=None,  # usamos el comando /ayuda personalizado
        )

    async def setup_hook(self) -> None:
        """Se ejecuta al iniciar, antes de conectar con Discord."""
        for archivo in sorted(COGS_DIR.glob("*.py")):
            if archivo.stem.startswith("_"):
                continue
            await self.load_extension(f"cogs.{archivo.stem}")
            log.info("Cog cargado: %s", archivo.stem)

        if TEST_GUILD_ID:
            try:
                guild = discord.Object(id=int(TEST_GUILD_ID))
            except ValueError:
                log.warning("TEST_GUILD_ID no es válido: %s", TEST_GUILD_ID)
            else:
                self.tree.copy_global_to(guild=guild)
                await self.tree.sync(guild=guild)
                log.info("Comandos sincronizados al instante en el servidor %s", TEST_GUILD_ID)
                return

        await self.tree.sync()
        log.info("Comandos slash sincronizados globalmente (pueden tardar en aparecer)")

    async def on_ready(self) -> None:
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="Server Security",
            )
        )
        log.info("Conectado como %s (ID: %s)", self.user, self.user.id)

        # Configurar roles hoisted (Founder / Bot)
        for guild in self.guilds:
            await self._setup_roles(guild)

    async def _setup_roles(self, guild: discord.Guild) -> None:
        """Crea o verifica los roles 'Founder 👑' y 'Bot 🤖' con hoist."""
        if not guild.me.guild_permissions.manage_roles:
            log.warning("No tengo el permiso 'Gestionar roles' en el servidor %s", guild.name)
            return

        # --- Rol Founder 👑 ---
        rol_founder = discord.utils.get(guild.roles, name="Founder 👑")
        if rol_founder is None:
            try:
                rol_founder = await guild.create_role(
                    name="Founder 👑",
                    color=discord.Color.gold(),
                    hoist=True,
                    reason="Rol Founder creado automáticamente",
                )
                # Mover el rol lo más alto posible (debajo del rol del bot)
                bot_top = guild.me.top_role.position
                await rol_founder.edit(position=max(bot_top - 1, 1))
                log.info("Rol 'Founder 👑' creado en %s", guild.name)
            except (discord.Forbidden, discord.HTTPException) as e:
                log.warning("No pude crear rol Founder: %s", e)
                return

        # Asignar al owner
        owner = None
        if OWNER_ID:
            try:
                owner = guild.get_member(int(OWNER_ID))
                if owner is None:
                    owner = await guild.fetch_member(int(OWNER_ID))
            except Exception:
                owner = None

        if owner is None and guild.owner_id:
            try:
                owner = guild.get_member(guild.owner_id) or await guild.fetch_member(guild.owner_id)
            except Exception:
                owner = None

        if owner and rol_founder not in owner.roles:
            try:
                await owner.add_roles(rol_founder, reason="Asignar Founder")
                log.info("Rol 'Founder 👑' asignado a %s", owner)
            except Exception as e:
                log.warning("No pude asignar Founder a %s: %s", owner, e)

        # --- Rol Bot 🤖 ---
        rol_bot = discord.utils.get(guild.roles, name="Bot 🤖")
        if rol_bot is None:
            try:
                rol_bot = await guild.create_role(
                    name="Bot 🤖",
                    color=discord.Color.blue(),
                    hoist=True,
                    reason="Rol Bot creado automáticamente",
                )
                log.info("Rol 'Bot 🤖' creado en %s", guild.name)
            except (discord.Forbidden, discord.HTTPException) as e:
                log.warning("No pude crear rol Bot: %s", e)
                return

        # Asegurar que ambos roles tengan hoist=True
        try:
            if not rol_founder.hoist:
                await rol_founder.edit(hoist=True)
            if not rol_bot.hoist:
                await rol_bot.edit(hoist=True)
        except Exception:
            pass

        # Asignar a todos los bots del servidor
        for m in guild.members:
            if m.bot and rol_bot not in m.roles:
                try:
                    await m.add_roles(rol_bot, reason="Asignar rol Bot")
                    log.info("Rol 'Bot 🤖' asignado a %s", m)
                except Exception as e:
                    log.warning("No pude asignar rol Bot a %s: %s", m, e)


async def main() -> None:
    async with MiBot() as bot:

        @bot.tree.error
        async def on_app_error(
            interaction: discord.Interaction, error: app_commands.AppCommandError
        ) -> None:
            if isinstance(error, app_commands.MissingPermissions):
                mensaje = "No tienes permisos para usar este comando."
            elif isinstance(error, app_commands.CommandOnCooldown):
                mensaje = f"Espera {error.retry_after:.1f} s antes de volver a usarlo."
            else:
                log.error("Error en comando slash: %s", error)
                mensaje = "Ocurrió un error al ejecutar el comando."

            if interaction.response.is_done():
                await interaction.followup.send(mensaje)
            else:
                await interaction.response.send_message(mensaje)

        if not TOKEN or TOKEN.startswith("PEGAR"):
            raise RuntimeError("Configura DISCORD_TOKEN en el archivo .env antes de iniciar.")

        await bot.start(TOKEN)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    asyncio.run(main())
