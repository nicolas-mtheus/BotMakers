Quase. O conteúdo está correto, mas **algumas coisas quebraram o Markdown** do README:

1. O `git clone` ficou com **link dentro do bloco bash** (isso quebra).
2. Faltou **fechar alguns blocos de código** com ``` .
3. A parte da **tabela de comandos** não está formatada como tabela.
4. O `.env` também não foi fechado corretamente.
5. O passo **4 Execução local** deveria ter bloco `bash`.

A versão **corrigida** ficaria assim:

````markdown
# 🧙‍♂️ BotMakers 2026 - Emakers Jr.

O **BotMakers** é o assistente oficial de onboarding e engajamento da Emakers Jr. Ele foi desenvolvido para automatizar o processo de entrada de novos membros e incentivar a cultura de ajuda mútua através de um sistema de gamificação.

## 🚀 Funcionalidades

### 1. Onboarding Automatizado
* **Aceite de Regras:** Sistema de botões para garantir que o membro leu as normas.
* **Cadastro por Modal:** Coleta de nome, trilhas (Backend, Frontend, Vendas, etc.) e hobbies.
* **Auto-atribuição de Cargos:** O bot gerencia automaticamente as permissões e altera o nickname do usuário.
* **Boas-vindas Visual:** Envio de banner personalizado com as informações do novo integrante.

### 2. Sistema de Gamificação (XP & Ranking)

O bot monitora canais de dúvidas específicos para premiar membros ativos:

* **Perguntas:** Ao usar a tag `@duvida`, o membro ganha **1 XP** e a conquista **"Primeiro Código"**.

* **Respostas:** Ao responder uma dúvida usando `@resposta` (via função Reply), o membro ganha pontos baseados na velocidade:

  * < 5 min: **5 XP**
  * < 10 min: **4 XP**
  * < 15 min: **3 XP**
  * < 20 min: **2 XP**
  * < 30 min: **1 XP**

* **Conquistas (Badges):**

  * **Primeiro Código:** Primeira dúvida enviada
  * **Engajado:** 5 dúvidas respondidas
  * **Mestre da Documentação:** 10 dúvidas respondidas

---

# 🛠️ Tecnologias

* [Python 3.10+](https://www.python.org/)
* [Disnake](https://docs.disnake.dev/)
* [JSON](https://docs.python.org/3/library/json.html)

---

# 📦 Instalação e Configuração

### 1. Clone o repositório

```bash
git clone https://github.com/nicolas-mtheus/BotMakers.git
cd BotMakers
````

### 2. Instale as dependências

```bash
pip install disnake python-dotenv
```

### 3. Configuração de ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
TOKEN=SEU_TOKEN_AQUI
```

⚠️ **Nunca envie o arquivo `.env` para o GitHub.**

---

### 4. Execução local

```bash
python main.py
```

---

# ⌨️ Comandos Disponíveis

| Comando           | Descrição                                        | Permissão     |
| ----------------- | ------------------------------------------------ | ------------- |
| `!setup_regras`   | Envia a mensagem com o botão de aceite de regras | Administrador |
| `!setup_cadastro` | Envia o painel de seleção de trilhas e hobbies   | Administrador |
| `!limpar_ranking` | Zera o banco de dados JSON e limpa o ranking     | Administrador |

---

# 🔒 Segurança (DevSecOps)

Este projeto utiliza práticas de segurança para evitar exposição de credenciais:

* Secret Scanning
* Uso de variáveis de ambiente
* Monitoramento do histórico do Git para evitar exposição de tokens

---

# 👨‍💻 Desenvolvido por

**Nicolas Matheus**
**Equipe Emakers Jr.**

```

Se quiser, também posso te mostrar **3 melhorias que deixam esse README com cara de projeto profissional no GitHub (nível projeto open source)** — tipo badges, preview do bot e estrutura de pastas.
```
