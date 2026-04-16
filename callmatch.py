import disnake
import asyncio
import random

class GerenciadorDinamica:
    def __init__(self, bot, cog_gamificacao):
        self.bot = bot
        self.cog_gamificacao = cog_gamificacao # Referência para podermos dar XP depois
        self.processando_dinamica = False

    async def tentar_iniciar(self, canal_fila):
        # Se já estiver rodando uma rotina ou não tiver 2 pessoas, ignora
        if self.processando_dinamica or len(canal_fila.members) < 2:
            return

        self.processando_dinamica = True
        
        ID_CANAL_PRIVADO = 1494316522397765632
        ID_CANAL_LOG = 1494315662594670653
        
        canal_privado = canal_fila.guild.get_channel(ID_CANAL_PRIVADO)
        canal_log = canal_fila.guild.get_channel(ID_CANAL_LOG)
        
        # Sorteia 2 pessoas
        selecionados = random.sample(canal_fila.members, 2)
        
        try:
            for membro in selecionados:
                await canal_privado.set_permissions(membro, view_channel=True, connect=True, speak=True)
                await membro.move_to(canal_privado)
            
            if canal_log:
                await canal_log.send(f"🤖 **Dinâmica Automática:** Match formado entre {selecionados[0].mention} e {selecionados[1].mention}! Iniciando monitoramento de 5 minutos...")
            
            # Inicia o monitoramento em segundo plano
            self.bot.loop.create_task(self.monitorar_call(selecionados, canal_privado, canal_fila, canal_log))
            
        except Exception as e:
            print(f"Erro ao iniciar dinâmica: {e}")
            self.processando_dinamica = False

    async def monitorar_call(self, membros, canal_privado, canal_fila, canal_log):
        tempo_total = 5 * 60
        intervalo = 30
        loops = tempo_total // intervalo
        sucesso = True

        for _ in range(loops):
            await asyncio.sleep(intervalo)
            
            for membro in membros:
                # Verifica se saiu ou mutou
                if (membro.voice is None or 
                    membro.voice.channel.id != canal_privado.id or 
                    membro.voice.self_mute or 
                    membro.voice.mute or 
                    membro.voice.self_deaf):
                    sucesso = False
                    break
            
            if not sucesso:
                if canal_log:
                    await canal_log.send(f"⚠️ A dinâmica entre {membros[0].mention} e {membros[1].mention} falhou. Alguém saiu ou mutou o microfone.")
                break

        # Se deu tudo certo, distribui o XP usando o arquivo de gamificação
        if sucesso:
            XP_POR_DINAMICA = 15
            for membro in membros:
                # Chama um método que vamos criar lá no gamificacao.py
                await self.cog_gamificacao.adicionar_xp_dinamica(membro, XP_POR_DINAMICA)
            
            if canal_log:
                await canal_log.send(f"🎉 Tempo esgotado! {membros[0].mention} e {membros[1].mention} concluíram a dinâmica e ganharam **{XP_POR_DINAMICA} XP** cada!")

        # Cleanup: tira permissões e DESCONECTA da call
        for membro in membros:
            await canal_privado.set_permissions(membro, overwrite=None)
            if membro.voice:
                try:
                    # Mover para 'None' derruba/desconecta o usuário da chamada de voz
                    await membro.move_to(None)
                except disnake.Forbidden:
                    pass
        
        # Libera o sistema para o próximo match
        self.processando_dinamica = False