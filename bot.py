import discord
from discord.ext import commands
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

@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")

@bot.event
async def on_member_join(member):
    guild = member.guild
    role = discord.utils.get(guild.roles, name="👥 Cidadão")

    canal_boas_vindas = next(
        (c for c in guild.text_channels if "entrada" in c.name.lower()), None
    )

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

bot.run(TOKEN)