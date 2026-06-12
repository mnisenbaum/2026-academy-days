# Lab 05 - Automatizando as chamadas RESTCONF

Bem-vindos ao **Lab 05**. No laboratório anterior, você interagiu manualmente com as APIs do roteador utilizando a interface gráfica do Bruno. Agora, daremos o próximo passo na jornada de automação: **transformar requisições manuais em scripts programáticos executáveis (Bash e Python)**.

A Inteligência Artificial desempenha um papel crucial aqui. Em vez de reescrever do zero toda a lógica de manipulação de requisições HTTP, autenticação e cabeçalhos, forneceremos o arquivo de configuração da nossa coleção JSON do Bruno diretamente para a IA e solicitaremos que ela faça o trabalho de portabilidade e geração de código.

---

## 🎯 Objetivos
* Exportar e injetar coleções de API (JSON) em assistentes de IA para engenharia reversa de código.
* Criar um script Bash interativo com controle de fluxo (menus) e tratamento de dados via `curl`.
* Desenvolver um script Python estruturado em um ambiente virtual (`venv`) utilizando a biblioteca `requests`.
* Compreender e analisar criticamente as linhas de código geradas através de comentários detalhados.

---

## 🛠️ Parte 1: Preparando a IA com a Coleção do Bruno

Para que a IA crie scripts precisos, precisamos alimentá-la com a estrutura correta das chamadas que funcionaram no laboratório anterior.

- [ ] Localize o arquivo de configuração baixado no Lab 04 (`NetAcad _ RESTCONF-Bruno.json`) ou exporte a coleção diretamente do Bruno.
- [ ] Abra o arquivo `.json` em um editor de texto (como o VS Code ou Bloco de Notas) e copie todo o seu conteúdo estruturado.
- [ ] Abra o seu assistente de IA (Gemini, ChatGPT ou Claude) e utilize a estratégia de prompt abaixo para iniciar a geração.

### Prompt de Engenharia para a IA:
> "Atue como um Engenheiro de Automação de Redes. Abaixo está o conteúdo JSON de uma coleção de chamadas RESTCONF feitas no aplicativo Bruno. Com base nessas requisições, preciso que você crie dois scripts interativos e totalmente comentados linha por linha para fins de aprendizado técnico. 
> 
> O primeiro deve ser um script Bash usando cURL. 
> O segundo deve ser um script Python usando a biblioteca requests dentro de um venv.
> 
> Ambos os scripts devem:
> 1. Solicitar ao usuário o endereço IP/Hostname do Catalyst, o usuário e a senha.
> 2. Exibir um menu interativo para que o usuário escolha qual ação executar: [1] Listar Interfaces, [2] Alterar Descrição da Interface GigabitEthernet1, [3] Sair.
> 
> [COLE O CONTEÚDO DO ARQUIVO JSON DO BRUNO AQUI]"

---

## 🐚 Parte 2: Scripting em Bash (Automação com cURL)

O Bash é excelente para automações rápidas diretamente no terminal Linux. A IA traduzirá a requisição HTTP do Bruno em comandos `curl` estruturados.

- [ ] Crie um arquivo chamado `automacao_restconf.sh` no seu ambiente Linux/WSL.
- [ ] Analise o código gerado pela IA (exemplo estruturado abaixo) e cole-o no seu arquivo.
- [ ] Garanta que o arquivo tem permissão de execução com o comando `chmod +x automacao_restconf.sh`.
- [ ] Execute o script usando `./automacao_restconf.sh` e teste a interação com o Sandbox.

### Código Bash Gerado e Comentado pela IA:

```bash
#!/bin/bash

# ==============================================================================
# SCRIPT DE AUTOMAÇÃO RESTCONF - ACADEMY DAYS 2026 (BASH + CURL)
# ==============================================================================

# Solicita as credenciais e dados do roteador dinamicamente ao usuário
echo "=== Configuração de Acesso ao Catalyst ==="
read -p "Digite o IP ou Hostname do dispositivo: " HOST
read -p "Digite o usuário: " USER
read -s -p "Digite a senha: " PASSWORD
echo -e "\n"

# Define a URL base combinando os inputs do usuário conforme o padrão do modelo YANG
BASE_URL="https://${HOST}/restconf/data"

# Loop contínuo para manter o menu interativo ativo até que o usuário decida sair
while true; do
    echo "=========================================="
    echo "     MENU DE AUTOMAÇÃO RESTCONF - BASH    "
    echo "=========================================="
    echo "1. Listar Interfaces (GET)"
    echo "2. Configurar Descrição na Gi1 (PATCH)"
    echo "3. Sair"
    read -p "Escolha uma opção [1-3]: " OPCAO

    case $OPCAO in
        1)
            echo -e "\n[+] Executando GET: Solicitando lista de interfaces..."
            # -k: Ignora certificados SSL autoassinados (Bypass)
            # -u: Aplica autenticação do tipo Basic Auth com as variáveis de input
            # -H: Define os Headers obrigatórios exigidos pelo padrão RESTCONF
            curl -k -u "${USER}:${PASSWORD}" -X GET "${BASE_URL}/ietf-interfaces:interfaces" \
                 -H "Accept: application/yang-data+json"
            echo -e "\n"
            ;;
        2)
            echo -e "\n"
            read -p "Digite a nova descrição para a interface Gi1: " DESC
            
            # Monta o payload JSON estruturado conforme o modelo YANG ietf-interfaces
            PAYLOAD="{\"ietf-interfaces:interface\": {\"name\": \"GigabitEthernet1\", \"description\": \"${DESC}\", \"type\": \"iana-if-type:ethernetCsmacd\"}}"
            
            echo "[+] Executando PATCH: Atualizando a descrição da interface..."
            # -d: Passa o payload JSON gerado
            # Content-Type: Informa ao IOS-XE que estamos enviando dados estruturados em JSON
            curl -k -u "${USER}:${PASSWORD}" -X PATCH "${BASE_URL}/ietf-interfaces:interfaces/interface=GigabitEthernet1" \
                 -H "Content-Type: application/yang-data+json" \
                 -H "Accept: application/yang-data+json" \
                 -d "$PAYLOAD" \
                 -v # Ativa o modo verboso para conseguirmos ver o status HTTP 204 de sucesso
            echo -e "\n"
            ;;
        3)
            echo "Encerrando o script. Até logo!"
            exit 0
            ;;
        *)
            echo -e "\n[!] Opção inválida. Tente novamente.\n"
            ;;
    esac
done
```

---

## 🐍 Parte 3: Scripting em Python (Ambiente Isolado e `requests`)

O Python é a linguagem padrão da indústria para programabilidade. Para não poluir o sistema operacional, utilizaremos um ambiente virtual (`venv`).

- [ ] Crie uma pasta para o projeto e acesse-a: `mkdir lab05_python && cd lab05_python`
- [ ] Crie o ambiente virtual: `python3 -m venv venv`
- [ ] Ative o ambiente virtual:
  * No Linux/macOS: `source venv/bin/activate`
  * No Windows (Prompt): `venv\Scripts\activate`
- [ ] Instale a biblioteca de manipulação HTTP recomendada pela IA: `pip install requests`
- [ ] Crie o arquivo `automacao_restconf.py` e insira o código gerado abaixo.
- [ ] Execute com `python automacao_restconf.py`.

### Código Python Gerado e Comentado pela IA:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SCRIPT DE AUTOMAÇÃO RESTCONF - ACADEMY DAYS 2026 (PYTHON + REQUESTS)
"""

import json
import requests
import urllib3
import getpass

# Desabilita os avisos visuais no terminal sobre conexões HTTPS sem certificados válidos (SSL autoassinado)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def obter_credenciais():
    print("=== Configuração de Acesso ao Catalyst ===")
    host = input("Digite o IP ou Hostname do dispositivo: ")
    usuario = input("Digite o usuário: ")
    # O getpass oculta a senha enquanto o usuário digita por motivos de segurança
    senha = getpass.getpass("Digite a senha: ")
    return host, usuario, senha

def listar_interfaces(base_url, auth, headers):
    print("\n[+] Executando GET: Solicitando lista de interfaces...")
    url = f"{base_url}/ietf-interfaces:interfaces"
    try:
        # requests.get: Realiza a chamada de leitura
        # verify=False: Realiza o bypass da checagem do certificado SSL
        response = requests.get(url, auth=auth, headers=headers, verify=False)
        
        if response.status_code == 200:
            # Transforma a resposta de texto cru para um dicionário formatado em JSON legível
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"[!] Erro ao buscar dados. Status Code: {response.status_code}")
    except Exception as e:
        print(f"[!] Erro de conexão: {e}")

def alterar_descricao(base_url, auth, headers):
    print("\n")
    nova_desc = input("Digite a nova descrição para a interface Gi1: ")
    url = f"{base_url}/ietf-interfaces:interfaces/interface=GigabitEthernet1"
    
    # Dicionário nativo do Python que mapeia exatamente a árvore do modelo YANG do Bruno
    payload = {
        "ietf-interfaces:interface": {
            "name": "GigabitEthernet1",
            "description": nova_desc,
            "type": "iana-if-type:ethernetCsmacd"
        }
    }
    
    print("[+] Executando PATCH: Atualizando dados no roteador...")
    try:
        # requests.patch: Atualização parcial de dados
        # json=payload: Converte automaticamente o dicionário Python para string JSON estruturada
        response = requests.patch(url, auth=auth, headers=headers, json=payload, verify=False)
        
        # O RESTCONF retorna 204 (No Content) quando a alteração ocorre com sucesso e não há dados para retornar
        if response.status_code in [200, 204]:
            print("[✔️] Descrição alterada com sucesso via API!")
        else:
            print(f"[!] Falha na alteração. Status Code: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"[!] Erro de conexão: {e}")

def main():
    host, usuario, senha = obter_credenciais()
    base_url = f"https://{host}/restconf/data"
    
    # Tupla utilizada pelo módulo 'requests' para injetar o cabeçalho HTTP Authorization: Basic
    auth = (usuario, senha)
    
    # Cabeçalhos mapeados a partir da estrutura importada do Bruno
    headers = {
        "Accept": "application/yang-data+json",
        "Content-Type": "application/yang-data+json"
    }

    while True:
        print("\n" + "="*42)
        print("    MENU DE AUTOMAÇÃO RESTCONF - PYTHON   ")
        print("="*42)
        print("1. Listar Interfaces (GET)")
        print("2. Configurar Descrição na Gi1 (PATCH)")
        print("3. Sair")
        opcao = input("Escolha uma opção [1-3]: ")

        if opcao == "1":
            listar_interfaces(base_url, auth, headers)
        elif opcao == "2":
            alterar_descricao(base_url, auth, headers)
        elif opcao == "3":
            print("Encerrando o script Python. Até logo!")
            break
        else:
            print("\n[!] Opção inválida. Tente novamente.")

if __name__ == "__main__":
    main()
```

---

## 🧠 Parte 4: Aprendizado e Comparação (Análise Crítica)

Agora que você utilizou três abordagens diferentes para interagir com o RESTCONF (Interface Gráfica do Bruno, Shell Script com Bash e Programação Estruturada com Python), preencha mentalmente ou discuta com seu grupo a tabela comparativa abaixo.

### Matriz de Comparação de Ferramentas de Automação

| Critério de Análise | Bruno (GUI) | Bash (cURL) | Python (requests) |
| :--- | :--- | :--- | :--- |
| **Velocidade de Teste Inicial** | 🟢 Muito Alta (Visual) | 🟡 Média | 🟡 Média |
| **Manipulação de Dados Complexos**| 🔴 Baixa / Manual | 🔴 Muito Complexa (Tratamento de Strings)| 🟢 Muito Alta (Dicionários/JSON nativo) |
| **Facilidade de Escalonamento** | 🔴 Baixa (Individual) | 🟡 Média (Scripts sequenciais) | 🟢 Excelente (Modularização/Funções) |
| **Flexibilidade de Interface** | 🟡 Fixa na Ferramenta | 🟢 Criação de Menus CLI rápidos | 🟢 Totalmente customizável (CLI ou Web) |

### Principais Lições Aprendidas:
1. **O Cabeçalho é a Chave:** Independentemente da ferramenta (Bruno, Bash ou Python), os cabeçalhos `Accept` e `Content-Type` com o valor `application/yang-data+json` são obrigatórios para que o IOS-XE processe os dados como JSON e não como XML.
2. **Abstração da IA:** A IA nos poupou de estruturar loops complexos em Bash ou mapear manualmente as exceções do módulo `requests` em Python. Ela serve como tradutora de protocolos.
3. **Casamento de Tipos:** Em Python, o uso do método `json=payload` remove a necessidade de escaparmos aspas (como fizemos no Bash `\"`), tornando o script mais seguro e resiliente a falhas de sintaxe.

---
*Fim do Lab 05. Você moveu as engrenagens da automação manual para o código. No próximo laboratório, utilizaremos o SDK oficial do CML2 para criar ambientes programáticos inteiros de forma dinâmica.*