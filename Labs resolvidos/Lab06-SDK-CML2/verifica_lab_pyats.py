"""
Script:   verifica_lab_pyats.py
Objetivo: Verificar o lab "sdk-opencode" usando pyATS integrado ao CML2.
Conexão:  via terminal server do CML (console), sem SSH direto ao dispositivo.
"""

from virl2_client import ClientLibrary
import re

# ============================================================
# CONFIGURAÇÕES
# ============================================================
URL = "https://10.10.14.121/"
USERNAME = "admin"
PASSWORD = "Cml2@123"
LAB_NAME = "sdk-opencode"

DEVICE_USER = "cisco"
DEVICE_PASS = "cisco"

# (node_a, slot_a, node_b, slot_b) — mesma topologia do lab_quadrado_ospf.py
LINKS = [
    ("R1", "Ethernet0/0", "10.0.12.1", "R2", "Ethernet0/0", "10.0.12.2"),
    ("R2", "Ethernet0/1", "10.0.23.1", "R3", "Ethernet0/0", "10.0.23.2"),
    ("R3", "Ethernet0/1", "10.0.34.1", "R4", "Ethernet0/0", "10.0.34.2"),
    ("R4", "Ethernet0/1", "10.0.41.1", "R1", "Ethernet0/1", "10.0.41.2"),
]

LOOPBACKS = {"R1": "1.1.1.1", "R2": "2.2.2.2", "R3": "3.3.3.3", "R4": "4.4.4.4"}

# (vizinho_id, ip_link) — adjacências esperadas em cada nó
OSPF_ADJ = {
    "R1": [("2.2.2.2", "10.0.12.2"), ("4.4.4.4", "10.0.41.1")],
    "R2": [("1.1.1.1", "10.0.12.1"), ("3.3.3.3", "10.0.23.2")],
    "R3": [("2.2.2.2", "10.0.23.1"), ("4.4.4.4", "10.0.34.2")],
    "R4": [("1.1.1.1", "10.0.41.2"), ("3.3.3.3", "10.0.34.1")],
}

# Prefixos OSPF que cada nó deve aprender (via OSPF, excluindo connected)
ROTAS_ESPERADAS = {
    "R1": ["10.0.23.0/30", "10.0.34.0/30", "2.2.2.2/32", "3.3.3.3/32", "4.4.4.4/32"],
    "R2": ["10.0.34.0/30", "10.0.41.0/30", "1.1.1.1/32", "3.3.3.3/32", "4.4.4.4/32"],
    "R3": ["10.0.12.0/30", "10.0.41.0/30", "1.1.1.1/32", "2.2.2.2/32", "4.4.4.4/32"],
    "R4": ["10.0.12.0/30", "10.0.23.0/30", "1.1.1.1/32", "2.2.2.2/32", "3.3.3.3/32"],
}

# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def linhas_uteis(texto):
    """Remove linhas de syslog, cabeçalhos de tabela, e linhas vazias."""
    resultado = []
    for linha in texto.split("\n"):
        linha = linha.strip().replace("\r", "")
        if not linha:
            continue
        # Pula syslog (*Jun 15 ...), cabeçalhos de tabelas
        if re.match(r"^\*", linha):
            continue
        if re.match(r"^(Neighbor|Interface|Codes:|Gateway|  )", linha):
            continue
        if linha.startswith("-"):
            continue
        resultado.append(linha)
    return resultado


def parse_show_ip_int_brief(output):
    """Extrai {interface: (ip, status, protocol)} do 'show ip interface brief'."""
    ifaces = {}
    for linha in linhas_uteis(output):
        partes = linha.split()
        if len(partes) < 6:
            continue
        nome = partes[0]
        ip = partes[1]
        # "administratively down" = 2 palavras
        if len(partes) == 7:
            status = f"{partes[4]} {partes[5]}"
            proto = partes[6]
        elif len(partes) == 6:
            status = partes[4]
            proto = partes[5]
        else:
            continue
        ifaces[nome] = (ip, status, proto)
    return ifaces


def parse_ospf_neighbor(output):
    """Extrai lista de (neighbor_id, address, interface) do 'show ip ospf neighbor'."""
    vizinhos = []
    for linha in linhas_uteis(output):
        partes = linha.split()
        # Formato: <RID> <Pri> <State> <Dead Time> <Address> <Interface>
        if len(partes) >= 6 and "FULL" in partes[2]:
            vizinhos.append((partes[0], partes[4], partes[5]))
    return vizinhos


def parse_show_ip_route_ospf(output):
    """Extrai lista de prefixos aprendidos via OSPF."""
    prefixos = []
    for linha in output.split("\n"):
        linha = linha.strip()
        if linha.startswith("O") and not linha.startswith("O "):
            continue
        # Linha de rota: O <prefixo> [cost] via <next-hop>
        # ou O <prefixo> is subnetted
        m = re.match(r"O\s+(\S+)", linha)
        if m:
            prefixos.append(m.group(1))
    return prefixos


def check_ping(output):
    """Verifica se o ping teve 100% de sucesso."""
    return "!!!!!" in output or "Success rate is 100 percent" in output


# ============================================================
# CONEXÃO
# ============================================================
client = ClientLibrary(
    url=URL,
    username=USERNAME,
    password=PASSWORD,
    ssl_verify=False,
)

info = client.system_info()
print(f"Conectado ao CML2 v{info['version']}")
print()

# --- Localiza lab (prioridade: STARTED > stopped) ---
lab_encontrado = None
for l in client.all_labs():
    if l.title == LAB_NAME and (lab_encontrado is None or l.state() == "STARTED"):
        lab_encontrado = l
if lab_encontrado is None:
    print(f"ERRO: Lab '{LAB_NAME}' não encontrado!")
    exit(1)

lab = lab_encontrado
estado = lab.state()
print(f"Lab: {lab.title} (ID: {lab.id}) | Estado: {estado}")
if estado != "STARTED":
    print("Iniciando lab...")
    lab.start(wait=True)
print()

# --- pyATS: credenciais ---
for node in lab.nodes():
    node.set_pyats_credentials(username=DEVICE_USER, password=DEVICE_PASS)
lab.pyats.sync_testbed(username=DEVICE_USER, password=DEVICE_PASS)
lab.pyats.set_termserv_credentials(username=USERNAME, password=PASSWORD)

# ============================================================
# VERIFICAÇÕES
# ============================================================
results = {}

for nome in ["R1", "R2", "R3", "R4"]:
    node = lab.get_node_by_label(nome)
    print(f"{'='*55}")
    print(f"  {nome}")
    print(f"{'='*55}")

    res = {}

    # --- 1. Interfaces ---
    print("\n  [1] Interfaces (show ip interface brief)")
    saida = lab.pyats.run_command(nome, "show ip interface brief")
    ifaces = parse_show_ip_int_brief(saida)

    for alvo, ip_esp in [("Loopback0", LOOPBACKS[nome]),
                         ("Ethernet0/0", None), ("Ethernet0/1", None)]:
        if alvo in ifaces:
            ip, status, proto = ifaces[alvo]
            ok = (ip == ip_esp if ip_esp else ip not in ("unassigned",)) and status == "up" and proto == "up"
            res[f"iface:{alvo}"] = "✅" if ok else "❌"
            print(f"    {alvo:<15} IP={ip:<15} Status={status:<20} Proto={proto} {'✅' if ok else '❌'}")
        else:
            res[f"iface:{alvo}"] = "❌"
            print(f"    {alvo:<15} não encontrada ❌")

    # Verifica IPs dos links nos pares Ethernet
    for a_nome, a_iface, a_ip, b_nome, b_iface, b_ip in LINKS:
        if a_nome != nome:
            continue
        if a_iface in ifaces:
            ip, status, proto = ifaces[a_iface]
            ok = ip == a_ip and status == "up" and proto == "up"
            res[f"link:{b_nome}"] = "✅" if ok else "❌"
            print(f"    {a_iface:<15} → {b_nome:<3} IP={ip:<15} {'✅' if ok else '❌'} (esperado {a_ip})")
        else:
            res[f"link:{b_nome}"] = "❌"
            print(f"    {a_iface:<15} → {b_nome:<3} não encontrada ❌")

    # --- 2. OSPF neighbors ---
    print("\n  [2] OSPF neighbors (show ip ospf neighbor)")
    saida = lab.pyats.run_command(nome, "show ip ospf neighbor")
    vizinhos = parse_ospf_neighbor(saida)
    vizinhos_ids = {v[0] for v in vizinhos}

    for rid_esp, ip_esp in OSPF_ADJ[nome]:
        ok = rid_esp in vizinhos_ids
        res[f"ospf:{rid_esp}"] = "✅" if ok else "❌"
        status = "FULL" if ok else "ausente"
        print(f"    {rid_esp:<15} ({ip_esp:<12}) {status} {'✅' if ok else '❌'}")

    if not vizinhos:
        print("    (nenhuma adjacência encontrada)")

    # --- 3. Rotas OSPF ---
    print("\n  [3] Rotas OSPF (show ip route ospf)")
    saida = lab.pyats.run_command(nome, "show ip route ospf")
    aprendidas = set(parse_show_ip_route_ospf(saida))
    esperadas = set(ROTAS_ESPERADAS[nome])
    acertos = aprendidas & esperadas
    faltas = esperadas - aprendidas
    res["rotas"] = f"✅ ({len(acertos)}/{len(esperadas)})" if not faltas else f"❌"
    print(f"    Encontradas: {len(acertos)}/{len(esperadas)}")
    for p in sorted(esperadas):
        print(f"      {p} {'✅' if p in acertos else '❌'}")

    # --- 4. Ping ---
    print("\n  [4] Ping")
    if nome == "R1":
        alvos = [
            ("10.0.12.2", "R2 (Eth0/0)"),
            ("10.0.41.1", "R4 (Eth0/1)"),
            ("4.4.4.4", "R4 (Loopback)"),
        ]
        for alvo, desc in alvos:
            try:
                saida = lab.pyats.run_command(nome, f"ping {alvo}")
                ok = check_ping(saida)
                res[f"ping:{alvo}"] = "✅" if ok else "❌"
                print(f"    ping {alvo} ({desc}): {'✅' if ok else '❌'}")
            except Exception as e:
                res[f"ping:{alvo}"] = "❌"
                print(f"    ping {alvo} ({desc}): ❌ (erro)")
    else:
        print("    (testado apenas a partir do R1)")

    results[nome] = res
    print()

# ============================================================
# TABELA RESUMO
# ============================================================
print(f"\n{'='*70}")
print("  RESUMO — VERIFICAÇÃO pyATS")
print(f"{'='*70}\n")

print(f"  {'Verificação':<30} {'R1':<10} {'R2':<10} {'R3':<10} {'R4':<10}")
print(f"  {'-'*60}")

linhas_resumo = [
    ("Loopback0", "iface:Loopback0"),
    ("Eth0/0 → link 1", "link:R2", "link:R1", "link:R2", "link:R3"),
    ("Eth0/1 → link 2", "link:R4", "link:R3", "link:R4", "link:R1"),
]

for label, r1k, r2k, r3k, r4k in [
    ("Loopback0", "iface:Loopback0", "iface:Loopback0", "iface:Loopback0", "iface:Loopback0"),
    ("Eth0/0 (link)", "link:R2", "link:R1", "link:R2", "link:R3"),
    ("Eth0/1 (link)", "link:R4", "link:R3", "link:R4", "link:R1"),
    ("OSPF vizinho 1", "ospf:2.2.2.2", "ospf:1.1.1.1", "ospf:2.2.2.2", "ospf:1.1.1.1"),
    ("OSPF vizinho 2", "ospf:4.4.4.4", "ospf:3.3.3.3", "ospf:4.4.4.4", "ospf:3.3.3.3"),
]:
    vals = [results["R1"].get(r1k, "❌"),
            results["R2"].get(r2k, "❌"),
            results["R3"].get(r3k, "❌"),
            results["R4"].get(r4k, "❌")]
    print(f"  {label:<28} {vals[0]:<10} {vals[1]:<10} {vals[2]:<10} {vals[3]:<10}")

# Linha das rotas
print(f"  {'Rotas OSPF':<28} ", end="")
for nome in ["R1", "R2", "R3", "R4"]:
    v = results[nome].get("rotas", "❌")
    print(f"{v:<10} ", end="")
print()

# Pings
ping_r1 = [v for k, v in results["R1"].items() if k.startswith("ping:")]
pings_ok = sum(1 for p in ping_r1 if p == "✅")
print(f"  {'Pings (R1)':<28} {pings_ok}/{len(ping_r1)} ✅")

# Total
total_ok = 0
total_checks = 0
for nome in ["R1", "R2", "R3", "R4"]:
    for chave, valor in results[nome].items():
        if chave == "rotas":
            total_checks += 1
            if valor.startswith("✅"):
                total_ok += 1
        elif chave.startswith("ping:"):
            continue  # contado no resumo de pings
        else:
            total_checks += 1
            if valor == "✅":
                total_ok += 1

print()
print(f"  {'='*60}")
print(f"  Resultado geral: {total_ok}/{total_checks} verificações OK")
if total_ok == total_checks:
    print("  ✅ LAB VERIFICADO COM SUCESSO — OSPF convergiu!")
else:
    print(f"  ⚠️  {total_checks - total_ok} falha(s)")
print(f"  {'='*60}")
