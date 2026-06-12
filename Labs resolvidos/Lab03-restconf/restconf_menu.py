import getpass
import json
import sys
import requests

# Desabilita avisos de certificados SSL autoassinados (comum em sandboxes DevNet)
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configurações do ambiente Sandbox DevNet
HOSTNAME = "devnetsandboxiosxec8k.cisco.com"
PORT = "443"
BASE_URL = f"https://{HOSTNAME}:{PORT}"

# Cabeçalhos padrão para RESTCONF
HEADERS = {
    "Content-Type": "application/yang-data+json",
    "Accept": "application/yang-data+json",
}


def solicitar_credenciais():
    print("=== Conexão RESTCONF Cisco Catalyst 8000V (DevNet Sandbox) ===")
    username = (
        input("Digite o usuário (padrão: npe-restconf): ").strip()
        or "npe-restconf"
    )
    password = getpass.getpass("Digite a senha: ")
    return (username, password)


def enviar_requisicao(metodo, path, auth, dados=None):
    url = f"{BASE_URL}{path}"
    print("\n" + "-" * 50)
    print(f"Executando: {metodo} {url}")
    print("-" * 50 + "\n")

    try:
        if metodo == "GET":
            response = requests.get(
                url, auth=auth, headers=HEADERS, verify=False
            )
        elif metodo == "PUT":
            response = requests.put(
                url, auth=auth, headers=HEADERS, data=dados, verify=False
            )
        elif metodo == "POST":
            response = requests.post(
                url, auth=auth, headers=HEADERS, data=dados, verify=False
            )
        else:
            print("Método HTTP não suportado.")
            return

        print(f"Status Code: {response.status_code}")

        # Se houver conteúdo na resposta, tenta parsear como JSON para formatar bonito
        if response.text:
            try:
                print(json.dumps(response.json(), indent=2))
            except ValueError:
                print(response.text)
        else:
            print("Resposta vazia (Sucesso sem corpo de retorno).")

    except Exception as e:
        print(f"Erro ao conectar ou processar a requisição: {e}")

    input("\nPressione [ENTER] para voltar ao menu...")


def menu_folder_01(auth):
    while True:
        print("\n=== [01] Get Device Config ===")
        print("1) Get Device Config (Top Level) [Cisco-IOS-XE-native]")
        print("0) Voltar ao Menu Principal")
        opt = input("Escolha uma opção: ").strip()

        if opt == "1":
            enviar_requisicao(
                "GET", "/restconf/data/Cisco-IOS-XE-native:native/", auth
            )
        elif opt == "0":
            break
        else:
            print("Opção inválida!")


def menu_folder_02(auth):
    while True:
        print("\n=== [02] Get Physical Interface Information ===")
        print("1) Get GE1 Config (OpenConfig)")
        print("2) Get GE1 Config (Cisco Native)")
        print("3) Get GE1 Description (OpenConfig)")
        print("4) Get GE1 Description (Cisco Native)")
        print("0) Voltar ao Menu Principal")
        opt = input("Escolha uma opção: ").strip()

        if opt == "1":
            enviar_requisicao(
                "GET",
                "/restconf/data/openconfig-interfaces:interfaces/interface=GigabitEthernet1",
                auth,
            )
        elif opt == "2":
            enviar_requisicao(
                "GET",
                "/restconf/data/Cisco-IOS-XE-native:native/interface/GigabitEthernet=1",
                auth,
            )
        elif opt == "3":
            enviar_requisicao(
                "GET",
                "/restconf/data/openconfig-interfaces:interfaces/interface=GigabitEthernet1/config/description",
                auth,
            )
        elif opt == "4":
            enviar_requisicao(
                "GET",
                "/restconf/data/Cisco-IOS-XE-native:native/interface/GigabitEthernet=1/description",
                auth,
            )
        elif opt == "0":
            break
        else:
            print("Opção inválida!")


def menu_folder_03_05(auth):
    while True:
        print("\n=== Get / Validate Loopback Configuration ===")
        print("1) Get Loopback 100 Config (Cisco Native)")
        print("2) Get Loopback 101 Config (OpenConfig)")
        print("0) Voltar ao Menu Principal")
        opt = input("Escolha uma opção: ").strip()

        if opt == "1":
            enviar_requisicao(
                "GET",
                "/restconf/data/Cisco-IOS-XE-native:native/interface/Loopback=100",
                auth,
            )
        elif opt == "2":
            enviar_requisicao(
                "GET",
                "/restconf/data/openconfig-interfaces:interfaces/interface=Loopback101",
                auth,
            )
        elif opt == "0":
            break
        else:
            print("Opção inválida!")


def menu_folder_04(auth):
    while True:
        print("\n=== [04] Create Loopback Interface ===")
        print("1) Create Loopback 100 (Cisco Native - IP 192.0.2.100)")
        print("2) Create Loopback 101 (OpenConfig - IP 192.0.3.101)")
        print("0) Voltar ao Menu Principal")
        opt = input("Escolha uma opção: ").strip()

        if opt == "1":
            payload_cisco = {
                "Cisco-IOS-XE-native:Loopback": [
                    {
                        "name": 100,
                        "description": "Created via RESTCONF",
                        "ip": {
                            "address": {
                                "primary": {
                                    "address": "192.0.2.100",
                                    "mask": "255.255.255.255",
                                }
                            }
                        },
                    }
                ]
            }
            enviar_requisicao(
                "PUT",
                "/restconf/data/Cisco-IOS-XE-native:native/interface/Loopback=100",
                auth,
                dados=json.dumps(payload_cisco),
            )
        elif opt == "2":
            payload_oc = {
                "openconfig-interfaces:interface": [
                    {
                        "name": "Loopback101",
                        "config": {
                            "name": "Loopback101",
                            "type": "iana-if-type:softwareLoopback",
                            "enabled": True,
                            "description": "Configured via RESTCONF and OpenConfig models",
                        },
                        "subinterfaces": {
                            "subinterface": [
                                {
                                    "index": 0,
                                    "config": {
                                        "index": 0,
                                        "enabled": True,
                                        "description": "Configured via RESTCONF and OpenConfig models",
                                    },
                                    "openconfig-if-ip:ipv4": {
                                        "addresses": {
                                            "address": [
                                                {
                                                    "ip": "192.0.3.101",
                                                    "config": {
                                                        "ip": "192.0.3.101",
                                                        "prefix-length": 32,
                                                    },
                                                }
                                            ]
                                        }
                                    },
                                }
                            ]
                        },
                    }
                ]
            }
            enviar_requisicao(
                "PUT",
                "/restconf/data/openconfig-interfaces:interfaces/interface=Loopback101",
                auth,
                dados=json.dumps(payload_oc),
            )
        elif opt == "0":
            break
        else:
            print("Opção inválida!")


def main():
    username, password = solicitar_credenciais()
    # Tupla utilizada pelo 'requests' para autenticação HTTP Basic
    auth = (username, password)

    while True:
        print("\n" + "=" * 50)
        print("          MENU RESTCONF - CAT8000V (PYTHON)      ")
        print("=================================================")
        print("1) [01] Get Device Config")
        print("2) [02] Get Physical Interface Information")
        print("3) [03/05] Get / Validate Loopback Configuration")
        print("4) [04] Create Loopback Interface (PUT)")
        print("5) [06] Save Running Config to Startup (POST)")
        print("0) Sair")
        print("=" * 50)
        main_opt = input("Escolha uma pasta/ação: ").strip()

        if main_opt == "1":
            menu_folder_01(auth)
        elif main_opt == "2":
            menu_folder_02(auth)
        elif main_opt == "3":
            menu_folder_03_05(auth)
        elif main_opt == "4":
            menu_folder_04(auth)
        elif main_opt == "5":
            enviar_requisicao(
                "POST", "/restconf/operations/cisco-ia:save-config", auth, "{}"
            )
        elif main_opt == "0":
            print("Saindo...")
            sys.exit(0)
        else:
            print("Opção inválida!")


if __name__ == "__main__":
    main()