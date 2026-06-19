from virl2_client import ClientLibrary

SERVER, USERNAME, PASSWORD = "https://10.10.14.121", "admin", "Cml2@123"
client = ClientLibrary(SERVER, USERNAME, PASSWORD, ssl_verify=False)

lab = client.join_existing_lab("17e2d11d-7a5c-4dc6-bfa0-11f44127a82a")
print(f"Lab: {lab.title} | ID: {lab.id}")

# Para o lab
print("Parando lab...")
lab.stop(wait=True)
print("Limpando (wipe)...")
lab.wipe(wait=True)

# Atualiza configuracoes com nomes de interfaces corretos (Ethernet, nao GigabitEthernet)
r1 = lab.get_node_by_label("r1")
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

r2 = lab.get_node_by_label("r2")
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

r3 = lab.get_node_by_label("r3")
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

r4 = lab.get_node_by_label("r4")
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

print("Configs atualizadas! Iniciando lab...")
lab.start(wait=True)
print("Lab rodando!")
