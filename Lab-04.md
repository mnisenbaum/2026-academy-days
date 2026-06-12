# Lab 04 - Bruno: RESTCONF Manualmente

Bem-vindos ao **Lab 04**. Neste laboratório, vamos explorar a programabilidade de redes utilizando **RESTCONF**, um protocolo fundamental para a automação moderna (*model-driven programmability*). Utilizaremos o **Bruno**, um cliente de API open-source e leve, ideal para testar e organizar nossas requisições HTTP antes de automatizá-las com código. 

A grande vantagem de usar a Inteligência Artificial neste contexto é a facilidade de gerar os *paths* de URLs baseados em modelos YANG e estruturar os *payloads* em JSON sem precisar decorar toda a hierarquia de dados do roteador.

---

## 🎯 Objetivos
* Interagir com equipamentos reais através de APIs utilizando o protocolo RESTCONF.
* Importar e gerenciar coleções de chamadas de API no Bruno.
* Utilizar IA Generativa para descobrir *endpoints* YANG e formatar *payloads* de configuração.

---

## 🛠️ Parte 1: Preparação do Ambiente e Sandbox

Para nossos testes, utilizaremos os laboratórios gratuitos *Always-On* do Cisco DevNet. Eles já possuem o serviço RESTCONF habilitado por padrão.

### Tabela de Referência dos Sandboxes DevNet
| Sandbox | URL de Acesso | Credenciais Padrão (Usuário / Senha) |
| :--- | :--- | :--- |
| **Catalyst 8000V** | [Acessar Sandbox Cat8k](https://devnetsandbox.cisco.com/DevNet/catalog/Cat8k-Always-On_cat8k-always-on) | `developer` / `C1sco12345` |
| **Catalyst 9000** | [Acessar Sandbox Cat9k](https://devnetsandbox.cisco.com/DevNet/catalog/Cat9k-Always-On_cat9k-always-on) | `developer` / `C1sco12345` |

### Checklist de Preparação
- [ ] Escolha e acesse um dos links acima para garantir que o Sandbox está operacional.
- [ ] Anote o IP ou Hostname fornecido na página do DevNet.
- [ ] Faça o download do arquivo de coleção do Bruno: [NetAcad | RESTCONF-Bruno.json](https://github.com/mnisenbaum/2026-academy-days/blob/main/arquivos-de-configuracao/NetAcad%20_%20RESTCONF-Bruno.json).

---

## ⚙️ Parte 2: Configuração da Ferramenta (Bruno)

- [ ] Abra o aplicativo **Bruno** no seu computador.
- [ ] No menu principal, clique em **Import Collection** e selecione o arquivo `NetAcad _ RESTCONF-Bruno.json` baixado.
- [ ] Com a coleção carregada, clique no nome dela na barra lateral esquerda e acesse a aba **Variables** (ou Auth, conforme estruturado).
- [ ] Configure as variáveis de ambiente:
  - **URL Base:** `https://<IP_DO_SANDBOX>:<PORTA>/restconf` (A porta comum é 443).
  - **Username:** `developer`
  - **Password:** `C1sco12345`
- [ ] Ative a opção para ignorar certificados SSL (*Bypass SSL/TLS Certificate Verification*) nas configurações do Bruno (ícone de engrenagem), pois os Sandboxes utilizam certificados autoassinados.

---

## 🚀 Parte 3: Execução das Requisições Prontas

- [ ] Expanda a coleção no Bruno e localize a primeira requisição.
- [ ] Verifique os *Headers*. Para RESTCONF com JSON, os cabeçalhos essenciais são:
  - `Accept: application/yang-data+json`
  - `Content-Type: application/yang-data+json`
- [ ] Clique em **Send** (Enviar).
- [ ] Analise o código de status HTTP retornado (espera-se `200 OK`).
- [ ] Observe o `Response Body` em JSON para entender a organização nativa dos dados via modelo YANG.
- [ ] Execute as demais requisições prontas na coleção, observando as diferenças entre `GET` (leitura) e `PUT`/`PATCH` (escrita/atualização).

---

## 🧠 Parte 4: Desafio de Aprendizado com IA

Vamos usar a IA como uma "assistente de arquitetura YANG" para descobrir rotas e estruturas JSON, acelerando o processo.

### Checklist do Desafio:

- [ ] Abra o seu assistente de IA preferido (Gemini, ChatGPT ou Claude).
- [ ] Envie um *prompt* estruturado. Sugestão:

> "Atue como um Engenheiro de Redes especialista no ecossistema Cisco IOS-XE e RESTCONF (modelos YANG). Preciso fazer duas coisas em um roteador Catalyst:
> 1. Uma requisição GET para listar todas as interfaces (modelo ietf-interfaces).
> 2. Uma requisição PATCH ou PUT para adicionar uma 'description' na interface GigabitEthernet1.
> Forneça o endpoint para o GET, o endpoint para o PATCH, o payload JSON necessário e os Headers HTTP obrigatórios."

- [ ] Analise a resposta da IA. Ela deve indicar a rota base `/data/ietf-interfaces:interfaces`.
- [ ] Volte ao **Bruno** e crie uma **New Request** dentro da coleção:
  - **Nome:** `Listar Interfaces (Desafio)`
  - **Método:** `GET`
  - **URL:** Cole a rota fornecida pela IA combinada com a sua URL base.
- [ ] Clique em **Send** e veja as interfaces.
- [ ] Crie outra **New Request**:
  - **Nome:** `Alterar Descrição da Interface`
  - **Método:** `PATCH` (ou `PUT`).
  - **URL:** Adicione a rota específica da interface na URL.
  - **Headers:** `Content-Type: application/yang-data+json`.
  - **Body (JSON):** Cole o *payload* gerado pela IA. Exemplo esperado:

```json
{
  "ietf-interfaces:interface": {
    "name": "GigabitEthernet1",
    "description": "CONFIGURADO VIA RESTCONF NO ACADEMY DAYS 2026",
    "type": "iana-if-type:ethernetCsmacd"
  }
}