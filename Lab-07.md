# Lab 07 - Usando o MCP do CML2 para configurá-lo

Bem-vindos ao **Lab 07**, o laboratório final da nossa trilha de automação no Academy Days 2026. 

Neste laboratório, daremos o passo definitivo na interação humano-máquina utilizando o **Model Context Protocol (MCP)**. O MCP permite conectar o "cérebro" da IA (como o Claude ou o agente Opencode) diretamente às APIs do Cisco Modeling Labs (CML2). Em vez de pedir para a IA escrever um script Python para você executar, o modelo ganha "ferramentas nativas" para interagir com o roteador de forma autônoma.

Vamos recriar a topologia do **Lab 01** (4 roteadores em anel), mas desta vez, a IA fará o trabalho atuando diretamente sobre a infraestrutura através do servidor MCP.

---

## 🎯 Objetivos
* Compreender o Model Context Protocol (MCP) como a ponte nativa entre as LLMs e as APIs de rede.
* Preparar e inicializar o servidor MCP oficial do CML2.
* Configurar o ambiente utilizando o Opencode (via prompt autônomo) ou o Claude Desktop (editando configurações do WSL).
* Provisionar uma topologia de rede completa através de comandos de linguagem natural e *Tool Calls*.

---

## 🛠️ Parte 1: Preparação do Ambiente e Conexão MCP

Você pode escolher um de dois caminhos para inicializar o MCP. Siga o checklist da opção que melhor se adequa ao seu ambiente.

> **Referência:** [Repositório GitHub - Hands-on MCP and CML](https://github.com/mnisenbaum/2026-academy-days/blob/main/labs-workshop-cisco-u/13-hands-on-mcp-and-cml/1.md)

### Opção A: Usando o Opencode (Recomendado para Linux/Mac/WSL)
O Opencode é capaz de preparar o próprio ambiente se você fornecer o prompt com a engenharia correta. Ele instalará tudo o que precisa sozinho.

- [ ] Abra o terminal interativo do Opencode no modo **Plan** (pressione a tecla Tab para alternar os modos).
- [ ] Copie e cole o prompt de inicialização abaixo. Lembre-se de substituir as credenciais fictícias pelas credenciais reais do seu CML2:

> Atue como Engenheiro de Automação de Redes. O ambiente atual está limpo. Execute as etapas abaixo de forma estritamente sequencial:
> 
> **Preparação:** Instale o gerenciador de pacotes uv, uvs, pipx e tudo que for necessário, clone o repositório do servidor MCP para CML (cml-mcp) e instale as dependências via uv sync. Não esqueça do pyats.
> **Configuração:** Defina as variáveis de ambiente necessárias (CML_URL='https://<SEU_IP>/', CML_USERNAME='<SEU_USUARIO>', CML_PASSWORD='<SUA_SENHA>', CML_VERIFY_CERT='false').
> **Conexão:** Inicialize o servidor MCP no seu contexto para expor as ferramentas da API do CML2.
> **Validação:** Crie um laboratório de teste vazio chamado 'Teste Opencode' para validar a conectividade antes de provisionar a topologia de rede final.

- [ ] Mude para o modo **Build** (pressione Tab novamente) e aprove a execução. A IA instalará todas as dependências e criará o laboratório de teste validando o MCP.

### Opção B: Usando o Claude Desktop (com WSL)
Se você estiver utilizando o aplicativo Claude Desktop no Windows, precisaremos apontar o MCP para rodar dentro do ecossistema WSL.

- [ ] Localize o arquivo de configuração do Claude Desktop (`claude_desktop_config.json`).
- [ ] Edite o arquivo adicionando o bloco de configuração abaixo (cole exatamente como está, respeitando os espaços para validar o JSON). Lembre-se de ajustar as variáveis para o seu ambiente:

    {
      "mcpServers": {
        "cml-mcp": {
          "command": "wsl",
          "args": [
            "bash",
            "-c",
            "CML_URL='https://<SEU_IP>/' CML_USERNAME='<SEU_USUARIO>' CML_PASSWORD='<SUA_SENHA>' CML_VERIFY_CERT='false' uv run --directory /caminho/para/cml-mcp mcp-server-cml"
          ]
        }
      }
    }

- [ ] Salve o arquivo e reinicie o Claude Desktop. 
- [ ] Verifique se apareceu um ícone de "ferramenta" (martelo ou tomada) na interface do Claude, indicando que as *tools* do CML2 foram carregadas com sucesso.

---

## 🚀 Parte 2: Recriando o Lab 01 via Ferramentas MCP

Com o MCP conectado, a IA se torna a operadora da rede. Não precisamos mais pedir que ela escreva código Python para nós rodarmos.

- [ ] No Opencode ou Claude Desktop (com as ferramentas já disponíveis no contexto), envie o seguinte prompt:

> As ferramentas do MCP do CML2 estão conectadas no seu contexto. Por favor, utilize-as para provisionar a topologia do nosso Lab 01.
> 
> Instruções:
> 1. Crie um novo laboratório chamado "Lab 01 - MCP Provisioning".
> 2. Adicione 4 roteadores Cisco (utilize as imagens csr1000v ou cat8000v disponíveis) e nomeie-os R1, R2, R3 e R4.
> 3. Conecte os roteadores rigorosamente em anel: R1(Gi1) com R2(Gi1), R2(Gi2) com R3(Gi1), R3(Gi2) com R4(Gi1), R4(Gi2) com R1(Gi2).
> 4. Inicie (start) todo o laboratório imediatamente após a criação dos links.

- [ ] Acompanhe a execução da IA. Você notará que ela fará as chamadas nativas de sistema (*Tool Calls* como `create_lab`, `create_node`, `create_link`, `start_node`).
- [ ] Acesse a interface web do seu CML2 e valide visualmente a topologia sendo criada e as máquinas virtuais realizando o *boot*.

---

## 🧠 Parte 3: Aprendizado e Operações de Dia 1

O verdadeiro poder do MCP é o contexto bidirecional: a IA não apenas "empurra" configurações, ela **lê o estado operacional da rede** e atua sobre ele dinamicamente.

- [ ] Após os roteadores estarem 100% iniciados no CML2, desafie o agente com o prompt de operação abaixo para observar a integração na prática:

> A topologia já está rodando. Quero que você faça o seguinte de forma autônoma:
> 1. Utilize a ferramenta adequada do MCP para acessar o roteador R1.
> 2. Leia o estado atual das interfaces dele e me explique, passo a passo, como você fez isso.
> 3. Em seguida, utilize a ferramenta integrada do pyATS (através do MCP) para configurar uma interface Loopback0 com o IP 1.1.1.1/32 no R1 e ateste que a configuração foi um sucesso.

- [ ] **Análise:** A IA abrirá a conexão com o equipamento virtualmente, executará comandos operacionais, interpretará o retorno nativamente através das ferramentas, construirá a configuração da Loopback e enviará a alteração, confirmando o estado final.

---
**Fim do Lab 07.** Parabéns por concluir esta jornada prática! Você presenciou a evolução da automação de redes, desde a execução de scripts estáticos até a operação autônoma dirigida por intenção (Intent-Based) utilizando o Model Context Protocol e Agentes de IA.