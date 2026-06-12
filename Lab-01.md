# Lab 01: Scripts IOS-XE Gerados por IA para o CML2

## 1. Objetivos do Aprendizado
* Familiarização prática com a interface e ciclo de vida de laboratórios no Cisco Modeling Labs (CML2).
* Utilização estratégica de Engenharia de Prompts (IA Generativa) para aceleração de provisionamento de planos de controle.
* Validação de conectividade IP e adjacências OSPFv2 no ecossistema Cisco IOS-XE (IOL).

## 2. Metodologia
A atividade será executada de forma híbrida: a infraestrutura física/lógica e o design da topologia serão construídos manualmente pelo aluno no CML2, enquanto a lógica de configuração de rede (endereçamento IP e roteamento dinâmico) será gerada via LLM (Large Language Model) com base em diretrizes técnicas estruturadas.

* **Produto Final:** Topologia em losango convergida, com rotas aprendidas via OSPFv2 e validadas por comandos `show`.

---

## 3. Guia de Execução Prática

### Etapa 1: Acesso ao Ambiente
- [ ] Conecte-se ao seu POD do CML2 na nuvem (via credenciais fornecidas pelo instrutor) ou abra o CML2 Workbench instalado localmente em sua máquina.
- [ ] Na dashboard inicial, clique em **"Add Lab"** para criar um espaço de trabalho limpo. Defina o nome como `Lab_01_IA_Scripts`.

### Etapa 2: Construção da Topologia e Documentação Visual
- [ ] Arraste **4 nós do tipo IOL (IOS On Linux)** para a área de trabalho. Renomeie-os sequencialmente de `R1` a `R4`.
- [ ] Conecte as interfaces dos roteadores de modo a formar uma topologia em **losango** (Exemplo: R1 conectado a R2 e R3; R4 conectado a R2 e R3).
- [ ] Adicione um elemento do tipo **Note (Caixa de Texto)** na topologia e insira rigorosamente os seguintes parâmetros de design:
  * **Endereçamento dos Links:** Subredes IPv4 no formato `10.x.y.0/24`, onde `x` e `y` representam os IDs dos roteadores conectados, obedecendo a regra `x < y`.
    * *Exemplo:* Link R1 para R2 $\rightarrow$ `10.1.2.0/24`
    * *Exemplo:* Link R2 para R4 $\rightarrow$ `10.2.4.0/24`
  * **Interfaces Loopback:** Cada roteador deve possuir uma interface `Loopback0` configurada com o endereço `x.x.x.x/32`, onde `x` é o número do roteador (Exemplo: R1 = `1.1.1.1/32`).
  * **Roteamento Dinâmico:** Configurar o OSPFv2 (Processo 1, Área 0) e anunciar todos os links e loopbacks participantes.
- [ ] **Validação Intermediária:** Capture um *print screen* da topologia contendo o diagrama visível e a caixa de texto de requisitos. Salve o arquivo para o relatório.

### Etapa 3: Engenharia de Prompt e Geração de Configurações
- [ ] Acesse a ferramenta de IA Generativa de sua preferência (Gemini, ChatGPT ou Claude).
- [ ] Submeta um prompt estruturado para gerar os blocos de configuração. 

*Sugestão de prompt técnico para copiar e adaptar:*
```text
Atue como um Engenheiro de Redes sênior certificado CCIE. Gere scripts de configuração no padrão Cisco IOS-XE para 4 roteadores (R1, R2, R3 e R4) conectados em uma topologia tipo losango no CML2. 

Considere as conexões:
- R1 conecta em R2 e R3
- R4 conecta em R2 e R3

Adote estritamente as regras:
1) Links IPv4: formato 10.x.y.0/24 (onde x e y são os números dos routers e x < y).
2) Loopback 0: endereço x.x.x.x/32 para cada roteador x.
3) OSPFv2: Ative o processo 1, configure o Router ID como o IP da loopback, e anuncie todas as redes (links e loopback) na Área 0 de forma explícita nas interfaces ou via comando network.

Forneça os blocos de comando de forma isolada e limpa para cada roteador, prontos para CLI.