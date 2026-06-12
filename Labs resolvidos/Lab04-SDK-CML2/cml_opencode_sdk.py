#!/usr/bin/env python3
"""
Cisco CML2 - Lab opencode-sdk
Topologia: 4 roteadores iol-xe em quadrado com OSPFv2

Cria:
  - 4 nos iol-xe (r1, r2, r3, r4) formando um quadrado
  - 4 links (lados do quadrado)
  - IPs nos links (10.x.y.0/24)
  - Loopbacks (x.x.x.x/32)
  - OSPFv2 area 0 em todos os roteadores
"""

from virl2_client import ClientLibrary

# ============================================================
# 1. CONEXAO AO CML2
# ============================================================
SERVER = "https://10.10.14.121"
USERNAME = "admin"
PASSWORD = "Cml2@123"

client = ClientLibrary(SERVER, USERNAME, PASSWORD, ssl_verify=False)
print(f"[OK] Conectado ao CML2 em {SERVER}")

# ============================================================
# 2. CRIAR LAB
# ============================================================
lab = client.create_lab(
    title="opencode-sdk",
    description="Lab 4x iol-xe com OSPFv2 - gerado via Python SDK",
)
print(f"[OK] Lab criado: '{lab.title}' (ID: {lab.id})")

# ============================================================
# 3. CRIAR NOS (vertices do quadrado)
# ============================================================
r1 = lab.create_node("r1", "iol-xe", x=100, y=100)
r2 = lab.create_node("r2", "iol-xe", x=400, y=100)
r3 = lab.create_node("r3", "iol-xe", x=400, y=400)
r4 = lab.create_node("r4", "iol-xe", x=100, y=400)
print("[OK] Nos criados: r1, r2, r3, r4")

# ============================================================
# 4. CRIAR LINKS (lados do quadrado)
#    IOL usa interfaces Ethernet0/0, Ethernet1/0, etc.
# ============================================================
# r1:Ethernet0/0 <-> r2:Ethernet0/0   (10.1.2.0/24)
lab.connect_two_nodes(r1, r2)
# r2:Ethernet1/0 <-> r3:Ethernet0/0   (10.2.3.0/24)
lab.connect_two_nodes(r2, r3)
# r3:Ethernet1/0 <-> r4:Ethernet0/0   (10.3.4.0/24)
lab.connect_two_nodes(r3, r4)
# r4:Ethernet1/0 <-> r1:Ethernet1/0   (10.1.4.0/24)
lab.connect_two_nodes(r4, r1)
print("[OK] Links criados: r1-r2, r2-r3, r3-r4, r4-r1")

# ============================================================
# 5. CONFIGURACOES (IPs + Loopbacks + OSPFv2)
#    ATENCAO: IOL usa Ethernet, NAO GigabitEthernet
# ============================================================

# r1: Eth0/0 -> 10.1.2.1, Eth1/0 -> 10.1.4.1, Lo0 -> 1.1.1.1/32
r1.configuration = """\
hostname r1
!
interface Loopback0
 ip address 1.1.1.1 255.255.255.255
!
interface Ethernet0/0
 ip address 10.1.2.1 255.255.255.0
 no shutdown
!
interface Ethernet1/0
 ip address 10.1.4.1 255.255.255.0
 no shutdown
!
router ospf 1
 router-id 1.1.1.1
 network 1.1.1.1 0.0.0.0 area 0
 network 10.1.2.0 0.0.0.255 area 0
 network 10.1.4.0 0.0.0.255 area 0
!
end"""

# r2: Eth0/0 -> 10.1.2.2, Eth1/0 -> 10.2.3.2, Lo0 -> 2.2.2.2/32
r2.configuration = """\
hostname r2
!
interface Loopback0
 ip address 2.2.2.2 255.255.255.255
!
interface Ethernet0/0
 ip address 10.1.2.2 255.255.255.0
 no shutdown
!
interface Ethernet1/0
 ip address 10.2.3.2 255.255.255.0
 no shutdown
!
router ospf 1
 router-id 2.2.2.2
 network 2.2.2.2 0.0.0.0 area 0
 network 10.1.2.0 0.0.0.255 area 0
 network 10.2.3.0 0.0.0.255 area 0
!
end"""

# r3: Eth0/0 -> 10.2.3.3, Eth1/0 -> 10.3.4.3, Lo0 -> 3.3.3.3/32
r3.configuration = """\
hostname r3
!
interface Loopback0
 ip address 3.3.3.3 255.255.255.255
!
interface Ethernet0/0
 ip address 10.2.3.3 255.255.255.0
 no shutdown
!
interface Ethernet1/0
 ip address 10.3.4.3 255.255.255.0
 no shutdown
!
router ospf 1
 router-id 3.3.3.3
 network 3.3.3.3 0.0.0.0 area 0
 network 10.2.3.0 0.0.0.255 area 0
 network 10.3.4.0 0.0.0.255 area 0
!
end"""

# r4: Eth0/0 -> 10.3.4.4, Eth1/0 -> 10.1.4.4, Lo0 -> 4.4.4.4/32
r4.configuration = """\
hostname r4
!
interface Loopback0
 ip address 4.4.4.4 255.255.255.255
!
interface Ethernet0/0
 ip address 10.3.4.4 255.255.255.0
 no shutdown
!
interface Ethernet1/0
 ip address 10.1.4.4 255.255.255.0
 no shutdown
!
router ospf 1
 router-id 4.4.4.4
 network 4.4.4.4 0.0.0.0 area 0
 network 10.3.4.0 0.0.0.255 area 0
 network 10.1.4.0 0.0.0.255 area 0
!
end"""

print("[OK] Configuracoes aplicadas nos 4 nos")

# ============================================================
# 6. INICIAR LAB
# ============================================================
print("[...] Iniciando lab (aguardando convergencia)...")
lab.start(wait=True)
print("[OK] Lab em execucao!")

# ============================================================
# 7. RESUMO
# ============================================================
print()
print("=" * 50)
print(f"  Lab:  {lab.title}")
print(f"  ID:   {lab.id}")
print(f"  Nos:  4x iol-xe")
print(f"  OSPF: Area 0 em todos os roteadores")
print("=" * 50)
