# Lab 06 - O SDK do CML2 e Agentes de IA

Bem-vindos ao **Lab 06**. Até agora, utilizamos IA Generativa para escrever scripts que nós mesmos copiamos, colamos e executamos. No entanto, quando lidamos com bibliotecas complexas e em constante atualização, como o SDK oficial do CML2 (`virl2_client`), a abordagem de *copiar e colar* do ChatGPT pode ser frustrante. A IA tende a "alucinar" parâmetros ou usar versões obsoletas da documentação, exigindo muitas tentativas e erros.

A solução para isso? **Agentes de IA (AI Agents)**. Em vez de pedir para a IA escrever o código para nós executarmos, daremos a ela um ambiente onde ela mesma pode planejar, escrever, consultar a documentação oficial, corrigir os próprios erros e executar a tarefa. Utilizaremos ferramentas como o **Opencode** ou **Claude Desktop** para isso.

---

## 🎯 Objetivos
* Compreender a diferença entre usar um assistente de código (LLM padrão) e um Agente Autônomo.
* Utilizar o Opencode (ou Claude Desktop) para interagir com o SDK `virl2_client`.
* Recriar a topologia do **Lab 01** (4 roteadores em anel com OSPF) de forma 100% automatizada.
* Praticar a engenharia de *prompt* focada em delegar tarefas para agentes.

---

## 🛠️ Parte 1: Preparação do Ambiente do Agente

O Opencode e agentes similares executam comandos no seu terminal para testar o código antes de entregá-lo. Por isso, exigem um ambiente Unix-like (Linux, macOS ou WSL no Windows).

### Checklist de Preparação
- [ ] Certifique-se de estar usando um terminal Linux, macOS ou o WSL (Windows Subsystem for Linux).
- [ ] Instale ou abra o **Opencode** (ou utilize o Claude Desktop configurado para acessar seu terminal).
- [ ] Verifique se você possui Python instalado no seu ambiente: `python3 --version`.
- [ ] Tenha em mãos as credenciais do seu POD do CML2: `URL`, `Usuário` e `Senha`.

---

## 🤖 Parte 2: O Modo "Plan" (Planejamento)

Os melhores agentes trabalham em duas fases: Planejamento (onde avaliam o que precisa ser feito) e Construção (onde executam).

- [ ] Abra o terminal interativo do agente (Opencode).
- [ ] Pressione a tecla **`Tab`** para alternar para o modo **Plan** (Planejar). Neste modo, o agente não altera nada no seu computador; ele apenas estrutura a lógica.
- [ ] Forneça o contexto completo para o agente. Copie e cole o *prompt* abaixo, ajustando as credenciais:

```text
Atue como um Engenheiro de Automação de Redes especialista em Cisco Modeling Labs (CML2).
Preciso que você crie um script Python utilizando a biblioteca oficial 'virl2_client' para automatizar a criação do meu Lab 01.

Aqui estão as credenciais do meu servidor (use-as no script):
- URL: https://<URL_DO_SEU_CML>
- Usuário: <SEU_USUARIO>
- Senha: <SUA_SENHA>
- Ignorar certificados SSL (verify=False).

O script deve realizar as seguintes ações:
1. Criar um novo laboratório (Lab) chamado "Lab 01 - Automação via Agente".
2. Adicionar 4 nós (nodes) do tipo "csr1000v" (ou "cat8000v", conforme disponibilidade do servidor), nomeados R1, R2, R3 e R4.
3. Conectar as interfaces na seguinte topologia de anel:
   - R1 (GigabitEthernet1) <--> R2 (GigabitEthernet1)
   - R2 (GigabitEthernet2) <--> R3 (GigabitEthernet1)
   - R3 (GigabitEthernet2) <--> R4 (GigabitEthernet1)
   - R4 (GigabitEthernet2) <--> R1 (GigabitEthernet2)
4. Iniciar os nós (start) após a criação da topologia.

Analise a documentação do virl2_client se necessário e me apresente o plano de execução.
```

- [ ] Analise a resposta do agente. Ele deverá descrever os passos lógicos, como a criação do cliente `ClientLibrary`, a instanciação do `Lab`, a criação de `Nodes` e `Links`.

---

## 🚀 Parte 3: A Mágica Acontece (Modo Build)

Agora que o agente sabe o que fazer, vamos dar permissão para ele executar o trabalho sujo: programar, instalar dependências e rodar o código.

- [ ] Pressione a tecla **`Tab`** novamente para alternar para o modo **Build** (Construir/Executar).
- [ ] Diga ao agente para seguir em frente: *"Execute o plano aprovado."*
- [ ] **Observe a execução:** O agente irá:
  1. Verificar se o `virl2_client` está instalado. Se não estiver, ele executará o `pip install virl2_client` sozinho.
  2. Criar o arquivo Python (ex: `criar_lab01.py`).
  3. Rodar o script (`python3 criar_lab01.py`).
  4. Analisar os logs de erro. (Se houver erro de sintaxe, o agente lerá o erro no terminal, reescreverá o código e tentará novamente, sem que você precise intervir).
- [ ] Acesse a interface web do seu CML2 e verifique o laboratório "Lab 01 - Automação via Agente" sendo criado e inicializado como num passe de mágica!

---

## 🧠 Parte 4: Aprendizado e Exploração

O perigo de usar agentes autônomos é perder a oportunidade de aprender *como* o código funciona, já que a máquina faz tudo. Vamos forçar a IA a nos ensinar.

### Checklist de Aprendizado
- [ ] Continue na mesma janela de chat do Opencode/Claude Desktop.
- [ ] Envie um novo desafio, mas desta vez, com foco em didática. Use este *prompt*:

```text
Excelente trabalho criando o laboratório! Agora eu quero aprender a usar o virl2_client.
Preciso que você altere o script para fazer uma nova tarefa: Colocar uma descrição ("Configurado pelo Agente") em todas as interfaces conectadas da topologia que acabamos de criar.

No entanto, eu NÃO quero que você simplesmente execute. Quero que você crie o código Python e me explique, passo a passo, como a estrutura de classes do SDK funciona para acessar uma interface de um nó específico e inserir as configurações iniciais (bootstrap/configuração de dia 0). Atue como meu instrutor.
```

- [ ] Leia atentamente a explicação. Você aprenderá conceitos do SDK, como acessar propriedades de nós (`lab.nodes()`) e interagir com o ciclo de vida do laboratório no CML2.

---
*Fim do Lab 06. Você elevou o nível da automação, passando de assistentes de código para Agentes Autônomos. No próximo laboratório (Lab 07), vamos integrar isso ao MCP (Model Context Protocol) para uma comunicação ainda mais nativa com o Claude.*