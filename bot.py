import discord
from discord.ext import commands
from discord.ui import View, Select
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.messages = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

emoji_cargo = {
    "🧠": "🧠 Estudante",
    "🎨": "🎨 Designer",
    "👨‍💻": "👨‍💻 Dev/Gamedev",
    "🧊": "🧊 Modelador 3D",
    "🎮": "🎮 Gamer"
}

@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")

@bot.event
async def on_member_join(member):
    guild = member.guild
    role = discord.utils.get(guild.roles, name="👥 Cidadão")
    canal_boas_vindas = next((c for c in guild.text_channels if "entrada" in c.name.lower()), None)

    if role:
        await member.add_roles(role)
    if canal_boas_vindas:
        await canal_boas_vindas.send(
            f"👋 Olá {member.mention}, seja bem-vindo(a) ao **EliteDigital**! Você recebeu o cargo **{role.name}** automaticamente."
        )

@bot.command()
@commands.has_permissions(administrator=True)
async def setup(ctx):
    guild = ctx.guild

    estrutura = {
        "🏠 BEM-VINDO(A)": ["🚪entrada", "📜regras", "🎭escolha-seu-perfil"],
        "🧠 CONHECIMENTO DIGITAL": [
            "💻programação", "🎨design-grafico", "🎮criação-de-jogos",
            "📚tutoriais-e-cursos", "🏆desafios-da-semana", "🧾diario-de-progresso"
        ],
        "🕹️ GAMES & SOCIAL": [
            "🎲matchmaking", "📢bate-papo-geral", ("🎧call-1", "voice"),
            ("🎧call-2", "voice"), ("🎙️call-estudo", "voice")
        ],
        "💬 ÁREA DE TROCA": [
            "📂mostre-seu-projeto", "🤝feedback-criativo", "💡dicas-e-hacks"
        ],
        "👑 ELITE & ADMINISTRAÇÃO": [
            "👨‍🏫administração", "🎯painel-de-progresso", "📣avisos-do-fundador"
        ]
    }

    await ctx.send("Criando categorias e canais...")

    for categoria, canais in estrutura.items():
        cat = await guild.create_category(name=categoria)
        for canal in canais:
            if isinstance(canal, tuple) and canal[1] == "voice":
                await guild.create_voice_channel(name=canal[0], category=cat)
            else:
                await guild.create_text_channel(name=canal, category=cat)

    await ctx.send("Servidor EliteDigital configurado com sucesso! ✅")

@bot.command()
@commands.has_permissions(administrator=True)
async def criar_cargos(ctx):
    guild = ctx.guild

    cargos = [
        ("🧠 Estudante", discord.Colour.blue()),
        ("🎨 Designer", discord.Colour.magenta()),
        ("👨‍💻 Dev/Gamedev", discord.Colour.purple()),
        ("🧊 Modelador 3D", discord.Colour.dark_teal()),
        ("🎮 Gamer", discord.Colour.orange()),
        ("👥 Cidadão", discord.Colour.light_grey()),
        ("🧙 Mentor", discord.Colour.gold()),
        ("👑 Fundador", discord.Colour.red())
    ]

    await ctx.send("Criando cargos...")

    for nome, cor in cargos:
        await guild.create_role(name=nome, colour=cor)

    await ctx.send("Cargos criados com sucesso! ✅")

class CargoSelect(Select):
    def __init__(self, guild):
        self.guild = guild
        options = [
            discord.SelectOption(label="Estudante", emoji="🧠", value="🧠 Estudante"),
            discord.SelectOption(label="Designer Gráfico", emoji="🎨", value="🎨 Designer"),
            discord.SelectOption(label="Dev / Criador de Jogos", emoji="👨‍💻", value="👨‍💻 Dev/Gamedev"),
            discord.SelectOption(label="Modelador 3D", emoji="🧊", value="🧊 Modelador 3D"),
            discord.SelectOption(label="Gamer", emoji="🎮", value="🎮 Gamer")
        ]
        super().__init__(placeholder="Selecione seus cargos...", min_values=0, max_values=len(options), options=options)

    async def callback(self, interaction: discord.Interaction):
        roles = []
        for value in self.values:
            role = discord.utils.get(self.guild.roles, name=value)
            if role:
                roles.append(role)

        for emoji, nome_cargo in emoji_cargo.items():
            role = discord.utils.get(self.guild.roles, name=nome_cargo)
            if role and role in interaction.user.roles and nome_cargo not in self.values:
                await interaction.user.remove_roles(role)

        for role in roles:
            await interaction.user.add_roles(role)

        await interaction.response.send_message("✅ Cargos atualizados com sucesso!", ephemeral=True)

class CargoMenuView(View):
    def __init__(self, guild):
        super().__init__(timeout=None)
        self.add_item(CargoSelect(guild))

@bot.command()
@commands.has_permissions(administrator=True)
async def menu_interativo(ctx):
    canal = next((c for c in ctx.guild.text_channels if "escolha-seu-perfil" in c.name), None)
    if not canal:
        await ctx.send("Canal 'escolha-seu-perfil' não encontrado.")
        return

    embed = discord.Embed(
        title="🎭 Escolha suas Áreas de Interesse",
        description=(
            "Use o menu abaixo para selecionar os cargos que deseja receber.\n"
            "Você pode marcar **mais de um**!\n\n"
            "🧠 **Estudante**\n"
            "🎨 **Designer Gráfico**\n"
            "👨‍💻 **Dev / Criador de Jogos**\n"
            "🧊 **Modelador 3D**\n"
            "🎮 **Gamer**"
        ),
        color=discord.Color.blurple()
    )

    view = CargoMenuView(ctx.guild)
    await canal.send(embed=embed, view=view)
    await ctx.send("✅ Menu interativo com embed enviado com sucesso!")

bot.run(TOKEN)
