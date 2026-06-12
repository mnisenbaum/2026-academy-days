# Lab 03 - Configurar o Lab 01 usando Netmiko

Este roteiro faz parte do workshop **Redes no Mundo da IA (Academy Days 2026)**. Nesta prática, utilizaremos a IA Generativa de forma iterativa para auxiliar na automação de tarefas de rede com **Python** e a biblioteca **Netmiko**, focando no conceito de Infraestrutura como Código (IaC).

---

## 🎯 Objetivos de Aprendizado
* Utilizar IA generativa para entender o papel de ferramentas de automação tradicionais (*SSH-based*).
* Configurar um ambiente virtual isolado Python (`venv`) para automação de redes.
* Empregar técnicas de *Prompt Engineering* para gerar scripts funcionais e documentados.
* **Aprendizado Invertido**: Executar códigos gerados por IA, analisar a sua lógica e aplicar modificações manuais personalizadas para consolidação do conhecimento.

---

## 💻 Pré-requisitos
* Topologia do **Lab 01** criada e validada no Cisco Modeling Labs (CML2).
* Conectividade IP entre a sua máquina local (ou VM de gerência) e o roteador de borda (R1).
* Python 3 e editor de código (VS Code, Cursor ou opencode) instalados.

---

## 📝 Checklist da Prática

### 1. Clonagem e Preparação da Topologia no CML2
- [ ] **Exportar o Lab 01:** Acesse o painel do CML2, vá até a topologia do Lab 01, clique em *Download/Export* e salve o arquivo `.json` na sua máquina.
- [ ] **Importar como Clone:** No painel inicial do CML2, clique em *Import* e selecione o arquivo `.json` salvo. Altere o nome para `Lab 03 - Netmiko`.
- [ ] **Conectar à Rede Externa:** Adicione um nó do tipo **External Cloud** (configurado em modo *Bridge*) à área de trabalho do CML2.
- [ ] **Conectar o R1 à Nuvem:** Crie um link físico entre a interface dedicada do roteador **R1** e a nuvem externa.
- [ ] **Configurar Acesso SSH Global:** Inicialize todos os roteadores e garanta que os parâmetros de SSH estejam configurados (chaves RSA geradas, credenciais locais e `transport input ssh` aplicado nas linhas VTY).
- [ ] **Validar Conectividade:** A partir do terminal da sua máquina, certifique-se de que consegue pingar e abrir uma sessão SSH diretamente para o IP atribuído à interface do **R1**.

### 2. Entendendo o Ecossistema com IA
- [ ] **Interagir com a IA:** Abra o seu chat de IA de preferência e envie a seguinte pergunta:
  > *"O que faz a biblioteca Netmiko no ecossistema de automação de redes Python, quais são seus principais casos de uso e por que ela é importante para ambientes legados?"*
- [ ] **Leitura Ativa:** Analise a resposta da IA para entender como a biblioteca abstrai a complexidade das interações baseadas em CLI.

### 3. Preparação do Ambiente de Programação (Ambiente Virtual)
- [ ] **Criar Diretório do Projeto:** Abra o terminal da sua máquina e crie uma pasta exclusiva para este laboratório.
- [ ] **Criar o Virtual Environment (venv):** Isole as bibliotecas Python:
  
```bash
  # Linux/macOS ou Windows (Git Bash/WSL)
  python3 -m venv venv
  ```
- [ ] **Ativar o Ambiente Virtual:**

```bash
  # Linux/macOS
  source venv/bin/activate

  # Windows (PowerShell)
  .\venv\Scripts\Activate.ps1
  ```
- [ ] **Instalar Dependências:** Com o ambiente ativo, instale a biblioteca Netmiko:

```bash
  pip install netmiko
  ```

### 4. Geração do Script via IA Generativa
- [ ] **Construir o Prompt Contextualizado:** No **mesmo chat** utilizado para gerar as configurações do Lab 01, envie:
> *"Atue como um Engenheiro de Automação de Redes. Escreva um script Python usando a biblioteca Netmiko para se conectar via SSH ao roteador R1. A partir de R1, o script deve interagir com as interfaces de todos os routers da topologia. O objetivo é adicionar descrições padronizadas às interfaces de todos os routers. Insira comentários explicativos detalhados linha por linha no código para que eu possa entender o papel do ConnectHandler, send_config_set e o gerenciamento de erros."*
- [ ] **Criar o Arquivo de Código:** Copie o script gerado. Na sua IDE, crie um arquivo chamado `config_netmiko.py` e cole o código.

### 5. Execução e Aprendizado Invertido (Modificação Manual)
- [ ] **Executar o Script:** No terminal com o `venv` ativo, execute:
```bash
  python config_netmiko.py
  ```
- [ ] **Verificar Resultados no CML2:** Acesse a console dos roteadores no CML2 e execute `show interfaces description`.
- [ ] **Aplicar Modificação Humana:** Abra o arquivo `config_netmiko.py`. Modifique manualmente o script alterando a string da descrição de uma interface específica (Ex: `'Interface Modificada Manualmente por [Seu Nome]'`).
- [ ] **Reexecutar e Validar:** Rode o script novamente e valide se a nova descrição foi injetada com sucesso.

---

## 💡 Estrutura Base Esperada do Código (Netmiko)

Caso precise de referência, o bloco principal da conexão em Netmiko deve ter este formato:

```python
from netmiko import ConnectHandler

roteador_r1 = {
    'device_type': 'cisco_xe',
    'host': '192.168.1.51', # IP da Bridge
    'username': 'admin',
    'password': 'cisco_password',
}

try:
    with ConnectHandler(**roteador_r1) as ssh_conn:
        ssh_conn.enable()
        
        comandos = [
            'interface GigabitEthernet1',
            'description Configurado via Netmiko e IA'
        ]
        
        output = ssh_conn.send_config_set(comandos)
        print(output)
except Exception as erro:
    print(f"Ocorreu um erro inesperado: {erro}")
```