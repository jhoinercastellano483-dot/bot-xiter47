"""Sistema de tickets con botón y canales privados."""

from pathlib import Path

import discord
from discord.ext import commands

from config import (
    TICKET_CATEGORY_ID,
    TICKET_PANEL_CHANNEL_ID,
    TICKET_STAFF_ROLE_ID,
)
from utils.embeds import crear, ok, fallo


class TicketTypeSelect(discord.ui.Select):
    """Dropdown con los tipos de ticket."""
    def __init__(self):
        options = [
            discord.SelectOption(label="🛒 7 Días: $ 𝟓", description="Licencia de 7 días", value="license_7d", emoji="🛒"),
            discord.SelectOption(label="🛒 15 Días: $ 𝟗", description="Licencia de 15 días", value="license_15d", emoji="🛒"),
            discord.SelectOption(label="🛒 31 Días: $ 18", description="Licencia de 31 días (1 mes)", value="license_31d", emoji="🛒"),
            discord.SelectOption(label="🛒 Permanente: $ 30", description="Licencia permanente", value="license_perm", emoji="🛒"),
            discord.SelectOption(label="🛠️ Soporte / Instalación", description="Ayuda con emuladores, antivirus, etc.", value="support", emoji="🛠️"),
            discord.SelectOption(label="❓ Dudas / Consultas", description="Preguntas generales", value="question", emoji="❓"),
        ]
        super().__init__(placeholder="Selecciona el tipo de ticket...", min_values=1, max_values=1, custom_id="ticket_type_select", options=options)

    async def callback(self, interaction: discord.Interaction):
        try:
            if not interaction.response.is_done():
                await interaction.response.defer(ephemeral=True)
        except (discord.HTTPException, discord.NotFound):
            pass
        await _crear_ticket_desde_interaccion(interaction, self.values[0])


class TicketView(discord.ui.View):
    """Panel de tickets con el dropdown directo en vez del botón abajo."""
    def __init__(self) -> None:
        super().__init__(timeout=None)
        self.add_item(TicketTypeSelect())



class CerrarTicketView(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Cerrar Ticket",
        style=discord.ButtonStyle.danger,
        emoji="🔒",
        custom_id="cerrar_ticket_btn",
    )
    async def cerrar_ticket(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        assert interaction.guild is not None
        miembro = interaction.user
        rol_staff = None
        if TICKET_STAFF_ROLE_ID:
            try:
                rol_staff = interaction.guild.get_role(int(TICKET_STAFF_ROLE_ID))
            except ValueError:
                rol_staff = None

        es_staff = rol_staff is not None and rol_staff in getattr(miembro, "roles", [])
        es_dueno = interaction.channel.topic and str(miembro.id) in interaction.channel.topic

        if not (es_staff or es_dueno):
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "No tienes permiso para cerrar este ticket.",
                    ephemeral=True,
                )
            return

        try:
            if not interaction.response.is_done():
                await interaction.response.defer()
        except (discord.HTTPException, discord.NotFound):
            pass
        try:
            await interaction.channel.delete(reason=f"Ticket cerrado por {miembro}")
        except discord.Forbidden:
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "No tengo permiso para eliminar este canal.",
                    ephemeral=True,
                )
            else:
                await interaction.followup.send(
                    "No tengo permiso para eliminar este canal.",
                    ephemeral=True,
                )


async def _crear_ticket_desde_interaccion(interaction: discord.Interaction, ticket_type: str | None = None) -> None:
    guild = interaction.guild
    assert guild is not None
    usuario = interaction.user

    nombre_ticket = f"ticket-{usuario.name}"
    for canal in guild.text_channels:
        if canal.topic and str(usuario.id) in canal.topic and canal.name.startswith("ticket-"):
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message(
                        embed=fallo(
                            "Ya tienes un ticket",
                            f"Ya tienes uno abierto en {canal.mention}.",
                        ),
                        ephemeral=True,
                    )
                else:
                    await interaction.followup.send(
                        embed=fallo(
                            "Ya tienes un ticket",
                            f"Ya tienes uno abierto en {canal.mention}.",
                        ),
                        ephemeral=True,
                    )
            except (discord.HTTPException, discord.NotFound):
                pass
            return

    categoria = None
    if TICKET_CATEGORY_ID:
        try:
            categoria = guild.get_channel(int(TICKET_CATEGORY_ID))
            if not isinstance(categoria, discord.CategoryChannel):
                categoria = None
        except ValueError:
            categoria = None

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        usuario: discord.PermissionOverwrite(
            view_channel=True,
            send_messages=True,
            read_message_history=True,
        ),
        guild.me: discord.PermissionOverwrite(
            view_channel=True,
            send_messages=True,
            read_message_history=True,
            manage_channels=True,
        ),
    }

    if TICKET_STAFF_ROLE_ID:
        try:
            rol = guild.get_role(int(TICKET_STAFF_ROLE_ID))
            if rol:
                overwrites[rol] = discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True,
                )
        except ValueError:
            pass

    try:
        canal = await guild.create_text_channel(
            name=nombre_ticket,
            category=categoria,
            overwrites=overwrites,
            topic=f"Ticket de {usuario} | ID: {usuario.id}",
        )
    except discord.Forbidden:
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    embed=fallo(
                        "Sin permisos",
                        "No puedo crear canales. Dame el permiso 'Gestionar canales'.",
                    ),
                    ephemeral=True,
                )
            else:
                await interaction.followup.send(
                    embed=fallo(
                        "Sin permisos",
                        "No puedo crear canales. Dame el permiso 'Gestionar canales'.",
                    ),
                    ephemeral=True,
                )
        except (discord.HTTPException, discord.NotFound):
            pass
        return

    # Construir embed según el tipo de ticket
    if ticket_type is None:
        description = "¡Bienvenido a tu ticket! Un miembro del staff te atenderá en breve."
    else:
        match ticket_type:
            case "license_7d":
                description = (
                    "🛒 **Licencia 7 Días** – $ 𝟓 (S/. 17)\n"
                    "Compra aquí con `/pago` o solicita los métodos de pago al staff."
                )
            case "license_15d":
                description = (
                    "🛒 **Licencia 15 Días** – $ 𝟗 (S/. 30)\n"
                    "Compra aquí con `/pago` o solicita los métodos de pago al staff."
                )
            case "license_31d":
                description = (
                    "🛒 **Licencia 31 Días** – $ 18 (S/. 60)\n"
                    "Compra aquí con `/pago` o solicita los métodos de pago al staff."
                )
            case "license_perm":
                description = (
                    "🛒 **Licencia Permanente** – $ 30 (S/. 100)\n"
                    "Compra aquí con `/pago` o solicita los métodos de pago al staff."
                )
            case "support":
                description = (
                    "🛠️ **Soporte / Instalación**\n"
                    "Ayuda con emuladores, antivirus, errores, etc.\n"
                    "Un miembro del staff te atenderá en breve."
                )
            case "question":
                description = (
                    "❓ **Dudas / Consultas**\n"
                    "Deja tu pregunta detallada y te responderemos lo más pronto posible."
                )
            case _:
                description = "¡Bienvenido a tu ticket! Un miembro del staff te atenderá en breve."
    embed = crear(
        "🎫 Ticket de Soporte",
        (description,),
        discord.Color.from_rgb(25, 25, 25),
    )
    embed.set_footer(text=f"Ticket de {usuario.display_name}")

    await canal.send(
        content=f"{usuario.mention}",
        embed=embed,
        view=CerrarTicketView(),
    )


class Tickets(commands.Cog, name="Tickets"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        self.bot.add_view(TicketView())
        self.bot.add_view(CerrarTicketView())

    @commands.hybrid_command(
        name="ticket",
        description="Abre un ticket de soporte",
    )
    async def ticket(self, ctx: commands.Context) -> None:
        if ctx.interaction:
            try:
                if not ctx.interaction.response.is_done():
                    await ctx.interaction.response.defer(ephemeral=True)
            except (discord.HTTPException, discord.NotFound):
                pass
        await self._crear_ticket_desde_ctx(ctx)

    async def _crear_ticket_desde_ctx(self, ctx: commands.Context) -> None:
        guild = ctx.guild
        assert guild is not None

        nombre_ticket = f"ticket-{ctx.author.name}"
        for canal in guild.text_channels:
            if canal.topic and str(ctx.author.id) in canal.topic and canal.name.startswith("ticket-"):
                await ctx.send(
                    embed=fallo(
                        "Ya tienes un ticket",
                        f"Ya tienes uno abierto en {canal.mention}.",
                    )
                )
                return

        categoria = None
        if TICKET_CATEGORY_ID:
            try:
                categoria = guild.get_channel(int(TICKET_CATEGORY_ID))
                if not isinstance(categoria, discord.CategoryChannel):
                    categoria = None
            except ValueError:
                categoria = None

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            ctx.author: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True,
            ),
            guild.me: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True,
                manage_channels=True,
            ),
        }

        if TICKET_STAFF_ROLE_ID:
            try:
                rol = guild.get_role(int(TICKET_STAFF_ROLE_ID))
                if rol:
                    overwrites[rol] = discord.PermissionOverwrite(
                        view_channel=True,
                        send_messages=True,
                        read_message_history=True,
                    )
            except ValueError:
                pass

        try:
            canal = await guild.create_text_channel(
                name=nombre_ticket,
                category=categoria,
                overwrites=overwrites,
                topic=f"Ticket de {ctx.author} | ID: {ctx.author.id}",
            )
        except discord.Forbidden:
            await ctx.send(
                embed=fallo(
                    "Sin permisos",
                    "No puedo crear canales. Necesito el permiso 'Gestionar canales'.",
                )
            )
            return

        embed = crear(
            "🎫 Ticket de Soporte",
            (
                f"¡Bienvenido a tu ticket, {ctx.author.mention}!\n\n"
                "Un miembro del staff te atenderá en breve.\n"
                "Describe tu consulta aquí."
            ),
            discord.Color.from_rgb(25, 25, 25),
        )
        embed.set_footer(text=f"Ticket de {ctx.author.display_name}")

        await canal.send(
            content=f"{ctx.author.mention}",
            embed=embed,
            view=CerrarTicketView(),
        )

    @commands.hybrid_command(
        name="cerrar",
        description="Cierra el ticket actual",
    )
    async def cerrar(self, ctx: commands.Context) -> None:
        if not ctx.channel.name or not ctx.channel.name.startswith("ticket-"):
            await ctx.send(
                embed=fallo("No es un ticket", "Este comando solo funciona dentro de un canal de ticket.")
            )
            return

        rol_staff = None
        if TICKET_STAFF_ROLE_ID:
            try:
                rol_staff = ctx.guild.get_role(int(TICKET_STAFF_ROLE_ID))
            except ValueError:
                rol_staff = None

        es_staff = rol_staff is not None and rol_staff in getattr(ctx.author, "roles", [])
        es_dueno = ctx.channel.topic and str(ctx.author.id) in ctx.channel.topic

        if not (es_staff or es_dueno):
            await ctx.send(
                embed=fallo("Sin permiso", "No puedes cerrar este ticket.")
            )
            return

        await ctx.send("Cerrando ticket...")
        try:
            await ctx.channel.delete(reason=f"Ticket cerrado por {ctx.author}")
        except discord.Forbidden:
            await ctx.send(
                embed=fallo("Sin permisos", "No tengo permiso para eliminar canales.")
            )

    @commands.hybrid_command(
        name="ticketpanel",
        description="Envía el panel de tickets con botón (solo staff)",
    )
    @commands.has_permissions(administrator=True)
    async def ticketpanel(self, ctx: commands.Context) -> None:
        canal_id = TICKET_PANEL_CHANNEL_ID
        canal = None
        if canal_id:
            try:
                canal = ctx.guild.get_channel(int(canal_id))
            except ValueError:
                canal = None

        if canal is None:
            canal = ctx.channel

        embed = crear(
            "PANEL Xiter 47' $ • Tu mejor opcion",
            (
                "Domina cada partida con nuestro poderoso **Aimbot**, **No Recoil**, **Sniper Scope** y **Attributes Weapon 2+**.\n"
                "Disfruta de funciones exclusivas como **ESP Line**, **Wallhack**, **Ghost Hack**, **Teleport Base**, **Snap Magnet**, **Invisible** y **Sync Fly 100m**.\n"
                "Personaliza tu experiencia con **SkinChanger**, **ArmasChanger** y **Keybinds Personalizados**.\n"
                "**Más de 25 funciones en un solo panel**, con una gran variedad de opciones para llevar tu juego al siguiente nivel. 🔥\n\n"
                "**🛠 DETALLES**\n"
                "• Compatibilidad con Windows: **8/10/11**\n"
                "• Compatibilidad con CPU: **Intel/AMD/Xeon**\n"
                "• Idiomas disponibles: **Inglés/Español/Portugués**\n\n"
                "**🚀 FUNCIONES**\n"
                "**Aimbot**\n"
                "**Ignore Derrubados**\n"
                "**Attributes Weapon 2+**\n"
                "**Modo Noite**\n"
                "**BackJump**\n"
                "**Sabor Tela Parada**\n"
                "**No Recoil**\n"
                "**Bloquear Mira**\n"
                "**Skyler Infinit**\n"
                "**Troca Rapido**\n"
                "**Sniper Scope**\n"
                "**ESP Line**\n"
                "**Ghost Hack**\n"
                "**Teleport Base**\n"
                "**Wall Hack**\n"
                "**Teleport Lite**\n"
                "**Tp Mark**\n"
                "**Underground**\n"
                "**Under Player 50m**\n"
                "**Down Enemy**\n"
                "**Snap Magnet**\n"
                "**Killstreak**\n"
                "**Auto Habilidade**\n"
                "**Sync Fly 100m**\n"
                "**Invisible**\n"
                "**Keybinds Personalizados**\n"
                "**SkinChanger**\n"
                "**ArmasChanger**\n\n"
                "**💰 PRECIOS**\n"
                "• 7 Días: **S/. 17.00 – $ 5.00**\n"
                "• 15 Días: **S/. 30.00 – $ 9.00**\n"
                "• 31 Días: **S/. 60.00 – $ 18.00**\n"
                "• Permanente: **S/. 100.00 – $ 30.00**\n\n"
                "📩 **PARA ADQUIRIR NUESTRO PRODUCTO, ABRE UN TICKET Y PONTE EN CONTACTO CON EL EQUIPO DEL STAFF**"
            ),
            discord.Color.from_rgb(25, 25, 25),
        )
        embed.set_footer(text="PANEL Xiter 47' $ • Tu mejor opcion")

        imagen_path = Path(__file__).resolve().parent.parent / "data" / "panel_image.jpg"
        archivo = discord.File(imagen_path, filename="panel_image.jpg")
        embed.set_image(url="attachment://panel_image.jpg")

        await canal.send(embed=embed, file=archivo, view=TicketView())

        if canal != ctx.channel:
            await ctx.send(
                embed=ok("Panel enviado", f"El panel de tickets se envió en {canal.mention}.")
            )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Tickets(bot))
