#!/usr/bin/env python3
"""Verifica OSPF - console logs + show commands"""

from virl2_client import ClientLibrary

SERVER, USERNAME, PASSWORD = "https://10.10.14.121", "admin", "Cml2@123"
client = ClientLibrary(SERVER, USERNAME, PASSWORD, ssl_verify=False)

lab = client.join_existing_lab("17e2d11d-7a5c-4dc6-bfa0-11f44127a82a")
print(f"Lab: {lab.title} | ID: {lab.id}\n")

lab.pyats.sync_testbed(USERNAME, PASSWORD)

for nome in ("r1", "r2", "r3", "r4"):
    node = lab.get_node_by_label(nome)
    try:
        out = node.run_pyats_command("show ip ospf neighbor", init_exec_commands=[])
        print(f"=== {nome} - show ip ospf neighbor ===")
        print(out)
        print()
    except Exception as e:
        print(f"=== {nome} === ERRO: {e}\n")

    try:
        out2 = node.run_pyats_command("show ip interface brief", init_exec_commands=[])
        print(f"=== {nome} - show ip interface brief ===")
        print(out2)
        print()
    except Exception as e:
        print(f"=== {nome} - ip int brief === ERRO: {e}\n")
