"""Mensajes de bienvenida y despedida automáticos con depuración."""

import discord
from discord.ext import commands

from config import CANAL_BIENVENIDA_ID, CANAL_DESPEDIDA_ID
from utils.embeds import crear, ok, fallo


class Bienvenida(commands.Cog, name="Bienvenida"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    def _obtener_canal(self, guild: discord.Guild, canal_id_str: str) -> discord.TextChannel | None:
        if not canal_id_str:
            print("[Bienvenida] No hay ID de canal configurado en .env")
            return None
        try:
            canal_id = int(canal_id_str)
        except ValueError:
            print(f"[Bienvenida] ID inválido: {canal_id_str}")
            return None
        canal = guild.get_channel(canal_id)
        if canal is None:
            print(f"[Bienvenida] No se encontró el canal ID {canal_id} en el servidor {guild.name}")
            return None
        if not isinstance(canal, discord.TextChannel):
            print(f"[Bienvenida] El ID {canal_id} no es un canal de texto")
            return None
        return canal

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        print(f"[Bienvenida] Detectado JOIN: {member} en {member.guild.name}")
        canal = self._obtener_canal(member.guild, CANAL_BIENVENIDA_ID)
        if canal is None:
            return

        embed = crear(
            "✨ ᴀᴄᴄᴇsᴏ ᴄᴏɴᴄᴇᴅɪᴅᴏ",
            f"{member.mention} ha entrado a la comunidad.",
            discord.Color.from_rgb(0, 255, 136),
        )
        embed.add_field(
            name="👤 Usuario",
            value=f"{member.mention}\n`{member}`",
            inline=True,
        )
        embed.add_field(
            name="👥 Número de miembro",
            value=f"**{member.guild.member_count}**",
            inline=True,
        )
        if member.joined_at:
            embed.add_field(
                name="📅 Fecha de ingreso",
                value=f"<t:{int(member.joined_at.timestamp())}:F>",
                inline=False,
            )
        embed.add_field(
            name="💬 Bienvenida",
            value=(
                "Tu acceso se ha completado con éxito.\n\n"
                "**¿Qué encontrarás por aquí?**\n"
                "• **Cheast & Configs:** Todo listo para tu juego.\n"
                "• **Comunidad Activa:** Comparte capturas, highlights y demuestra tu nivel.\n"
                "• **Actualizaciones:** Novedades y mejoras constantes.\n\n"
                "¡A romperla! 🚀"
            ),
            inline=False,
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"ID: {member.id} · Xiter 47' $")

        try:
            await canal.send(embed=embed)
            print("[Bienvenida] Mensaje enviado")
        except discord.Forbidden:
            print("[Bienvenida] ERROR: Sin permiso para enviar mensajes")
        except discord.HTTPException as error:
            print(f"[Bienvenida] ERROR HTTP: {error}")

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member) -> None:
        print(f"[Bienvenida] Detectado LEAVE: {member} de {member.guild.name}")
        canal = self._obtener_canal(member.guild, CANAL_DESPEDIDA_ID)
        if canal is None:
            return

        embed = crear(
            "👋 ʜᴀ sᴀʟɪᴅᴏ ᴅᴇʟ sᴇʀᴠɪᴅᴏʀ",
            f"{member.mention} ha decidido abandonar la comunidad.",
            discord.Color.from_rgb(220, 53, 69),
        )
        embed.add_field(
            name="👤 Usuario",
            value=f"{member.mention}\n`{member}`",
            inline=True,
        )
        embed.add_field(
            name="👥 Miembros restantes",
            value=f"**{member.guild.member_count}**",
            inline=True,
        )
        if member.joined_at:
            embed.add_field(
                name="📅 Fecha",
                value=f"<t:{int(member.joined_at.timestamp())}:R> se unió",
                inline=False,
            )

        embed.add_field(
            name="💬 Mensaje",
            value=(
                "Su sesión en la casa ha finalizado.\n"
                "Las puertas quedan abiertas por si decide volver.\n"
                "Seguimos activos con los que se quedan para romperla. 🔥"
            ),
            inline=False,
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"ID: {member.id} · Xiter 47' $")

        try:
            await canal.send(embed=embed)
            print("[Bienvenida] Mensaje de despedida enviado")
        except discord.Forbidden:
            print("[Bienvenida] ERROR: Sin permiso para enviar mensajes")
        except discord.HTTPException as error:
            print(f"[Bienvenida] ERROR HTTP: {error}")

    @commands.hybrid_command(
        name="bienvenida",
        description="Prueba el mensaje de bienvenida",
    )
    @commands.has_permissions(administrator=True)
    async def bienvenida_cmd(self, ctx: commands.Context) -> None:
        canal = self._obtener_canal(ctx.guild, CANAL_BIENVENIDA_ID)
        if canal is None:
            await ctx.send(embed=fallo("Error", "No está configurado el canal de bienvenida."))
            return

        embed = crear(
            f"👋 ¡Bienvenido {ctx.author.display_name}! (Prueba)",
            f"Este es el mensaje de bienvenida automático.",
            discord.Color.green(),
        )
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        await canal.send(embed=embed)
        await ctx.send(embed=ok("Listo", "Mensaje de bienvenida enviado al canal."))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Bienvenida(bot))
