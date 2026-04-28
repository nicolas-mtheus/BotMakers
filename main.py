import disnake
from disnake.ext import commands
import os
from dotenv import load_dotenv
load_dotenv()
token = os.getenv('TOKEN')

bot = commands.Bot(command_prefix="!", intents=disnake.Intents.all())

# --- CONFIGURAÇÕES DE IDs ---
ID_CARGO_CANDIDATO = 1492920808169799772
ID_CARGO_LEITOR = 1492944955176648914 # CRIE UM CARGO NOVO E COLOQUE O ID AQUI
ID_CANAL_BEM_VINDO = 1492921954171359312
ID_CANAL_REGRAS = 1492922019799371937

CARGOS_TRILHAS = {
    "Dev Backend": 1492920063815188630,
    "Dev Frontend": 1492920168261877913,
    "Vendas": 1492920290957856828,
    "Processos Internos": 1492920452933226608,
    "Marketing": 1492920577001001182
}

# --- ETAPA 2: CADASTRO (COM OPÇÕES PREDEFINIDAS) ---
class NomeModal(disnake.ui.Modal):
    def __init__(self, hobbies, trilhas):
        self.hobbies = hobbies
        self.trilhas = trilhas
        super().__init__(
            title="Finalizar Cadastro",
            components=[
                disnake.ui.TextInput(label="Seu Nome Completo", custom_id="nome", max_length=32)
            ]
        )

    async def callback(self, inter: disnake.ModalInteraction):
        await inter.response.defer(ephemeral=True)
        nome = inter.text_values["nome"]

        # 1. Muda Nick
        try: await inter.author.edit(nick=nome)
        except: pass

        # 2. Gerencia Cargos (Dá Candidato, remove Leitor)
        cargo_cand = inter.guild.get_role(ID_CARGO_CANDIDATO)
        cargo_leitor = inter.guild.get_role(ID_CARGO_LEITOR)
        
        await inter.author.add_roles(cargo_cand)
        if cargo_leitor: await inter.author.remove_roles(cargo_leitor)

        # 3. Dá os cargos das Trilhas e Hobbies
        for t in self.trilhas:
            c = inter.guild.get_role(CARGOS_TRILHAS.get(t))
            if c: await inter.author.add_roles(c)
        
        for h in self.hobbies:
            role = disnake.utils.get(inter.guild.roles, name=h)
            if not role: role = await inter.guild.create_role(name=h)
            await inter.author.add_roles(role)

        # 4. Boas-vindas (COM BANNER LOCAL)
        canal_bv = bot.get_channel(ID_CANAL_BEM_VINDO)
        embed = disnake.Embed(
            title="🚀 Novo Candidato Aprovado no Onboarding!",
            description=f"O ecossistema da Emakers Jr acabou de crescer. Bem-vindo, **{nome}**!",
            color=disnake.Color.purple()
        )
        embed.set_thumbnail(url=inter.author.display_avatar.url)
        embed.add_field(name="💼 Trilhas", value=", ".join(self.trilhas) or "Nenhuma", inline=False)
        embed.add_field(name="🎯 Hobbies", value=", ".join(self.hobbies) or "Nenhum", inline=False)
        embed.set_footer(text="Processo Seletivo Emakers 2026")

        # --- A MÁGICA DA IMAGEM AQUI ---
        # Abre o arquivo local e anexa no embed
        arquivo_banner = disnake.File("baner_emakers.png", filename="baner_emakers.png")
        embed.set_image(url="attachment://baner_emakers.png")

        if canal_bv:
            # Atenção: Tem que passar o parâmetro 'file=arquivo_banner' aqui no send
            await canal_bv.send(content=f"🎉 Dêem as boas-vindas ao {inter.author.mention}!", file=arquivo_banner, embed=embed)
        
        await inter.edit_original_message(content="✨ Cadastro concluído! O servidor foi liberado para você.")

class CadastroView(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.hobbies = []
        self.trilhas = []

    @disnake.ui.string_select(
        placeholder="Escolha seus Hobbies",
        options=[
            disnake.SelectOption(label="Jogar Games", emoji="🎮"),
            disnake.SelectOption(label="Jogar Futebol", emoji="⚽"),
            disnake.SelectOption(label="Estudar", emoji="📚"),
            disnake.SelectOption(label="Ler", emoji="📖")
        ],
        min_values=1, max_values=3
    )
    async def sel_hobbies(self, select, inter):
        self.hobbies = inter.values
        await inter.response.send_message(f"Selecionado: {', '.join(inter.values)}", ephemeral=True)

    @disnake.ui.string_select(
        placeholder="Escolha suas Trilhas (Máx 2)",
        options=[disnake.SelectOption(label=t) for t in CARGOS_TRILHAS.keys()],
        min_values=1, max_values=2
    )
    async def sel_trilhas(self, select, inter):
        self.trilhas = inter.values
        await inter.response.send_message(f"Selecionado: {', '.join(inter.values)}", ephemeral=True)

    @disnake.ui.button(label="Concluir Registro", style=disnake.ButtonStyle.green)
    async def finalizar(self, button, inter):
        if not self.trilhas:
            return await inter.response.send_message("Selecione as trilhas primeiro!", ephemeral=True)
        await inter.response.send_modal(NomeModal(self.hobbies, self.trilhas))

# --- ETAPA 1: REGRAS ---
class RegrasView(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @disnake.ui.button(label="Li e aceito as regras", style=disnake.ButtonStyle.green, custom_id="aceitar_regras")
    async def aceitar(self, button, inter):
        cargo_leitor = inter.guild.get_role(ID_CARGO_LEITOR)
        await inter.author.add_roles(cargo_leitor)
        await inter.response.send_message("✅ Regras aceitas! Vá para o canal #complete-seu-cadastro.", ephemeral=True)

@bot.event
async def on_ready():
    print(f"✅ O Mago {bot.user} está pronto!")

@bot.command()
async def setup_regras(ctx):
    regras_texto = """
Bem-vindo(a)! Para garantir um ambiente colaborativo, seguro e organizado durante o nosso Processo Seletivo, pedimos que todos sigam as diretrizes da comunidade do Discord, bem como as regras específicas do nosso servidor abaixo:

🤝 **1. Respeito e Profissionalismo**
• Trate todos com respeito, independentemente de cargo ou opinião.
• Discussões saudáveis são sempre bem-vindas, mas não toleramos ataques pessoais, preconceito ou ofensas.
• Mantenha um tom profissional e evite linguajar inadequado.

📂 **2. Uso Adequado dos Canais**
• Utilize cada canal para o seu propósito correto (ex.: #bate-papo-geral para conversas e #dúvidas-gerais para questões do processo).
• Evite desviar do assunto (off-topic) em canais sérios e não faça spam.

🔒 **3. Privacidade e Confidencialidade**
• É estritamente proibido compartilhar dados confidenciais da empresa ou informações pessoais de outros candidatos e membros.

💬 **4. Boas Práticas de Comunicação**
• Seja claro(a) e objetivo(a) para facilitar a colaboração e a produtividade.
• Utilize as formatações do Discord para facilitar a leitura em textos longos.
• Evite o excesso de emojis, GIFs e mensagens fragmentadas que possam poluir o chat.

🎧 **5. Etiqueta nos Canais de Voz**
• Dê preferência ao uso de fones de ouvido para evitar retorno/eco.
• Mantenha seu microfone mutado (silenciado) quando não estiver falando.
• Não interrompa reuniões, dinâmicas ou calls em andamento sem necessidade.

🏢 **6. Conformidade com as Normas da Empresa**
• Os valores e regras da Emakers Jr também se aplicam no ambiente virtual. Respeite a hierarquia.
• Fique atento(a) aos canais de anúncios para não perder atualizações.

⚠️ **Atenção às Consequências**
O descumprimento destas regras pode resultar em advertências e na **expulsão do Processo Seletivo**.

❓ **Dúvidas ou denúncias?** Sinta-se à vontade para chamar um organizador no privado. O sigilo é garantido.
"""
    embed = disnake.Embed(
        title="📜 Regras da Comunidade - Emakers Jr",
        description=regras_texto,
        color=disnake.Color.red()
    )
    await ctx.send(embed=embed, view=RegrasView())

@bot.command()
async def setup_cadastro(ctx):
    embed = disnake.Embed(title="📝 Cadastro de Candidato", description="Selecione suas opções abaixo:", color=disnake.Color.blue())
    await ctx.send(embed=embed, view=CadastroView())

bot.load_extension("gamificacao")

bot.run(token)