import json
import requests
import urllib3

# Desabilita avisos de certificados SSL autoassinados comuns em ambientes de lab
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_credentials():
    """Coleta as informações do roteador com os valores padrão do arquivo Bruno."""
    print("--- Configurações do Roteador (RESTCONF) ---")
    hostname = input("Hostname/IP [Padrão: 44.201.40.38]: ").strip() or "44.201.40.38"
    port = input("Porta [Padrão: 443]: ").strip() or "443"
    username = input("Usuário [Padrão: npe-restconf]: ").strip() or "npe-restconf"
    password = input("Senha [Padrão: C1sco12345]: ").strip() or "C1sco12345"
    
    base_url = f"https://{hostname}:{port}"
    return base_url, (username, password)

def execute_request(method, url, auth, body=None):
    """Executa a chamada HTTP e exibe os detalhes da requisição e da resposta."""
    headers = {
        "Content-Type": "application/yang-data+json",
        "Accept": "application/yang-data+json"
    }
    
    print("\n" + "="*60)
    print(f">> EFETUANDO CHAMADA API:")
    print(f"Método: {method}")
    print(f"URL   : {url}")
    if body:
        print(f"Body  :\n{json.dumps(body, indent=2)}")
    else:
        print("Body  : None")
    print("="*60)

    try:
        if method == "GET":
            response = requests.get(url, auth=auth, headers=headers, verify=False)
        elif method == "PUT":
            response = requests.put(url, auth=auth, headers=headers, json=body, verify=False)
        elif method == "POST":
            response = requests.post(url, auth=auth, headers=headers, json=body, verify=False)
        else:
            print(f"Método {method} não suportado.")
            return

        print(f"\n<< RESPOSTA (Status Code: {response.status_code})")
        if response.text:
            try:
                # Tenta formatar como JSON se a resposta contiver dados
                print(json.dumps(response.json(), indent=2))
            except ValueError:
                print(response.text)
        else:
            print("[Sem corpo de resposta - Operação concluída com sucesso]")
            
    except Exception as e:
        print(f"Erro ao conectar ou processar a requisição: {e}")
    
    print("="*60 + "\n")
    input("Pressione Enter para voltar ao menu...")

def main():
    base_url, auth = get_credentials()
    
    # Mapeamento do menu baseado fielmente na estrutura do arquivo JSON do Bruno
    menu_options = {
        # Pasta 01
        "1": {
            "name": "Get Device Config (Top Level) [Cisco Native]",
            "method": "GET",
            "path": "/restconf/data/Cisco-IOS-XE-native:native/",
            "body": None
        },
        # Pasta 02
        "2": {
            "name": "Get GE1 Config (OpenConfig)",
            "method": "GET",
            "path": "/restconf/data/openconfig-interfaces:interfaces/interface=GigabitEthernet1",
            "body": None
        },
        "3": {
            "name": "Get GE1 Config [Cisco Native]",
            "method": "GET",
            "path": "/restconf/data/Cisco-IOS-XE-native:native/interface/GigabitEthernet=1",
            "body": None
        },
        "4": {
            "name": "Get GE1 Description (OpenConfig)",
            "method": "GET",
            "path": "/restconf/data/openconfig-interfaces:interfaces/interface=GigabitEthernet1/config/description",
            "body": None
        },
        "5": {
            "name": "Get GE1 Description [Cisco Native]",
            "method": "GET",
            "path": "/restconf/data/Cisco-IOS-XE-native:native/interface/GigabitEthernet=1/description",
            "body": None
        },
        # Pasta 03
        "6": {
            "name": "Get Loopback 101 Config (OpenConfig)",
            "method": "GET",
            "path": "/restconf/data/openconfig-interfaces:interfaces/interface=Loopback101",
            "body": None
        },
        "7": {
            "name": "Get Loopback 100 Config [Cisco Native]",
            "method": "GET",
            "path": "/restconf/data/Cisco-IOS-XE-native:native/interface/Loopback=100",
            "body": None
        },
        # Pasta 04
        "8": {
            "name": "Create Loopback 101 (OpenConfig)",
            "method": "PUT",
            "path": "/restconf/data/openconfig-interfaces:interfaces/interface=Loopback101",
            "body": {
                "openconfig-interfaces:interface": [
                    {
                        "name": "Loopback101",
                        "config": {
                            "name": "Loopback101",
                            "type": "iana-if-type:softwareLoopback",
                            "enabled": True,
                            "description": "Configured via RESTCONF and OpenConfig models"
                        },
                        "subinterfaces": {
                            "subinterface": [
                                {
                                    "index": 0,
                                    "config": {
                                        "index": 0,
                                        "enabled": True,
                                        "description": "Configured via RESTCONF and OpenConfig models"
                                    },
                                    "openconfig-if-ip:ipv4": {
                                        "addresses": {
                                            "address": [
                                                {
                                                    "ip": "192.0.3.101",
                                                    "config": {
                                                        "ip": "192.0.3.101",
                                                        "prefix-length": 32
                                                    }
                                                }
                                            ]
                                        }
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        },
        "9": {
            "name": "Create Loopback 100 [Cisco Native]",
            "method": "PUT",
            "path": "/restconf/data/Cisco-IOS-XE-native:native/interface/Loopback=100",
            "body": {
                "Cisco-IOS-XE-native:Loopback": [
                    {
                        "name": 100,
                        "description": "Created via RESTCONF",
                        "ip": {
                            "address": {
                                "primary": {
                                    "address": "192.0.2.100",
                                    "mask": "255.255.255.255"
                                }
                            }
                        }
                    }
                ]
            }
        },
        # Pasta 06
        "10": {
            "name": "Save Running Config to Startup (cisco-ia:save-config)",
            "method": "POST",
            "path": "/restconf/operations/cisco-ia:save-config",
            "body": {}
        }
    }

    while True:
        print("\n" + "="*45)
        print("         MENU RESTCONF - CAT8000V")
        print("="*45)
        print("[01 - Get Device Config]")
        print("  1. Get Device Config (Top Level)")
        print("[02 - Get Physical Interface Information]")
        print("  2. Get GE1 Config (OpenConfig)")
        print("  3. Get GE1 Config (Cisco Native)")
        print("  4. Get GE1 Description (OpenConfig)")
        print("  5. Get GE1 Description (Cisco Native)")
        print("[03 / 05 - Get & Validate Loopbacks]")
        print("  6. Get Loopback 101 Config (OpenConfig)")
        print("  7. Get Loopback 100 Config (Cisco Native)")
        print("[04 - Create Interfaces]")
        print("  8. Create Loopback 101 (OpenConfig)")
        print("  9. Create Loopback 100 (Cisco Native)")
        print("[06 - Maintenance]")
        print("  10. Save Running Config to Startup")
        print("-"*45)
        print("  0. Sair")
        print("="*45)
        
        choice = input("Escolha uma opção: ").strip()
        
        if choice == "0":
            print("Saindo... Até logo!")
            break
        elif choice in menu_options:
            opt = menu_options[choice]
            target_url = f"{base_url}{opt['path']}"
            execute_request(opt["method"], target_url, auth, opt["body"])
        else:
            print("Opção inválida! Tente novamente.")

if __name__ == "__main__":
    main()