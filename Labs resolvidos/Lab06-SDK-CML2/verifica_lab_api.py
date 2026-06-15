"""
Script:   verifica_lab_api.py
Objetivo: Verificar a configuração dos 4 roteadores IOL-XE no lab
          "sdk-opencode" usando apenas a API do CML2 (sem SSH/pyATS).
SDK:      virl2-client
"""

from virl2_client import ClientLibrary

# ============================================================
# CONFIGURAÇÕES
# ============================================================
URL = "https://10.10.14.121/"
USERNAME = "admin"
PASSWORD = "Cml2@123"
LAB_NAME = "sdk-opencode"

# Valores esperados de acordo com o script de criação
EXPECTED = {
    "R1": {
        "loopback": ("1.1.1.1", "255.255.255.255"),
        "interfaces": {
            "Ethernet0/0": ("10.0.12.1", "255.255.255.252"),
            "Ethernet0/1": ("10.0.41.2", "255.255.255.252"),
        },
        "router_id": "1.1.1.1",
        "ospf_networks": ["10.0.12.0", "10.0.41.0"],
    },
    "R2": {
        "loopback": ("2.2.2.2", "255.255.255.255"),
        "interfaces": {
            "Ethernet0/0": ("10.0.12.2", "255.255.255.252"),
            "Ethernet0/1": ("10.0.23.1", "255.255.255.252"),
        },
        "router_id": "2.2.2.2",
        "ospf_networks": ["10.0.12.0", "10.0.23.0"],
    },
    "R3": {
        "loopback": ("3.3.3.3", "255.255.255.255"),
        "interfaces": {
            "Ethernet0/0": ("10.0.23.2", "255.255.255.252"),
            "Ethernet0/1": ("10.0.34.1", "255.255.255.252"),
        },
        "router_id": "3.3.3.3",
        "ospf_networks": ["10.0.23.0", "10.0.34.0"],
    },
    "R4": {
        "loopback": ("4.4.4.4", "255.255.255.255"),
        "interfaces": {
            "Ethernet0/0": ("10.0.34.2", "255.255.255.252"),
            "Ethernet0/1": ("10.0.41.1", "255.255.255.252"),
        },
        "router_id": "4.4.4.4",
        "ospf_networks": ["10.0.34.0", "10.0.41.0"],
    },
}


def verifica_hostname(hostname, config):
    """Verifica se o hostname está correto na config."""
    for linha in config.split("\n"):
        linha = linha.strip()
        if linha.startswith("hostname "):
            return linha.split("hostname ")[1].strip() == hostname
    return False


def verifica_interface(iface, ip_esperado, mask_esperada, config):
    """
    Verifica se a interface possui o IP/mask configurados.
    Procura pelo bloco 'interface <iface>' e lê as linhas seguintes.
    """
    linhas = config.split("\n")
    dentro = False
    ip = None
    mask = None
    shutdown = False
    for linha in linhas:
        linha_strip = linha.strip()
        if linha_strip.startswith(f"interface {iface}"):
            dentro = True
            continue
        if dentro:
            if linha_strip.startswith("interface ") or linha_strip.startswith("!"):
                break
            if linha_strip.startswith("ip address "):
                partes = linha_strip.split()
                if len(partes) >= 3:
                    ip = partes[2]
                    mask = partes[3] if len(partes) >= 4 else None
            if linha_strip == "shutdown":
                shutdown = True

    ip_ok = ip == ip_esperado and mask == mask_esperada
    shutdown_ok = not shutdown
    return ip_ok, shutdown_ok, ip, mask, shutdown


def verifica_loopback(ip_esperado, mask_esperada, config):
    """Verifica a interface Loopback0."""
    ip_ok, _, ip, mask, _ = verifica_interface("Loopback0", ip_esperado, mask_esperada, config)
    return ip_ok, ip, mask


def verifica_ospf_router_id(router_id_esperado, config):
    """Verifica o router-id do OSPF."""
    linhas = config.split("\n")
    dentro_ospf = False
    router_id = None
    for linha in linhas:
        linha_strip = linha.strip()
        if linha_strip.startswith("router ospf 1"):
            dentro_ospf = True
            continue
        if dentro_ospf:
            if linha_strip.startswith("!") or linha_strip.startswith("end") or linha_strip.startswith("interface "):
                break
            if "router-id" in linha_strip:
                router_id = linha_strip.split("router-id")[1].strip()
    return router_id == router_id_esperado, router_id


def verifica_ospf_networks(redes_esperadas, config):
    """Verifica os network statements do OSPF."""
    linhas = config.split("\n")
    dentro_ospf = False
    redes_encontradas = []
    for linha in linhas:
        linha_strip = linha.strip()
        if linha_strip.startswith("router ospf 1"):
            dentro_ospf = True
            continue
        if dentro_ospf:
            if linha_strip.startswith("!") or linha_strip.startswith("end") or linha_strip.startswith("interface "):
                break
            if linha_strip.startswith("network "):
                partes = linha_strip.split()
                if len(partes) >= 2:
                    redes_encontradas.append(partes[1])
    return sorted(redes_encontradas) == sorted(redes_esperadas), redes_encontradas


def verifica_passive_loopback(config):
    """Verifica se a Loopback0 está como passive-interface no OSPF."""
    linhas = config.split("\n")
    dentro_ospf = False
    for linha in linhas:
        linha_strip = linha.strip()
        if linha_strip.startswith("router ospf 1"):
            dentro_ospf = True
            continue
        if dentro_ospf:
            if linha_strip.startswith("!") or linha_strip.startswith("end") or linha_strip.startswith("interface "):
                break
            if "passive-interface" in linha_strip and "Loopback0" in linha_strip:
                return True
    return False


def verifica_no_shutdown(iface, config):
    """Verifica se a interface NÃO tem 'shutdown'."""
    _, _, _, shutdown = verifica_interface(iface, None, None, config)
    return not shutdown


# ============================================================
# EXECUÇÃO PRINCIPAL
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

# Encontra o lab pelo nome (prioriza o que está em execução)
labs = client.all_labs()
lab = None
for l in labs:
    if l.title == LAB_NAME:
        estado = l.state()
        # Prefere labs em STARTED; se não achar, pega o último
        if estado == "STARTED" or lab is None:
            lab = l

if lab is None:
    print(f"ERRO: Lab '{LAB_NAME}' não encontrado!")
    exit(1)

estado_lab = lab.state()
print(f"Lab: {lab.title} (ID: {lab.id})")
print(f"Estado do lab: {estado_lab}")
print()

if estado_lab != "STARTED":
    print("⚠️  O lab não está em execução. Iniciando...")
    lab.start(wait=True)
    print("  -> STARTED")
    print()

# ============================================================
# VERIFICAÇÃO NÓ A NÓ
# ============================================================
resultados = {}

for nome_host in ["R1", "R2", "R3", "R4"]:
    print(f"{'='*60}")
    print(f"  VERIFICANDO: {nome_host}")
    print(f"{'='*60}")

    node = lab.get_node_by_label(nome_host)
    exp = EXPECTED[nome_host]

    # Verifica se o nó está bootado antes de extrair config
    if not node.is_booted():
        print(f"  ⚠️  Nó não está bootado. Aguardando...")
        node.wait_until_converged()

    # Extrai a running config via API do CML2 (não requer SSH)
    node.extract_configuration()
    config = node.configuration

    resultado = {}

    # --- Hostname ---
    hostname_ok = verifica_hostname(nome_host, config)
    resultado["hostname"] = ("✅" if hostname_ok else "❌", nome_host if hostname_ok else "---")
    print(f"  hostname {nome_host}: {'✅ OK' if hostname_ok else '❌ FALHOU'}")

    # --- Loopback0 ---
    lb_ok, lb_ip, lb_mask = verifica_loopback(exp["loopback"][0], exp["loopback"][1], config)
    resultado["loopback"] = ("✅" if lb_ok else "❌", f"{lb_ip or 'N/A'}/{lb_mask or 'N/A'}")
    esperado_lb = f"{exp['loopback'][0]}/{exp['loopback'][1]}"
    print(f"  Loopback0: {lb_ip or 'N/A'}/{lb_mask or 'N/A'}  (esperado: {esperado_lb}) {'✅' if lb_ok else '❌'}")

    # --- Interfaces Ethernet ---
    for iface_nome, (ip_esp, mask_esp) in exp["interfaces"].items():
        ip_ok, shutdown_ok, ip, mask, shutdown = verifica_interface(iface_nome, ip_esp, mask_esp, config)
        estado = "up" if not shutdown else "shutdown"
        resultado[iface_nome] = ("✅" if ip_ok and not shutdown else "❌", f"{ip}/{mask} ({estado})")
        print(f"  {iface_nome}: {ip}/{mask} {estado}  (esperado: {ip_esp}/{mask_esp}, up) {'✅' if ip_ok and not shutdown else '❌'}")

    # --- OSPF router-id ---
    rid_ok, rid = verifica_ospf_router_id(exp["router_id"], config)
    resultado["router-id"] = ("✅" if rid_ok else "❌", rid or "N/A")
    print(f"  OSPF router-id: {rid or 'N/A'}  (esperado: {exp['router_id']}) {'✅' if rid_ok else '❌'}")

    # --- OSPF network statements ---
    nets_ok, redes = verifica_ospf_networks(exp["ospf_networks"], config)
    resultado["ospf_networks"] = ("✅" if nets_ok else "❌", ", ".join(redes) if redes else "N/A")
    print(f"  OSPF networks: {', '.join(redes) if redes else 'N/A'}  (esperado: {', '.join(exp['ospf_networks'])}) {'✅' if nets_ok else '❌'}")

    # --- passive-interface Loopback0 ---
    passive_ok = verifica_passive_loopback(config)
    resultado["passive"] = ("✅" if passive_ok else "❌", "")
    print(f"  passive-interface Loopback0: {'✅ OK' if passive_ok else '❌ FALHOU'}")

    resultados[nome_host] = resultado
    print()

# ============================================================
# TABELA RESUMO
# ============================================================
print(f"\n{'='*70}")
print("  RESUMO DA VERIFICAÇÃO")
print(f"{'='*70}")
print()
print(f"{'Item':<22} {'R1':<12} {'R2':<12} {'R3':<12} {'R4':<12}")
print("-" * 70)

checks = [
    ("hostname", "hostname"),
    ("Loopback0", "loopback"),
    ("Ethernet0/0", "Ethernet0/0"),
    ("Ethernet0/1", "Ethernet0/1"),
    ("OSPF router-id", "router-id"),
    ("OSPF networks", "ospf_networks"),
    ("passive Lo0", "passive"),
]

total_ok = 0
total_checks = 0

for label, chave in checks:
    linhas_resumo = []
    for nome in ["R1", "R2", "R3", "R4"]:
        if chave == "passive":
            status, _ = resultados[nome].get(chave, ("❌", ""))
        elif chave == "loopback":
            status, detalhe = resultados[nome].get(chave, ("❌", ""))
            if status == "✅":
                total_ok += 1
        else:
            status, detalhe = resultados[nome].get(chave, ("❌", ""))
        linhas_resumo.append(status)
        if chave not in ("passive",):
            total_checks += 1
            if status == "✅":
                total_ok += 1

    print(f"  {label:<20} {linhas_resumo[0]:<12} {linhas_resumo[1]:<12} {linhas_resumo[2]:<12} {linhas_resumo[3]:<12}")

print("-" * 70)
print(f"\nResultado: {total_ok}/{total_checks} verificações OK")

if total_ok == total_checks:
    print("\n✅ LAB VERIFICADO COM SUCESSO — Todas as configurações estão corretas!")
else:
    print(f"\n⚠️  {total_checks - total_ok} verificação(ões) falharam — revise os detalhes acima.")
