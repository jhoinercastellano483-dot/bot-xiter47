"""Comandos de moderación del servidor."""

from datetime import timedelta
from typing import Optional

import discord
from discord.ext import commands

from utils import storage
from utils.embeds import aviso, crear, fallo, ok

MAX_ADVERTENCIAS = 1000


class Moderacion(commands.Cog, name="Moderación"):
    @commands.hybrid_command(name="limpiar", description="Borra varios mensajes del canal")
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def limpiar(self, ctx: commands.Context, cantidad: int = 10) -> None:
        if not 1 <= cantidad <= 100:
            await ctx.send(embed=fallo("Cantidad inválida", "Elige un número entre 1 y 100."))
            return

        # Si es comando con prefijo, también contamos el mensaje que lo invocó.
        limite = cantidad + (0 if ctx.interaction else 1)
        borrados = await ctx.channel.purge(limit=limite)
        await ctx.channel.send(
            embed=ok("🧹 Mensajes eliminados", f"Se borraron **{len(borrados)}** mensajes."),
            delete_after=5,
        )

    @commands.hybrid_command(name="expulsar", description="Expulsa a un miembro")
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def expulsar(
        self,
        ctx: commands.Context,
        miembro: discord.Member,
        *,
        motivo: str = "No especificado",
    ) -> None:
        await miembro.kick(reason=f"{motivo} | por {ctx.author}")
        await ctx.send(
            embed=ok(
                "👢 Miembro expulsado",
                f"{miembro.mention} fue expulsado.\n**Motivo:** {motivo}",
            )
        )

    @commands.hybrid_command(name="banear", description="Banea a un miembro del servidor")
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def banear(
        self,
        ctx: commands.Context,
        miembro: discord.Member,
        *,
        motivo: str = "No especificado",
    ) -> None:
        await ctx.guild.ban(miembro, reason=f"{motivo} | por {ctx.author}")
        await ctx.send(
            embed=ok(
                "🔨 Miembro baneado",
                f"{miembro.mention} fue baneado.\n**Motivo:** {motivo}",
            )
        )

    @commands.hybrid_command(name="desbanear", description="Quita el ban a un usuario")
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def desbanear(
        self,
        ctx: commands.Context,
        usuario: discord.User,
        *,
        motivo: str = "No especificado",
    ) -> None:
        try:
            await ctx.guild.unban(usuario, reason=f"{motivo} | por {ctx.author}")
        except discord.NotFound:
            await ctx.send(embed=fallo("No encontrado", "Ese usuario no está baneado."))
            return
        await ctx.send(embed=ok("✅ Ban removido", f"{usuario} ya no está baneado."))

    @commands.hybrid_command(name="silenciar", description="Silencia a un miembro temporalmente")
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    async def silenciar(
        self,
        ctx: commands.Context,
        miembro: discord.Member,
        minutos: int = 10,
        *,
        motivo: str = "No especificado",
    ) -> None:
        if minutos <= 0:
            await ctx.send(embed=fallo("Tiempo inválido", "Los minutos deben ser mayores a 0."))
            return
        await miembro.timeout(
            timedelta(minutes=minutos),
            reason=f"{motivo} | por {ctx.author}",
        )
        await ctx.send(
            embed=ok(
                "🔇 Miembro silenciado",
                f"{miembro.mention} fue silenciado por **{minutos} min**.\n**Motivo:** {motivo}",
            )
        )

    @commands.hybrid_command(name="desilenciar", description="Quita el silencio a un miembro")
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    async def desilenciar(self, ctx: commands.Context, miembro: discord.Member) -> None:
        await miembro.timeout(None, reason=f"Por {ctx.author}")
        await ctx.send(embed=ok("🔊 Silencio removido", f"{miembro.mention} ya puede hablar."))

    @commands.hybrid_command(name="advertir", description="Registra una advertencia a un miembro")
    @commands.has_permissions(moderate_members=True)
    async def advertir(
        self,
        ctx: commands.Context,
        miembro: discord.Member,
        *,
        motivo: str,
    ) -> None:
        datos = storage.cargar("warnings", {})
        clave = str(miembro.id)
        total = datos.get(clave, 0) + 1
        datos[clave] = min(total, MAX_ADVERTENCIAS)
        storage.guardar("warnings", datos)
        await ctx.send(
            embed=aviso(
                "⚠️ Advertencia registrada",
                f"{miembro.mention} lleva **{datos[clave]}** advertencias.\n**Motivo:** {motivo}",
            )
        )

    @commands.hybrid_command(name="advertencias", description="Muestra las advertencias de un miembro")
    @commands.has_permissions(moderate_members=True)
    async def advertencias(
        self,
        ctx: commands.Context,
        miembro: Optional[discord.Member] = None,
    ) -> None:
        miembro = miembro or ctx.author
        datos = storage.cargar("warnings", {})
        total = datos.get(str(miembro.id), 0)
        await ctx.send(
            embed=crear("⚠️ Advertencias", f"{miembro.mention} tiene **{total}** advertencias.")
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Moderacion(bot))
