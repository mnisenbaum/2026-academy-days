"""
Script:   lab_quadrado_ospf.py
Objetivo: Criar um lab no CML2 com 4 roteadores IOL-XE em topologia
          quadrada, configurar IPs (bloco 10.0.0.0/8), loopbacks e OSPFv2.
SDK:      virl2-client (Cisco Modeling Labs 2 Client Library)
"""

from virl2_client import ClientLibrary

# ============================================================
# CONFIGURAÇÕES DE ACESSO AO CML2
# ============================================================
URL = "https://10.10.14.121/"
USERNAME = "admin"
PASSWORD = "Cml2@123"

# Conecta ao controller CML2
# ssl_verify=False porque o certificado é auto-assinado (homologação)
client = ClientLibrary(
    url=URL,
    username=USERNAME,
    password=PASSWORD,
    ssl_verify=False,
)

info = client.system_info()
print(f"Conectado ao CML2 v{info['version']}")
print()

# ============================================================
# CRIAÇÃO DO LAB
# ============================================================
lab = client.create_lab("sdk-opencode")
print(f"Lab criado: {lab.title} (ID: {lab.id})")
print()

# ============================================================
# DEFINIÇÃO DA TOPOLOGIA
# ============================================================
# Coordenadas (x, y) para posicionar os 4 roteadores em quadrado
#     R1 (200, 100) ---- R2 (500, 100)
#           |                 |
#     R4 (200, 400) ---- R3 (500, 400)
#
# Cada roteador tem 2 links:
#   R1: Eth0/0 -> R2:Eth0/0   |   Eth0/1 -> R4:Eth0/1
#   R2: Eth0/0 -> R1:Eth0/0   |   Eth0/1 -> R3:Eth0/0
#   R3: Eth0/0 -> R2:Eth0/1   |   Eth0/1 -> R4:Eth0/0
#   R4: Eth0/0 -> R3:Eth0/1   |   Eth0/1 -> R1:Eth0/1

# Dicionário com posições e configuração de cada roteador
ROUTERS = {
    "R1": {"x": 200, "y": 100},
    "R2": {"x": 500, "y": 100},
    "R3": {"x": 500, "y": 400},
    "R4": {"x": 200, "y": 400},
}

# ============================================================
# CRIAÇÃO DOS NÓS (ROTEADORES)
# ============================================================
# "iol-xe": node definition padrão para IOL rodando IOS XE (Docker).
#   - 4 interfaces Ethernet físicas por padrão (Eth0/0 .. Eth0/3)
#   - Expansível até Eth7/3 (32 interfaces)
#   - Loopback0 já definida no template
#   - 1024 MB RAM, 1 CPU
#   - Config generator driver: iosv
#
# "iol-xe-17-18-02": image definition (versão específica do IOS XE)
#
# populate_interfaces=True tenta criar interfaces automaticamente,
# mas para IOL-XE é necessário criá-las manualmente via
# node.create_interface(slot=N).

nodes = {}
for nome, pos in ROUTERS.items():
    node = lab.create_node(
        label=nome,
        node_definition="iol-xe",
        image_definition="iol-xe-17-18-02",
        x=pos["x"],
        y=pos["y"],
    )
    # Cria as 2 interfaces Ethernet que usaremos (slots 0 e 1)
    node.create_interface(slot=0)
    node.create_interface(slot=1)
    nodes[nome] = node
    print(f"  Nó criado: {node.label} (ID: {node.id})")

print()

# ============================================================
# CRIAÇÃO DOS LINKS (CONEXÕES)
# ============================================================
# Como criamos as interfaces manualmente com slots 0 e 1, temos:
#   slot 0 = Ethernet0/0
#   slot 1 = Ethernet0/1
#
# Usamos node.get_interface_by_slot(slot) para obter o objeto
# Interface, e lab.create_link(iface_a, iface_b) para conectá-las.

links_config = [
    # (node_a, slot_a, node_b, slot_b)
    ("R1", 0, "R2", 0),   # R1:E0/0 <-> R2:E0/0
    ("R2", 1, "R3", 0),   # R2:E0/1 <-> R3:E0/0
    ("R3", 1, "R4", 0),   # R3:E0/1 <-> R4:E0/0
    ("R4", 1, "R1", 1),   # R4:E0/1 <-> R1:E0/1
]

# O método get_interface_by_slot(slot) retorna o objeto Interface
# pelo número do slot. Em seguida, lab.create_link(iface1, iface2)
# cria o link entre as duas interfaces.

for nome_a, slot_a, nome_b, slot_b in links_config:
    iface_a = nodes[nome_a].get_interface_by_slot(slot_a)
    iface_b = nodes[nome_b].get_interface_by_slot(slot_b)
    link = lab.create_link(iface_a, iface_b)
    print(f"  Link: {nome_a}:{iface_a.label} <-> {nome_b}:{iface_b.label}")

print()

# ============================================================
# ESQUEMA DE ENDEREÇAMENTO IPv4
# ============================================================
# Usando o bloco 10.0.0.0/8 com máscara /30 (2 hosts por link)
#
# Link        Sub-rede       Roteador A          Roteador B
# R1-R2    10.0.12.0/30   R1 E0/0: .1       R2 E0/0: .2
# R2-R3    10.0.23.0/30   R2 E0/1: .1       R3 E0/0: .2
# R3-R4    10.0.34.0/30   R3 E0/1: .1       R4 E0/0: .2
# R4-R1    10.0.41.0/30   R4 E0/1: .1       R1 E0/1: .2
#
# Loopbacks (máscara /32):
#   R1: 1.1.1.1/32   R2: 2.2.2.2/32
#   R3: 3.3.3.3/32   R4: 4.4.4.4/32
#
# OSPF: processo 1, área 0 em todas as interfaces
# As loopbacks são configuradas como passive para não enviar hellos.

LINK_IPS = {
    # (node_a, slot_a): (ip_a, ip_b, prefixo, mascara_wildcard)
    # node_b, slot_b será inferido
    ("R1", 0): ("10.0.12.1", "10.0.12.2", "255.255.255.252"),
    ("R2", 0): ("10.0.12.2", "10.0.12.1", "255.255.255.252"),
    ("R2", 1): ("10.0.23.1", "10.0.23.2", "255.255.255.252"),
    ("R3", 0): ("10.0.23.2", "10.0.23.1", "255.255.255.252"),
    ("R3", 1): ("10.0.34.1", "10.0.34.2", "255.255.255.252"),
    ("R4", 0): ("10.0.34.2", "10.0.34.1", "255.255.255.252"),
    ("R4", 1): ("10.0.41.1", "10.0.41.2", "255.255.255.252"),
    ("R1", 1): ("10.0.41.2", "10.0.41.1", "255.255.255.252"),
}

LOOPBACKS = {
    "R1": "1.1.1.1",
    "R2": "2.2.2.2",
    "R3": "3.3.3.3",
    "R4": "4.4.4.4",
}

# ============================================================
# GERAÇÃO E INJEÇÃO DAS CONFIGURAÇÕES
# ============================================================
# O nó IOL-XE possui um arquivo editável "ios_config.txt" que
# contém a startup configuration. O SDK expõe esse conteúdo
# através da propriedade node.configuration (leitura/escrita).
#
# Ao setar node.configuration = "..." atualizamos o arquivo no
# CML2. Quando o lab for iniciado, o CML gera a config final
# a partir desse template.
#
# NOTA: O template original usa "inserthostname-here" como
# placeholder do hostname. O config generator do CML (driver
# iosv) substitui esse placeholder pelo label do nó. Vamos
# escrever a config inteira manualmente para ter controle total.

def gerar_config(nome):
    """
    Gera a configuração IOS completa para um roteador.
    """
    lb_ip = LOOPBACKS[nome]
    linhas = [f"hostname {nome}", "!"]

    # --- Interface Loopback ---
    linhas += [
        "interface Loopback0",
        f" ip address {lb_ip} 255.255.255.255",
        " ip ospf 1 area 0",
        "!",
    ]

    # --- Interfaces Ethernet ---
    # Itera sobre todos os slots configurados para este roteador
    for slot in (0, 1):
        chave = (nome, slot)
        if chave not in LINK_IPS:
            continue
        ip, _, mascara = LINK_IPS[chave]
        iface = nodes[nome].get_interface_by_slot(slot)
        iface_label = iface.label
        linhas += [
            f"interface {iface_label}",
            f" ip address {ip} {mascara}",
            " ip ospf 1 area 0",
            " no shutdown",
            "!",
        ]

    # --- OSPF ---
    # Configuração via router ospf com network statements
    # Roteador OSPFv2, área 0 em todas as interfaces
    # As redes a serem anunciadas são derivadas dos IPs configurados
    linhas += [
        "router ospf 1",
        f" router-id {lb_ip}",
        " passive-interface Loopback0",
        " log-adjacency-changes",
    ]

    # Network statements: para cada interface, converte ip/mascara
    # em network + wildcard
    for slot in (0, 1):
        chave = (nome, slot)
        if chave not in LINK_IPS:
            continue
        ip, _, mascara = LINK_IPS[chave]

        # Converte máscara de sub-rede para wildcard
        from ipaddress import IPv4Address, IPv4Network
        rede = IPv4Network(f"{ip}/{mascara}", strict=False)
        # O comando network no IOS espera:
        #   network <rede> <wildcard-mask> area <area>
        wildcard = str(rede.hostmask)
        linhas.append(f" network {rede.network_address} {wildcard} area 0")

    linhas += ["!", "end"]
    return "\n".join(linhas)


# Aplica a configuração em cada nó
for nome in ROUTERS:
    config_texto = gerar_config(nome)
    nodes[nome].configuration = config_texto
    print(f"  Configuração aplicada em {nome}")

print()

# ============================================================
# CONSTRUÇÃO DAS CONFIGURAÇÕES E INÍCIO DO LAB
# ============================================================
# build_configurations() gera os arquivos de configuração
# finais para todos os nós que possuem suporte a config
# generator e que ainda não foram configurados.
#
# Em seguida, start() inicia todos os nós do lab.
# O parâmetro wait=True faz o SDK aguardar até que todos
# os nós estejam bootados (convergência).

# NOTA: As configurações já foram injetadas diretamente via
# node.configuration. O CML2 usará essas configurações no boot.
# O método build_configurations() é usado para nós que dependem
# do config generator do CML (não é nosso caso aqui).

print("Iniciando lab (isso pode levar alguns minutos)...")
lab.start(wait=True)

print()
print("Lab concluído! Todos os roteadores estão operacionais.")
