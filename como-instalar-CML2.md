# **Roteiro de Instalação \- Cisco Modeling Labs v2.10 (CML-Free)**

Este guia prático descreve os requisitos, o download e os passos necessários para a instalação e configuração do **Cisco Modeling Labs v2.10 (CML-Free)**, a versão gratuita de uso individual, em diferentes ambientes.

## **0\. Requisitos Mínimos para Rodar o CML2 (v2.10)**

O consumo de recursos do CML2 depende do tamanho e do tipo das topologias que você pretende simular. Com o sistema ocioso (sem laboratórios ativos), o servidor CML-Free consome cerca de 1 GB de RAM e quase nada de CPU.

### **Requisitos Mínimos Recomendados:**

* **Memória (RAM):** Mínimo de **8 GB** (reservados/dedicados para a VM).  
* **Processador (CPU):** **4 ou mais núcleos físicos** com suporte obrigatório a tecnologias de virtualização aninhada (**Intel VT-x/EPT** ou **AMD-V/RVI**).  
  * *Nota sobre processadores:* Processadores Intel possuem suporte oficial e total. Processadores AMD funcionam, mas o suporte a algumas imagens de referência é oferecido de forma "best effort" (melhor esforço). **Processadores Apple Silicon (chips M1, M2, M3, M4) não são suportados.**  
* **Armazenamento:** Mínimo de **32 GB** de espaço em disco (padrão de instalação).  
  * *Recomendação de produção:* Pelo menos **100 GB** ou mais (preferencialmente em SSD ou RAID de alta velocidade). Copiar todas as imagens de nodes do arquivo *refplat* para o disco local consome muito espaço, e discos lentos podem causar falhas ao iniciar nodes pesados (como o NX-OS 9000).  
* **Rede:** Mínimo de 1 Interface de Rede (NIC).  
* **Navegador Web:** Google Chrome ou Mozilla Firefox atualizados (compatíveis com HTML5).

## **Limitations e Características do CML-Free**

O CML-Free possui as mesmas funcionalidades da versão *CML-Personal*, operando de forma idêntica com apenas algumas particularidades:

* **Limite de Nós (Nodes):** O CML-Free permite rodar simultaneamente um **máximo de 5 nós ativos**.  
  * *Exceções ao limite:* Nós de **Unmanaged Switch** (Switch Não Gerenciado) e **External Connector** (Conector de Rede Externa) **não contam** para este limite. Você pode rodar 5 nós roteadores/firewalls mais quantos switches não gerenciados e conectores externos desejar.  
* **Licenciamento Simplificado:** **Não** é necessária uma licença ou conta de *Smart Licensing* da Cisco. Durante a instalação, você pode pular a etapa de licenciamento.  
  * O status no painel indicará OK (FREE-TIER). O sistema pode mostrar que está em "Modo de Avaliação" (*Evaluation Mode* ou *Evaluation Expired*), mas você pode ignorar esse aviso e a contagem regressiva; a sua instância gratuita não expirará.  
* **Coleta de Telemetria:** A coleta de dados estatísticos de uso anônimo (telemetria) é obrigatória e está sempre ativa no CML-Free para ajudar a Cisco a melhorar o software.  
* **Imagens de Referência Incluídas:** A ISO do *refplat* da versão Free é otimizada para iniciantes e inclui as imagens do **IOL**, **IOL-L2**, **ASAv**, além de hosts Linux como **Ubuntu**, **Alpine** e uma imagem com **Desktop gráfico**.

## **1\. Como Baixar o CML-Free v2.10**

Para baixar o CML-Free, você precisará de uma conta no portal da Cisco e fazer o download diretamente pelo **Cisco's Software Central (SWC)**.

### **Passo 1: Cadastro no Cisco.com (CCO ID)**

Se você ainda não possui uma conta, crie uma em [Cisco ID](https://id.cisco.com/).

**⚠️ Importante devido a Controle de Exportações dos EUA:**

* Preencha todos os campos do seu perfil CCO. Não deixe campos em branco.  
* No campo de Empresa (*Company*), caso não trabalhe em uma, preencha como **"Self"** e insira seu endereço residencial completo (incluindo o CEP/Post Code correto).  
* Utilize um e-mail com domínio reconhecível (comerciais ou populares como gmail.com e yahoo.com).

### **Passo 2: Acessar o Portal de Downloads**

1. Certifique-se de ter se registrado previamente na página de registro do CML-Free.  
2. Acesse o site do [Cisco's Software Central (SWC)](https://software.cisco.com/download/home).  
3. Faça login com seu CCO ID.  
4. No campo de busca do SWC, procure por **"Modeling Labs"**.  
5. Navegue até a última versão disponível (**v2.10**).

### **Passo 3: Baixar os Arquivos do CML-Free v2.10**

Baixe apenas os arquivos correspondentes ao seu método de instalação:

1. **Para Instalação como VM:** Baixe o arquivo do Controlador em formato **.ova** (CML Controller OVA).  
2. **Para Instalação Bare Metal / Outros Hipervisores:** Baixe o arquivo do Controlador em formato **.iso** (CML Controller ISO).  
3. **Reference Platform (refplat) ISO:** Baixe o arquivo .iso de imagens de referência correspondente ao CML-Free para que você possa inicializar seus nós de rede.

## **2\. Instalação Importando a Imagem OVA (VMware)**

Esta é a opção recomendada pela facilidade de gerenciamento de recursos, backup por snapshots e portabilidade.

**⚠️ Atenção:** Não ligue a máquina virtual imediatamente após a importação. Você deve ajustar as configurações abaixo antes do primeiro boot.

### **A. VMware Workstation (Windows) / Fusion (macOS Intel)**

1. Abra o arquivo .ova baixado clicando duas vezes ou selecionando *Abrir com* o VMware Workstation/Fusion.  
2. Siga o assistente de importação e clique em **Customize** ou **Finish**.  
3. Acesse as **Configurações da VM** (Settings) e ajuste:  
   * **Processadores:** Aloque pelo menos 4 cores. **Obrigatório:** Ative a opção **"Virtualize Intel VT-x/EPT"** (Windows) ou **"Enable hypervisor applications"** (macOS).  
   * **Memória:** Defina 8 GB ou mais.  
   * **Disco Rígido (Hard Disk):** Expanda o tamanho padrão de 32 GB para 100 GB ou mais. O CML2 redimensionará o sistema de arquivos automaticamente no primeiro boot.  
   * **CD/DVD:** Mapeie o drive de CD/DVD para apontar para o arquivo refplat\_image.iso (ISO do refplat gratuito) e marque a opção **"Connect at power on"** (Conectar ao iniciar).  
   * **Placa de Rede:** Escolha **NAT** (recomendado para receber IP automático do VMware) ou **Bridge** (para que a VM faça parte da sua rede física local).  
4. Inicie a VM para rodar o assistente de configuração inicial no console. Durante o assistente, pule a etapa de licenciamento.

### **B. VMware ESXi (Versão 7.0 ou posterior)**

1. **Upload do Refplat:** Faça o upload do arquivo refplat\_image.iso para um datastore acessível pelo host ESXi.  
2. **Implantação do OVA:** No cliente web do ESXi, selecione *Deploy a virtual machine from an OVF or OVA file* e importe o arquivo OVA do controlador CML2.  
3. **Configuração da VM (Não ligue a VM ainda):**  
   * **Hardware Virtual:** Atualize a compatibilidade do hardware da VM para a versão mais recente suportada pelo seu host ESXi.  
   * **CPU:** Aloque os vCPUs necessários. Em *Hardware Virtualization*, marque a caixa **"Expose hardware assisted virtualization to the guest OS"** e habilite os contadores de desempenho de CPU virtualizados (*Virtual CPU Performance Counters*).  
   * **Memória:** Defina a RAM desejada e **ative a reserva total de memória** (*Reserve all guest memory*). Isso impede que o ESXi faça swap em disco e evita travamentos nos nós simulados.  
   * **Disco Rígido:** Aumente o tamanho do disco (mínimo de 100 GB recomendado para evitar falta de espaço posterior).  
   * **CD/DVD Drive:** Altere o local para *Datastore ISO File*, selecione o arquivo refplat\_image.iso carregado no passo 1 e marque **"Connect at power on"**. Use o nó de dispositivo IDE virtual mais baixo (ex: IDE 0:0).  
   * **Configurações Avançadas da VM:** Em *VM Options \-\> Advanced*, mude a sensibilidade de latência (*Latency Sensitivity*) para **High**.  
   * **Segurança do vSwitch/Port Group:** Para utilizar conexões externas em modo bridge no CML2, altere as seguintes propriedades no Port Group utilizado pela VM CML:  
     * *Promiscuous Mode* \= **Accept**  
     * *Forged Transmits* \= **Accept**  
   * No próprio Host ESXi (configurações avançadas do sistema), configure:  
     * Net.ReversePathFwdCheck \= 1  
     * Net.ReversePathFwdCheckPromisc \= 1  
4. Ligue a VM e abra o console para realizar o assistente de configuração inicial (pule a etapa de licenciamento).

## **3\. Instalação Bare Metal: Hardware Dedicado e Hipervisores Alternativos**

### **A. Hardware Físico Dedicado**

A Cisco suporta oficialmente instalações Bare Metal diretamente nos servidores UCS modelos M5, M6 e M7 (C220 e C240). Outros hardwares Intel funcionam em regime de melhor esforço (*best effort*).

1. O servidor físico precisa estar configurado para modo de inicialização **UEFI**.  
2. Monte o arquivo ISO do controlador CML2 (ex: usando o console KVM do Cisco CIMC, montando remotamente, ou gerando um pendrive bootável via Rufus).  
   * *Dica:* Transferir a ISO por VPNs lentas via console CIMC pode causar falha na instalação. Prefira disponibilizar a ISO em um servidor HTTP local co-localizado.  
3. Inicie o servidor pelo instalador UEFI montado.  
4. O instalador é **totalmente automatizado e não interativo**; ele formatará o primeiro disco detectado e instalará o sistema base.  
   * *Instalação com múltiplos discos:* Se o servidor possuir múltiplos discos e você deseja selecionar um disco específico (evitando apagar dados de discos secundários), reinicie no menu de boot do GRUB do instalador, aperte a tecla **E** e anexe o parâmetro cml\_system\_disk=XXX (onde XXX é o identificador único do disco alvo, como sdb, nvme0n1 ou parte do nome serial detectado pelo sistema). Digite \<Ctrl+X\> para bootar.  
5. Após concluir, o instalador ejetará a mídia virtual e reiniciará o servidor.  
6. Antes de bootar o sistema pela primeira vez, acesse as opções de mídia do servidor e monte o arquivo refplat\_image.iso no leitor de CD/DVD virtual do console de gerência do hardware (CIMC/KVM).  
7. Execute o primeiro boot a partir do disco rígido e finalize o setup inicial via console. Pule as etapas de licenciamento tradicional.

### **B. Proxmox VE (KVM)**

O Proxmox não possui suporte nativo ao formato OVA da Cisco, portanto a instalação deve ser feita criando uma VM do zero utilizando o arquivo ISO do controlador CML2.

1. Faça o upload do ISO do Controlador CML2 e do ISO do *refplat* para o armazenamento de ISOs do Proxmox.  
2. Crie uma nova VM no Proxmox com as seguintes definições:  
   * **OS:** Selecione o ISO do controlador CML2.  
   * **System:** Marque o campo de BIOS como **OVMF (UEFI)** e adicione um disco EFI.  
   * **CPU:** Defina a quantidade de cores desejada. **Importante:** Mude o tipo de processador (*Type*) para **host** para repassar as instruções de virtualização Intel/AMD de forma aninhada.  
   * **Memory:** Aloque pelo menos 8 GB e desative o Ballooning Device (garante RAM física fixa para a VM).  
   * **Disks:** Adicione um disco rígido do tipo SCSI (com VirtIO SCSI) de pelo menos 100 GB.  
   * **Network:** Escolha o modo Bridge configurado na sua rede.  
3. Inicie a VM para começar a instalação do sistema. Ela será automatizada a partir do ISO do controlador.  
4. Após o reboot de conclusão da instalação, desligue a VM temporariamente.  
5. Acesse as configurações de Hardware da VM no Proxmox, adicione um segundo leitor de CD/DVD ou altere o atual para apontar para o arquivo refplat\_image.iso.  
6. Ligue a VM e acesse a console do Proxmox para preencher as credenciais e configurações de rede no assistente inicial de primeiro boot do CML.

### **C. Hyper-V (Windows Server / Windows Pro)**

Instalar no Hyper-V exige a criação manual de uma VM Geração 2 para suportar UEFI e a habilitação explícita de virtualização aninhada via PowerShell.

1. No Hyper-V Manager, crie uma nova máquina virtual:  
   * **Geração:** Escolha **Geração 2** (obrigatório para UEFI).  
   * **Memória:** Atribua 8 GB ou mais e **desmarque** a opção de Memória Dinâmica.  
   * **Rede:** Conecte a um Switch Virtual Externo configurado.  
   * **Disco Rígido Virtual:** Crie um novo disco com pelo menos 100 GB.  
   * **Opções de Instalação:** Selecione para instalar o sistema operacional a partir de um arquivo de imagem ISO (aponte para a ISO do controlador CML2).  
2. Antes de iniciar a VM, abra o PowerShell do Windows como Administrador para habilitar a virtualização aninhada na VM do CML. Execute o comando:  
   Set-VMProcessor \-VMName "NOME\_DA\_SUA\_VM\_CML" \-ExposeVirtualizationExtensions $true

3. Se o seu processador for AMD e você estiver em sistemas Windows recentes, certifique-se de que a virtualização aninhada para AMD também esteja ativa no Hyper-V.  
4. Inicie a VM CML e instale o sistema.  
5. Após o término e a reinicialização automática da instalação, desligue a VM do CML.  
6. Insira a ISO do refplat\_image.iso no drive de DVD virtual da VM através das configurações do Hyper-V.  
7. Inicie a VM e complete o processo usando o assistente inicial de terminal.