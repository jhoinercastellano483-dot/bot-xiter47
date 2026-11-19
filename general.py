"""Comandos generales: saludo, ayuda, ping, etc."""

import discord
from discord.ext import commands

from config import DESCRIPCION_BOT, NOMBRE_BOT
from utils.embeds import crear, ok


class General(commands.Cog, name="General"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="ping", description="Muestra la latencia del bot")
    async def ping(self, ctx: commands.Context) -> None:
        ms = round(self.bot.latency * 1000)
        await ctx.send(embed=ok("🏓 Pong!", f"Latencia: **{ms} ms**"))

    @commands.hybrid_command(name="hola", description="El bot te saluda")
    async def hola(self, ctx: commands.Context) -> None:
        await ctx.send(f"¡Hola, {ctx.author.mention}! 👋 ¿En qué puedo ayudarte?")

    @commands.hybrid_command(name="ayuda", description="Muestra todos los comandos disponibles")
    async def ayuda(self, ctx: commands.Context) -> None:
        embed = crear(
            "📚 Comandos disponibles",
            f"{DESCRIPCION_BOT}\n\nUsa `/comando` o `!comando`.",
        )
        for cog in self.bot.cogs.values():
            comandos = [
                f"`/{cmd.name}` — {cmd.short_doc or cmd.description or 'Sin descripción'}"
                for cmd in cog.get_commands()
                if not cmd.hidden
            ]
            if comandos:
                embed.add_field(name=cog.qualified_name, value="\n".join(comandos), inline=False)

        embed.set_footer(text=f"Total: {len(list(self.bot.walk_commands()))} comandos")
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="decir", description="Envía un mensaje con formato embed")
    @commands.has_permissions(manage_messages=True)
    async def decir(self, ctx: commands.Context, *, mensaje: str) -> None:
        await ctx.send(embed=crear("📢 Aviso", mensaje))

    @commands.hybrid_command(
        name="acerca",
        aliases=["about", "info"],
        description="Muestra información sobre el bot",
    )
    async def acerca(self, ctx: commands.Context) -> None:
        embed = crear("🛡️ Server Security", DESCRIPCION_BOT)
        if self.bot.user is not None:
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)

        embed.add_field(
            name="Funciones",
            value="Moderación · Seguridad · Utilidades · Entretenimiento",
            inline=False,
        )
        embed.add_field(
            name="Comandos",
            value="`/ayuda` — lista completa\n`/invitar` — enlace de invitación",
            inline=False,
        )
        embed.set_footer(text="Python + discord.py")
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="invitar", description="Obtén el enlace para invitarme")
    async def invitar(self, ctx: commands.Context) -> None:
        permisos = discord.Permissions(
            send_messages=True,
            embed_links=True,
            read_message_history=True,
            manage_messages=True,
            kick_members=True,
            ban_members=True,
            moderate_members=True,
            use_external_emojis=True,
            add_reactions=True,
        )
        url = discord.utils.oauth_url(
            self.bot.user.id,
            permissions=permisos,
            scopes=("bot", "applications.commands"),
        )
        await ctx.send(embed=crear("🔗 Invítame a tu servidor", f"[Haz clic aquí]({url})"))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(General(bot))
