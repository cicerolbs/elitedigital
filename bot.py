import discord
from discord.ext import commands
from discord.ui import View, Select, Button
from discord import app_commands
import os
from dotenv import load_dotenv
import json
from flask import Flask
from threading import Thread

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
    visitante = discord.utils.get(member.guild.roles, name="🚧 Visitante")
    if visitante:
        await member.add_roles(visitante)

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
        super().__init__(placeholder="Selecione seus cargos...", min_values=0, max_values=len(options), options=options, custom_id="cargo_select")

    async def callback(self, interaction: discord.Interaction):
        roles = [discord.utils.get(self.guild.roles, name=value) for value in self.values if discord.utils.get(self.guild.roles, name=value)]

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

    for categoria, canais in estrutura.items():
        cat = discord.utils.get(guild.categories, name=categoria)
        if not cat:
            cat = await guild.create_category(name=categoria)
        for canal in canais:
            if isinstance(canal, tuple) and canal[1] == "voice":
                if not discord.utils.get(guild.voice_channels, name=canal[0]):
                    await guild.create_voice_channel(name=canal[0], category=cat)
            else:
                if not discord.utils.get(guild.text_channels, name=canal):
                    await guild.create_text_channel(name=canal, category=cat)

    await criar_cargos(ctx)
    await regras(ctx)
    await menu_interativo(ctx)
    await ctx.send("✅ Setup finalizado com sucesso!")

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
        ("👑 Fundador", discord.Colour.red()),
        ("🚧 Visitante", discord.Colour.dark_gray())
    ]
    for nome, cor in cargos:
        if not discord.utils.get(ctx.guild.roles, name=nome):
            await guild.create_role(name=nome, colour=cor)

@bot.command()
@commands.has_permissions(administrator=True)
async def menu_interativo(ctx):
    canal = discord.utils.get(ctx.guild.text_channels, name="🎭escolha-seu-perfil")
    if not canal:
        await ctx.send("Canal '🎭escolha-seu-perfil' não encontrado.")
        return

    async for msg in canal.history(limit=50):
        if msg.author == bot.user and msg.components:
            try:
                await msg.delete()
            except:
                pass

    embed = discord.Embed(
        title="🎭 Escolha suas Áreas de Interesse",
        description=(
            "Use o menu abaixo para selecionar os cargos que deseja receber.\n"
            "Você pode marcar **mais de um!**\n\n"
            "🧠 **Estudante**\n"
            "🎨 **Designer Gráfico**\n"
            "👨‍💻 **Dev / Criador de Jogos**\n"
            "🧊 **Modelador 3D**\n"
            "🎮 **Gamer**"
        ),
        color=discord.Color.blurple()
    )

    await canal.send(embed=embed, view=CargoMenuView(ctx.guild))

@bot.command()
@commands.has_permissions(administrator=True)
async def regras(ctx):
    canal = discord.utils.get(ctx.guild.text_channels, name="📜regras")
    if not canal:
        await ctx.send("Canal de regras não encontrado.")
        return

    async for msg in canal.history(limit=50):
        if msg.author == bot.user and msg.components:
            try:
                await msg.delete()
            except:
                pass

    embed = discord.Embed(
        title="📜 Regras do Servidor",
        description=(
            "1. Respeite todos os membros.\n"
            "2. Proibido spam, flood ou divulgação sem permissão.\n"
            "3. Use os canais de forma adequada.\n"
            "4. Assédio ou discurso de ódio resultará em ban.\n"
            "5. Aproveite o servidor com educação e colaboração."
        ),
        color=discord.Color.gold()
    )

    button = Button(label="Aceito as Regras", style=discord.ButtonStyle.success)

    async def button_callback(interaction):
        visitante = discord.utils.get(ctx.guild.roles, name="🚧 Visitante")
        cidadao = discord.utils.get(ctx.guild.roles, name="👥 Cidadão")
        if visitante in interaction.user.roles:
            await interaction.user.remove_roles(visitante)
        if cidadao:
            await interaction.user.add_roles(cidadao)
        await interaction.response.send_message("✅ Regras aceitas! Bem-vindo ao servidor!", ephemeral=True)

    button.callback = button_callback
    view = View()
    view.add_item(button)
    await canal.send(embed=embed, view=view)

@bot.command()
@commands.has_permissions(administrator=True)
async def backup(ctx):
    guild = ctx.guild
    data = {}
    for cat in guild.categories:
        data[cat.name] = []
        for chan in cat.channels:
            perms = {str(role): {"read": perm.read_messages} for role, perm in chan.overwrites.items() if isinstance(role, discord.Role)}
            data[cat.name].append({"name": chan.name, "type": str(chan.type), "permissions": perms})
    with open("server_backup.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    await ctx.send(file=discord.File("server_backup.json"))

# Mantém o bot vivo no Render
app = Flask('')

@app.route('/')
def home():
    return "Bot EliteDigital está ativo!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

keep_alive()
bot.run(TOKEN)
