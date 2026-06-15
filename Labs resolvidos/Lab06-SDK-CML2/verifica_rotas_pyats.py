"""
Script:   verifica_rotas_pyats.py
Objetivo: Mostrar as rotas OSPF e adjacências dos 4 roteadores
          usando pyATS (conexão via terminal server do CML).
"""

from virl2_client import ClientLibrary

URL = "https://10.10.14.121/"
USER = "admin"
PASS = "Cml2@123"
LAB_ID = "78915d70-44f9-4bdd-9c76-df61821ca0a6"

c = ClientLibrary(url=URL, username=USER, password=PASS, ssl_verify=False)
lab = c.join_existing_lab(LAB_ID)
print(f"Lab: {lab.title}  |  Estado: {lab.state()}")

# Configura pyATS
for n in lab.nodes():
    n.set_pyats_credentials(username="cisco", password="cisco")
lab.pyats.sync_testbed(username="cisco", password="cisco")
lab.pyats.set_termserv_credentials(username=USER, password=PASS)

for nome in ["R1", "R2", "R3", "R4"]:
    print(f"\n{'='*50}")
    print(f"  {nome}")
    print(f"{'='*50}")

    # OSPF neighbors
    out = lab.pyats.run_command(nome, "show ip ospf neighbor")
    print("  [OSPF Neighbors]")
    for line in out.split("\n"):
        line = line.strip()
        if line and not line.startswith("Neighbor") and not line.startswith("-"):
            print(f"    {line}")

    # Rotas OSPF
    out = lab.pyats.run_command(nome, "show ip route ospf")
    print("  [Rotas OSPF]")
    for line in out.split("\n"):
        line = line.strip()
        if line.startswith("O"):
            print(f"    {line}")
