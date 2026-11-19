"""Protección anti-raid: expulsa a quien crea canales/roles/invites en masa."""

from collections import defaultdict, deque
from datetime import datetime, timezone
from typing import Deque, Dict, Optional, Tuple

import discord
from discord.ext import commands

from config import (
    ANTIRAID_ENABLED,
    ANTIRAID_EXEMPT_IDS,
    ANTIRAID_LIMIT,
    ANTIRAID_WINDOW,
)
from utils.embeds import crear, fallo


class AntiRaid(commands.Cog, name="Anti-Raid"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.historial: Dict[Tuple[int, int], Deque[datetime]] = defaultdict(deque)
        self.ultima_accion: Dict[int, datetime] = {}

    def _esta_exento(self, member: Optional[discord.Member]) -> bool:
        if member is None or member.bot:
            return True
        if member.id == member.guild.owner_id:
            return True
        if member.id == self.bot.user.id:
            return True
        if member.id in ANTIRAID_EXEMPT_IDS:
            return True
        permisos = member.guild_permissions
        return permisos.administrator or permisos.manage_guild

    async def _autor_por_audit(
        self,
        guild: discord.Guild,
        accion: discord.AuditLogAction,
        objetivo_id: int,
    ) -> Optional[discord.User]:
        """Consulta el registro de auditoría para saber quién creó un rol/webhook/canal."""
        if not guild.me.guild_permissions.view_audit_log:
            return None
        try:
            async for entrada in guild.audit_logs(limit=15, action=accion):
                if entrada.target and entrada.target.id == objetivo_id:
                    return entrada.user
        except (discord.Forbidden, discord.HTTPException):
            return None
        return None

    async def _registrar(
        self,
        member: Optional[discord.Member],
        guild: discord.Guild,
        tipo: str,
    ) -> None:
        if not ANTIRAID_ENABLED or member is None:
            return

        # Algunos eventos entregan User en vez de Member; lo resolvemos al miembro real.
        if not isinstance(member, discord.Member):
            member = guild.get_member(member.id)
            if member is None:
                return
        if self._esta_exento(member):
            return

        ahora = datetime.now(timezone.utc)
        reciente = self.ultima_accion.get(member.id)
        if reciente and (ahora - reciente).total_seconds() < ANTIRAID_WINDOW:
            return  # ya se tomó acción contra este miembro

        clave = (guild.id, member.id)
        eventos = self.historial[clave]
        while eventos and (ahora - eventos[0]).total_seconds() > ANTIRAID_WINDOW:
            eventos.popleft()
        eventos.append(ahora)

        if len(eventos) < ANTIRAID_LIMIT:
            return

        total = len(eventos)
        eventos.clear()
        self.ultima_accion[member.id] = ahora

        try:
            await member.kick(
                reason=f"Anti-raid: {total} {tipo} en {ANTIRAID_WINDOW}s"
            )
        except (discord.Forbidden, discord.HTTPException) as error:
            log_msg = f"No pude expulsar a {member} ({member.id}): {error}"
            print(f"[Anti-Raid] {log_msg}")
            return

        embed = fallo(
            "🛡️ Anti-Raid activado",
            f"**{member}** (`{member.id}`) fue expulsado por crear "
            f"**{total} {tipo}** en menos de **{ANTIRAID_WINDOW} s**.",
        )
        canal = guild.system_channel
        if canal is not None and canal.permissions_for(guild.me).send_messages:
            await canal.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: discord.abc.GuildChannel) -> None:
        if isinstance(
            channel,
            (discord.TextChannel, discord.VoiceChannel, discord.CategoryChannel),
        ):
            autor = await self._autor_por_audit(
                channel.guild, discord.AuditLogAction.channel_create, channel.id
            )
            if isinstance(autor, discord.Member):
                await self._registrar(autor, channel.guild, "canales")

    @commands.Cog.listener()
    async def on_guild_role_create(self, role: discord.Role) -> None:
        autor = await self._autor_por_audit(
            role.guild, discord.AuditLogAction.role_create, role.id
        )
        if isinstance(autor, discord.Member):
            await self._registrar(autor, role.guild, "roles")

    @commands.Cog.listener()
    async def on_invite_create(self, invite: discord.Invite) -> None:
        await self._registrar(invite.inviter, invite.guild, "invitaciones")

    @commands.hybrid_command(name="antiraid", description="Muestra la configuración anti-raid")
    @commands.has_permissions(administrator=True)
    async def antiraid(self, ctx: commands.Context) -> None:
        embed = crear("🛡️ Anti-Raid", "Protección contra creación masiva de elementos.")
        embed.add_field(
            name="Estado",
            value="🟢 Activo" if ANTIRAID_ENABLED else "🔴 Desactivado",
            inline=True,
        )
        embed.add_field(
            name="Umbral",
            value=f"{ANTIRAID_LIMIT} acciones en {ANTIRAID_WINDOW} s",
            inline=True,
        )
        embed.add_field(
            name="Detecta",
            value="Canales, roles e invitaciones",
            inline=False,
        )
        embed.add_field(
            name="Exentos",
            value="Dueño, administradores, gestores de servidor, bots e IDs configurados",
            inline=False,
        )
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(AntiRaid(bot))
