# 🧠 Guia de Engenharia de Prompt para DevNetOps
### Baseado nas Diretrizes Oficiais da Anthropic · Workshop DevNetOps

> **Público-alvo:** Professores de TI que utilizam IA generativa para automação e configuração de redes Cisco.  
> **Objetivo:** Apresentar os princípios fundamentais para escrever prompts eficazes, com exemplos práticos aplicados a redes de computadores.

---

## 📋 Índice

1. [A Metáfora Central](#-a-metáfora-central)
2. [Os 6 Princípios Fundamentais](#-os-6-princípios-fundamentais)
   - [1. Seja Claro e Direto](#1-seja-claro-e-direto)
   - [2. Adicione Contexto e Motivação](#2-adicione-contexto-e-motivação)
   - [3. Use Exemplos — Few-Shot Prompting](#3-use-exemplos--few-shot-prompting)
   - [4. Estruture com Tags XML](#4-estruture-com-tags-xml)
   - [5. Atribua um Papel — Role Prompting](#5-atribua-um-papel--role-prompting)
   - [6. Encadeie Prompts para Tarefas Complexas](#6-encadeie-prompts-para-tarefas-complexas)
3. [Princípio Bônus: Afirmativo vs. Negativo](#-princípio-bônus-afirmativo-vs-negativo)
4. [Referência Rápida](#-referência-rápida)
5. [Exercícios Práticos](#-exercícios-práticos)
6. [Recursos Oficiais](#-recursos-oficiais)

---

## 🎯 A Metáfora Central

> *"Pense no prompt como instruções para um funcionário novo brilhante, que não tem nenhum contexto sobre o seu projeto. Quanto mais claro você for, melhor o resultado."*
> — Anthropic Prompt Engineering Guide

### O Teste do Colega

Antes de enviar um prompt para a IA, aplique este teste simples:

> 📌 **Mostre seu prompt para um colega com pouco contexto sobre a tarefa e peça para ele seguí-lo. Se ele ficar confuso, a IA vai ficar também.**

Este único hábito resolve a maioria dos problemas com prompts mal escritos.

---

## 🏗️ Os 6 Princípios Fundamentais

---

### 1. Seja Claro e Direto

A IA responde bem a instruções precisas e explícitas. Ser vago força o modelo a adivinhar — e ele pode adivinhar errado.

**O que fazer:**
- Especifique o formato de saída desejado
- Liste restrições e limitações
- Use etapas numeradas quando a ordem importa
- Diga explicitamente quando quiser resultados "acima do básico"

#### ❌ Prompt fraco

```
Configure OSPF no router.
```

#### ✅ Prompt forte

```
Você é um engenheiro de rede Cisco.
Configure OSPFv2 no router R1 com as seguintes especificações:
- Process ID: 1
- Area: 0 (backbone)
- Rede anunciada: 10.0.0.0/24
- Rede anunciada: 192.168.1.0/30

Retorne APENAS os comandos IOS em modo de configuração global.
Não inclua explicações, comentários ou output de show commands.
```

---

### 2. Adicione Contexto e Motivação

Explicar *por que* você precisa de algo ajuda o modelo a calibrar o nível de detalhe, o tom e as prioridades da resposta.

**O que incluir como contexto:**
- Quem vai usar a saída (alunos, engenheiros, clientes)
- Qual o propósito do resultado (lab, produção, troubleshooting)
- Restrições do ambiente (versão IOS, hardware virtual, CML2)
- O que deve ser evitado e por quê

#### Exemplo — Lab de Troubleshooting

```
Contexto: Estou criando um lab de troubleshooting para alunos de DevNet Associate.
Os alunos precisam identificar o problema sozinhos como parte do exercício.

Tarefa: Gere a configuração OSPFv2 para dois routers com exatamente UM fault
injetado (ex: area mismatch, passive interface incorreta, network statement errado).

Restrição: Não inclua comentários que revelem onde está o erro.
A configuração deve parecer intencional, não acidental.
```

---

### 3. Use Exemplos — Few-Shot Prompting

Exemplos são a forma mais confiável de guiar o **formato**, **tom** e **estrutura** da saída. Em vez de descrever o que você quer, mostre.

**Boas práticas para exemplos:**

| Critério | Descrição |
|----------|-----------|
| **Relevantes** | Próximos do seu caso de uso real |
| **Diversos** | Cobrir variações e casos-limite |
| **Estruturados** | Envolver em tags `<example>` |
| **Quantidade** | 3 a 5 exemplos para melhores resultados |

#### Exemplo — Gerador de Descrições de Interface

```xml
Gere descrições padronizadas para interfaces de roteadores Cisco.

<examples>
  <example>
    <input>GigabitEthernet0/0 | Link para SW-CORE | VLAN 10 | 192.168.10.1/24</input>
    <output>description UPLINK_TO_SW-CORE_VLAN10_192.168.10.1/24</output>
  </example>
  <example>
    <input>GigabitEthernet0/1 | Link WAN para ISP | IP público | 203.0.113.1/30</input>
    <output>description WAN_ISP_PRIMARY_203.0.113.1/30</output>
  </example>
  <example>
    <input>Loopback0 | Endereço de gerência OSPF | 10.255.255.1/32</input>
    <output>description MGMT_OSPF_ROUTER_ID_10.255.255.1/32</output>
  </example>
</examples>

Agora gere para:
GigabitEthernet0/2 | Link para R2 | backbone OSPF | 10.0.0.1/30
```

---

### 4. Estruture com Tags XML

Tags XML eliminam ambiguidade em prompts complexos que misturam instruções, contexto, exemplos e dados variáveis.

**Tags recomendadas:**

```xml
<role>       → Define o papel/persona da IA
<task>       → O que deve ser feito
<context>    → Informações de fundo
<constraints>→ Limites e restrições
<input>      → Os dados a processar
<output_format> → Como deve ser a saída
<examples>   → Exemplos de referência
```

#### Exemplo — Script Netmiko para Verificação OSPF

```xml
<role>
  Engenheiro de automação de redes especializado em Python e Netmiko.
</role>

<task>
  Gere um script Python usando Netmiko para conectar via SSH em um
  roteador IOS-XE e verificar o status dos vizinhos OSPF.
</task>

<context>
  Ambiente de laboratório CML2. Dispositivos acessíveis via IP de gerência.
  Python 3.10+, Netmiko 4.x instalado.
</context>

<constraints>
  - Apenas código Python, sem explicações
  - Tratar exceções de conexão (NetmikoTimeoutException, AuthenticationException)
  - Retornar saída como lista de dicionários com keys: neighbor_id, state, interface
</constraints>

<output_format>
  Arquivo Python completo, pronto para execução.
  Credenciais como variáveis no topo do script.
</output_format>
```

---

### 5. Atribua um Papel — Role Prompting

Definir um papel (persona) no início do prompt foca o comportamento, vocabulário e nível de detalhe da resposta. Até uma única frase faz diferença.

**Papéis úteis para DevNetOps:**

```
"Você é um instrutor Cisco DevNet Associate com 10 anos de experiência."

"Você é um engenheiro de rede que responde SOMENTE com comandos IOS válidos."

"Você é um gerador de topologias CML2 — retorne sempre JSON válido, sem texto adicional."

"Você é um especialista em pyATS/Genie que cria test cases para validação de redes."

"Você é um revisor técnico que avalia se configurações Cisco seguem as boas práticas."
```

#### Exemplo completo com Role + Task

```
Você é um instrutor sênior de Cisco CCNA que está criando material didático.

Explique o processo de formação de adjacência OSPFv2 entre dois roteadores
para alunos que já entenderam o modelo OSI mas ainda não estudaram protocolos
de roteamento dinâmico.

Use linguagem acessível, analogias do cotidiano e mantenha a explicação
em no máximo 200 palavras.
```

---

### 6. Encadeie Prompts para Tarefas Complexas

Para tarefas grandes e complexas, dividir em múltiplos prompts sequenciais produz resultados muito melhores do que um único prompt gigante. A saída de cada etapa alimenta a próxima.

#### Fluxo de Trabalho: Criação de Lab Completo no CML2

```
┌─────────────────────────────────────────────────────────┐
│  PROMPT 1 — Topologia                                    │
│  "Gere JSON CML2 para topologia em anel com 4 routers   │
│   IOS-XE e OSPFv2 convergido."                          │
└────────────────────┬────────────────────────────────────┘
                     │ output: topology.yaml
                     ▼
┌─────────────────────────────────────────────────────────┐
│  PROMPT 2 — Fault Injection                              │
│  "A partir desta topologia, crie uma variante com        │
│   exatamente 2 faults para troubleshooting."            │
└────────────────────┬────────────────────────────────────┘
                     │ output: topology_faulty.yaml
                     ▼
┌─────────────────────────────────────────────────────────┐
│  PROMPT 3 — Lab Guide                                    │
│  "Gere um guia de lab Markdown para alunos baseado       │
│   nesta topologia com os faults injetados."             │
└────────────────────┬────────────────────────────────────┘
                     │ output: lab-guide.md
                     ▼
┌─────────────────────────────────────────────────────────┐
│  PROMPT 4 — Script de Validação                          │
│  "Crie um script pyATS que verifica se os faults         │
│   foram corrigidos pelo aluno."                         │
└─────────────────────────────────────────────────────────┘
                     │ output: validate_lab.py
```

**Vantagens do encadeamento:**
- Cada etapa pode ser revisada antes de prosseguir
- Erros são isolados e fáceis de corrigir
- Permite reutilizar etapas em outros labs

---

## ✅ Princípio Bônus: Afirmativo vs. Negativo

A IA responde melhor a instruções que dizem **o que fazer** do que instruções que dizem **o que não fazer**.

| ❌ Evite | ✅ Prefira |
|---------|-----------|
| "Não use markdown" | "Responda em texto puro, sem formatação" |
| "Não seja verboso" | "Seja conciso. Máximo 3 frases por item." |
| "Não invente comandos" | "Use apenas comandos documentados no IOS 15.x+" |
| "Não explique o óbvio" | "Assuma que o leitor tem certificação CCNA" |

---

## 📊 Referência Rápida

| # | Princípio | Palavra-chave | Impacto |
|---|-----------|--------------|---------|
| 1 | Seja claro e direto | **Precisão** | ⭐⭐⭐⭐⭐ |
| 2 | Adicione contexto | **Motivação** | ⭐⭐⭐⭐ |
| 3 | Use exemplos | **Few-shot** | ⭐⭐⭐⭐⭐ |
| 4 | Tags XML | **Estrutura** | ⭐⭐⭐⭐ |
| 5 | Defina um papel | **Role** | ⭐⭐⭐ |
| 6 | Encadeie prompts | **Chaining** | ⭐⭐⭐⭐ |
| + | Afirmativo > Negativo | **Clareza** | ⭐⭐⭐ |

---

## 🧪 Exercícios Práticos

### Exercício 1 — Reescreva o Prompt
Melhore o prompt abaixo aplicando os princípios 1, 2 e 5:

```
# Prompt original (ruim)
"Explique VLANs"

# Seu prompt melhorado:
# (escreva aqui)
```

<details>
<summary>💡 Ver sugestão de resposta</summary>

```
Você é um instrutor Cisco DevNet Associate.

Explique o conceito de VLANs para alunos que já entendem
o modelo OSI e switches básicos, mas nunca configuraram
segmentação de rede.

Inclua:
1. Definição em uma frase
2. Analogia do mundo real
3. Exemplo de configuração IOS para criar VLAN 10 chamada "SERVERS"

Limite: 250 palavras.
```
</details>

---

### Exercício 2 — Adicione Exemplos
O prompt abaixo funciona, mas poderia ser muito melhor com few-shot. Adicione 3 exemplos usando tags XML:

```
Gere nomes padronizados para ACLs Cisco baseado na descrição fornecida.

# Adicione seus exemplos aqui:

Descrição: "Bloqueia tráfego Telnet vindo da rede de alunos para os roteadores"
```

---

### Exercício 3 — Monte um Prompt Completo
Crie um prompt que usa todos os 6 princípios para a seguinte tarefa:

> *"Gerar um script Python com Netmiko que faz backup das configurações de 5 roteadores Cisco e salva em arquivos `.txt` nomeados com o hostname e a data."*

---

## 📚 Recursos Oficiais

| Recurso | Link |
|---------|------|
| Anthropic Prompt Engineering Docs | [platform.claude.com/docs](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview) |
| Anthropic Prompting Best Practices | [Prompting Best Practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices) |
| Cisco DevNet Learning Labs | [developer.cisco.com/learninglabs](https://developer.cisco.com/learninglabs/) |
| CML2 Documentation | [developer.cisco.com/modeling-labs](https://developer.cisco.com/modeling-labs/) |

---

## 📝 Sobre Este Guia

Este guia foi elaborado para o **Workshop DevNetOps** destinado a professores de TI com foco em automação de redes Cisco.

Os princípios são baseados na documentação oficial de Prompt Engineering da Anthropic e adaptados para casos de uso de redes de computadores, automação com Python (Netmiko, NAPALM, pyATS) e laboratórios CML2.

---

*Última atualização: Junho 2026*