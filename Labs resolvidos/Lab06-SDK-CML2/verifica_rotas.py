"""
Script rápido: extrai a running config de cada nó via API CML2
e mostra as configurações de interesse (hostname, IPs, OSPF).
Sem pyATS — apenas chamadas REST.
"""
from virl2_client import ClientLibrary

URL = "https://10.10.14.121/"
USER = "admin"
PASS = "Cml2@123"
LAB_ID = "78915d70-44f9-4bdd-9c76-df61821ca0a6"

c = ClientLibrary(url=URL, username=USER, password=PASS, ssl_verify=False)
lab = c.join_existing_lab(LAB_ID)
print(f"Lab: {lab.title}  |  Estado: {lab.state()}")

for nome in ["R1", "R2", "R3", "R4"]:
    node = lab.get_node_by_label(nome)
    node.extract_configuration()
    print(f"\n{'='*50}")
    print(f"  {nome}")
    print(f"{'='*50}")
    for linha in node.configuration.split("\n"):
        l = linha.strip()
        if any(kw in l for kw in ("hostname", "interface ", "ip address",
                                   "ip ospf", "router-id", "network ",
                                   "passive", "router ospf", "shutdown")):
            print(f"  {l}")
