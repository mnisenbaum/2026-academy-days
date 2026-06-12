# Guia Prático: Instalação do Cisco Modeling Labs (CML) 2.10 no Hyper-V

> **Elaborado para o Workshop Academy Days 2026 — Unindo Redes, Automação e Inteligência Artificial para preparar os profissionais do amanhã.**

---

## 1. Introdução

Bem-vindo ao guia oficial de preparação de infraestrutura para o nosso **Workshop de IA e Automação no Academy Days 2026**!

O Cisco Modeling Labs (CML) é a plataforma oficial de simulação de redes da Cisco. Executá-lo diretamente sobre o Hyper-V do Windows 10/11 ou Windows Server como uma instalação **Bare Metal** (via ISO) é uma excelente alternativa para criar seu próprio laboratório local.

Este guia foi desenhado para garantir que sua instalação ocorra sem sobressaltos, focando nos ajustes de configuração do Hyper-V que são vitais para o funcionamento dos nós de simulação (como roteadores IOS, switches L2/L3 e firewalls).

---

## 2. Requisitos de Hardware e Software

Antes de iniciar, certifique-se de que seu computador atende aos requisitos mínimos:

| Recurso | Requisito Mínimo | Requisito Recomendado | Notas Importantes |
|---|---|---|---|
| Processador | 4 vCPUs | 8 vCPUs ou mais | Deve suportar virtualização (Intel VT-x ou AMD-V) |
| Memória RAM | 8 GB | 16 GB ou mais | **Não utilizar** Memória Dinâmica no Hyper-V |
| Armazenamento | 100 GB SSD | 150 GB+ SSD (NVMe) | Espaço para imagens de referência (Refplat ISO) |
| Rede | Default Switch | External Switch (Bridge) | Conectividade externa para integração com IA/APIs |

### Arquivos Necessários (Downloads)

1. **ISO do CML 2.10** — O instalador do sistema operacional base do CML (ex: `cml2_2.10.x_amd64.iso`)
2. **ISO Refplat (Reference Platforms)** — Arquivo contendo as imagens dos dispositivos Cisco (ex: `refplat-202X-XX-XX-fcs.iso`)

---

## 3. Passo 1: Criando a Máquina Virtual no Hyper-V

Siga rigorosamente as etapas abaixo no **Gerenciador do Hyper-V**:

1. Abra o **Gerenciador do Hyper-V** no seu Windows.
2. No painel de ações (à direita), clique em **Novo → Máquina Virtual**.
3. Configure os campos conforme abaixo:

   - **Nome:** Defina um nome claro (ex: `CML2-BareMetal`)
   - **Especificar Geração:** Selecione **Geração 2** _(obrigatório para melhor suporte a UEFI e arquiteturas modernas)_
   - **Atribuir Memória:** Insira `8192 MB` (8 GB) ou mais

   > ⚠️ **CRÍTICO:** Desmarque a caixa **"Usar Memória Dinâmica para esta máquina virtual"**. O CML exige alocação estática para gerenciar a RAM dos roteadores simulados.

   - **Configurar Rede:** Selecione **Default Switch** (ou uma rede externa de sua preferência para que o laboratório tenha acesso à internet para as práticas de IA)
   - **Conectar Disco Rígido Virtual:** Crie um disco rígido virtual com **100 GB** ou mais
   - **Opções de Instalação:** Selecione _"Instalar um sistema operacional de um arquivo de imagem inicializável"_ e aponte para a ISO do CML 2.10 baixada

4. Clique em **Concluir**, mas **NÃO ligue a VM ainda**.

---

## 4. Passo 2: Ajustes Críticos de Hardware (Antes de Ligar)

Para que o CML Geração 2 funcione corretamente no Hyper-V, são necessárias **duas modificações cruciais** nas configurações de hardware:

### A. Desativar a Inicialização Segura (Secure Boot)

O kernel do CML (baseado em Linux) não irá bootar com a Inicialização Segura padrão do Windows ativada.

1. No Gerenciador do Hyper-V, clique com o botão direito na VM criada e selecione **Configurações**.
2. Na aba **Segurança** (painel esquerdo), desmarque a opção **"Habilitar Inicialização Segura"**.

### B. Adicionar a Segunda Unidade de DVD (ISO Refplat)

O CML precisa de acesso simultâneo ao instalador e às imagens de roteadores/switches durante e após o boot.

1. Ainda nas **Configurações da VM**, selecione **Controladora SCSI** no menu à esquerda.
2. Selecione **Unidade de DVD** e clique em **Adicionar**.
3. Na nova unidade criada, mude a opção para **Arquivo de imagem** e aponte para a ISO da Refplat (`refplat-202X-...iso`).
4. Clique em **Aplicar** e **OK**.

---

## 5. Passo 3: Habilitando a Virtualização Aninhada (Nested Virtualization)

O CML executa emuladores (QEMU) dentro do Linux para rodar os sistemas operacionais de rede Cisco. Por padrão, o Hyper-V **não expõe** as extensões de virtualização do processador físico para dentro da VM. Se não ativarmos isso, os roteadores do seu laboratório ficarão travados ou não ligarão.

> ⚠️ **Esta configuração deve ser feita com a VM desligada**, através do PowerShell em modo Administrador.

1. Abra o **PowerShell como Administrador**.
2. Execute o comando abaixo substituindo `"NomeDaSuaVM"` pelo nome exato que você deu à sua máquina virtual:

```powershell
# Ativa as extensões de virtualização física na vCPU da máquina virtual
Set-VMProcessor -VMName "CML2-BareMetal" -ExposeVirtualizationExtensions $true
```

3. Verifique se o comando foi aplicado com sucesso:

```powershell
Get-VMProcessor -VMName "CML2-BareMetal" | Select-Object VMName, ExposeVirtualizationExtensions
```

> ✅ O resultado esperado no campo `ExposeVirtualizationExtensions` deve ser **`True`**.

---

## 6. Passo 4: Instalação e Configuração do Sistema

Agora estamos prontos para ligar a máquina e proceder com o assistente de instalação do CML.

1. No Gerenciador do Hyper-V, clique duas vezes na VM para abrir a console de exibição e clique em **Iniciar**.
2. O instalador do CML será iniciado. Pressione **Enter** na tela de boot padrão.
3. Siga o assistente de instalação interativo preenchendo as seguintes informações:

   - **Language / Keyboard:** Mantenha o padrão ou ajuste para sua preferência.
   - **System Accounts:**
     - Defina o usuário administrativo do sistema Linux (o padrão sugerido é `sysadmin`) e uma senha forte.
     - Defina o usuário de acesso à interface Web (o padrão sugerido é `admin`) e uma senha forte.
   - **Network Configuration:** Se estiver usando o Default Switch, o CML obterá um IP automaticamente via DHCP. Recomenda-se manter o DHCP para facilitar a conexão inicial.
   - **CML Setup & Serviços Opcionais:** O instalador irá detectar as duas unidades de CD/DVD configuradas no Passo 2. Ele validará a presença da ISO de instalação e montará a Refplat ISO automaticamente.

   > ⚠️ **MUITO IMPORTANTE:** Durante o assistente de configuração, o instalador solicitará que você escolha quais serviços opcionais deseja ativar por padrão. Você deve marcar as **três caixas de seleção obrigatórias**:

   ```
   [*] OpenSSH     — Serviço SSH na porta 1122 (para conexões administrativas seguras).
   [*] PATty       — Redirecionamento de portas de nós do laboratório (para facilitar
                     acesso externo às portas de console).
   [*] MCPServer   — Servidor MCP (Model Context Protocol) para LLMs. Este serviço é
                     indispensável para as práticas de inteligência artificial do workshop.
   ```

4. Confirme as opções e selecione **"Install"**. O processo de cópia de arquivos e configuração do sistema levará alguns minutos.

---

## 7. Acesso e Validação

Uma vez concluída a instalação, a console da máquina virtual apresentará uma tela de gerenciamento do CML contendo a URL de acesso.

```
============================================================
Cisco Modeling Labs (CML)
============================================================
Web URL: https://192.168.x.x/
============================================================
```

1. Abra o **navegador** do seu computador hospedeiro (Windows).
2. Acesse o endereço IP fornecido (ex: `https://192.168.x.x/`).

   > 📝 Ignore o aviso de certificado SSL autoassinado do navegador.

3. Entre com as credenciais do usuário web (`admin` e a senha definida no assistente).
4. **Pronto!** O seu servidor CML está pronto para simular topologias de rede avançadas integradas com scripts Python, Netmiko e inteligência artificial generativa.

---

## 8. Solução de Problemas (Troubleshooting)

### ❌ Os nós da topologia (ex: IOSv) dão boot mas ficam travados em loop ou dão erro de CPU

- **Causa:** Virtualização aninhada não habilitada.
- **Resolução:** Desligue a VM e execute o comando PowerShell do [Passo 3](#5-passo-3-habilitando-a-virtualização-aninhada-nested-virtualization).

---

### ❌ A VM do CML não passa da tela do logotipo ou apresenta erro UEFI/Boot

- **Causa:** Inicialização Segura (Secure Boot) está habilitada.
- **Resolução:** Desligue a VM, abra as configurações no Hyper-V, vá em **Segurança** e desmarque **"Habilitar Inicialização Segura"**.

---

### ❌ Falta de nós ou erro indicando que as imagens das plataformas de referência não foram encontradas

- **Causa:** A segunda ISO (`refplat`) não foi adicionada à controladora SCSI ou o arquivo não está acessível.
- **Resolução:** Verifique o [Passo 2](#4-passo-2-ajustes-críticos-de-hardware-antes-de-ligar) e confirme que a controladora possui **duas unidades de DVD** físicas mapeadas de forma independente no Hyper-V.

---

*Elaborado para o Workshop Academy Days 2026 — Unindo Redes, Automação e Inteligência Artificial para preparar os profissionais do amanhã.*
