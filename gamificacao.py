import disnake
from disnake.ext import commands
import json
import os
from datetime import datetime, timezone

class Gamificacao(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.arquivo_dados = 'gamificacao.json'
        self.canais_duvida = [
            1493035858662785055, 1493037158657949736, 1493039484000796732, 
            1493042841126047754, 1493044264710705353, 1493045714778067024, 
            1493054457481531484
        ]
        self.canal_ranking = 1493053228420436068
        self.dados = self.carregar_dados()
        print("✅ Módulo de Gamificação carregado com sucesso!")

    def carregar_dados(self):
        if os.path.exists(self.arquivo_dados):
            with open(self.arquivo_dados, 'r') as f:
                return json.load(f)
        return {"usuarios": {}, "duvidas_ativas": {}}

    def salvar_dados(self):
        with open(self.arquivo_dados, 'w') as f:
            json.dump(self.dados, f, indent=4)

    def get_user_data(self, user_id):
        user_id = str(user_id)
        if user_id not in self.dados["usuarios"]:
            self.dados["usuarios"][user_id] = {"xp": 0, "perguntas": 0, "respostas": 0}
        return self.dados["usuarios"][user_id]

    async def atualizar_ranking(self, guild):
        canal = self.bot.get_channel(self.canal_ranking)
        if not canal: return

        usuarios_ordenados = sorted(
            self.dados["usuarios"].items(), 
            key=lambda x: x[1]["xp"], 
            reverse=True
        )

        embed = disnake.Embed(
            title="🏆 Painel de Liderança - Emakers Jr.", 
            description="Os membros mais ativos e engajados em ajudar a equipe!",
            color=disnake.Color.gold()
        )

        for i, (user_id, stats) in enumerate(usuarios_ordenados[:10]):
            membro = guild.get_member(int(user_id))
            nome = membro.display_name if membro else "Usuário Desconhecido"
            medalha = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else "⭐"
            embed.add_field(
                name=f"{medalha} {i+1}º Lugar: {nome}", 
                value=f"**XP:** {stats['xp']} | Perguntas: {stats['perguntas']} | Ajudou: {stats['respostas']} vezes", 
                inline=False
            )

        await canal.purge(limit=10)
        await canal.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        # 1. Lógica de PERGUNTAR (@duvida)
        if message.channel.id in self.canais_duvida:
            conteudo = message.clean_content.lower()
            if "@duvida" in conteudo or "@dúvida" in conteudo:
                user_id = str(message.author.id)
                user_data = self.get_user_data(user_id)
                
                self.dados["duvidas_ativas"][str(message.id)] = datetime.now(timezone.utc).isoformat()
                user_data["xp"] += 1
                user_data["perguntas"] += 1
                self.salvar_dados()
                
                await message.add_reaction("❓")
                
                cargo_primeiro = message.guild.get_role(1493959489852936292)
                if cargo_primeiro and cargo_primeiro not in message.author.roles:
                    await message.author.add_roles(cargo_primeiro)
                    await message.channel.send(f"🎉 Parabéns {message.author.mention}! Você ganhou a conquista **Primeiro Código** por fazer sua primeira pergunta!")
                
                await self.atualizar_ranking(message.guild)

        # 2. Lógica de RESPONDER (@resposta)
        if message.channel.id in self.canais_duvida and "@resposta" in message.clean_content.lower():
            if message.reference and message.reference.message_id:
                duvida_id = str(message.reference.message_id)
                
                if duvida_id in self.dados["duvidas_ativas"]:
                    data_str = self.dados["duvidas_ativas"][duvida_id]
                    data_pergunta = datetime.fromisoformat(data_str)
                    agora = datetime.now(timezone.utc)
                    minutos_passados = (agora - data_pergunta).total_seconds() / 60
                    
                    pontos = 0
                    if minutos_passados <= 5: pontos = 5
                    elif minutos_passados <= 10: pontos = 4
                    elif minutos_passados <= 15: pontos = 3
                    elif minutos_passados <= 20: pontos = 2
                    elif minutos_passados <= 30: pontos = 1
                    
                    if pontos > 0:
                        user_id = str(message.author.id)
                        user_data = self.get_user_data(user_id)
                        
                        user_data["xp"] += pontos
                        user_data["respostas"] += 1
                        
                        del self.dados["duvidas_ativas"][duvida_id]
                        self.salvar_dados()
                        
                        msg_original = await message.channel.fetch_message(message.reference.message_id)
                        await msg_original.remove_reaction("❓", self.bot.user)
                        await msg_original.add_reaction("✅")
                        
                        await message.reply(f"🚀 Excelente! Você respondeu em {minutos_passados:.1f} minutos e ganhou **{pontos} XP**!")
                        
                        if user_data["respostas"] == 5:
                            cargo_engajado = message.guild.get_role(1493959819491807303)
                            if cargo_engajado: await message.author.add_roles(cargo_engajado)
                            await message.channel.send(f"🔥 {message.author.mention} acabou de virar **Engajado** por ajudar 5 pessoas!")
                        
                        elif user_data["respostas"] == 10:
                            cargo_mestre = message.guild.get_role(1493959988127858850)
                            if cargo_mestre: await message.author.add_roles(cargo_mestre)
                            await message.channel.send(f"🧙‍♂️ {message.author.mention} ascendeu ao cargo de **Mestre da Documentação** (10 ajudas)!")
                        
                        await self.atualizar_ranking(message.guild)
                    else:
                        await message.reply("Obrigado pela ajuda! Infelizmente já se passaram mais de 30 minutos, então esta resposta não gerou pontos.")

    #comando somente para admin limpar o ranking e as dúvidas ativas (para testes ou reset geral) !limpar_ranking
    @commands.command(name="limpar_ranking")
    @commands.has_permissions(administrator=True) # Trava de segurança: só Admins podem usar
    async def limpar_ranking(self, ctx):
        # 1. Zera os dados na memória da classe
        self.dados["usuarios"] = {}
        self.dados["duvidas_ativas"] = {}
        
        # 2. Salva o estado vazio no gamificacao.json (limpa o arquivo físico)
        self.salvar_dados()
        
        # 3. Atualiza o canal do ranking para mostrar o placar zerado
        await self.atualizar_ranking(ctx.guild)
        
        # 4. Feedback visual de sucesso
        await ctx.send("🧹 **Banco de dados resetado!** O ranking e as dúvidas ativas foram limpos com sucesso.")
        
# Função obrigatória para o Discord.py carregar o módulo
def setup(bot):
    bot.add_cog(Gamificacao(bot))