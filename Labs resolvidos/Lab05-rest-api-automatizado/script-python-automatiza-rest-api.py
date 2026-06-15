import requests
import urllib3
import getpass
import json
import time

# Desativa os avisos de certificado SSL autoassinado (comum em laboratórios/sandboxes)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def exibir_cabecalho():
    print("=" * 58)
    print("    Configuração de Acesso RESTCONF - Cisco Cat8k    ")
    print("=" * 58)

def coletar_credenciais():
    host = input("Endereço IP ou Hostname (ex: 44.201.40.38): ").strip()
    port = input("Porta (ex: 443): ").strip()
    user = input("Usuário: ").strip()
    # getpass oculta os caracteres enquanto o usuário digita a senha
    password = getpass.getpass("Senha: ")
    print("\n" + "=" * 58 + "\n")
    
    base_url = f"https://{host}:{port}"
    return base_url, user, password

def tratar_resposta(response):
    """Função auxiliar para tratar e imprimir as respostas da API."""
    print(f"Status Code: {response.status_code}")
    
    # Se a resposta tiver conteúdo e for 200 OK ou 201 Created
    if response.status_code in [200, 201] and response.text:
        try:
            dados = response.json()
            # Imprime o JSON formatado e indentado
            print(json.dumps(dados, indent=4))
        except ValueError:
            print("Resposta não é um JSON válido.")
    elif response.status_code == 204:
        print("Sucesso! (Sem conteúdo retornado / 204 No Content).")
    else:
        print("Falha ou resposta inesperada:")
        print(response.text)
    print("-" * 58)

def restconf_get(base_url, credenciais, path):
    url = f"{base_url}{path}"
    headers = {
        "Accept": "application/yang-data+json"
    }
    print(f"\nExecutando GET em: {path}")
    
    # verify=False substitui a flag -k do curl
    # auth=credenciais aplica o Basic Auth automaticamente
    response = requests.get(url, headers=headers, auth=credenciais, verify=False)
    tratar_resposta(response)

def restconf_put(base_url, credenciais, path, payload):
    url = f"{base_url}{path}"
    headers = {
        "Content-Type": "application/yang-data+json",
        "Accept": "application/yang-data+json"
    }
    print(f"\nExecutando PUT em: {path}")
    
    response = requests.put(url, headers=headers, auth=credenciais, data=json.dumps(payload), verify=False)
    tratar_resposta(response)

def restconf_post(base_url, credenciais, path, payload):
    url = f"{base_url}{path}"
    headers = {
        "Content-Type": "application/yang-data+json",
        "Accept": "application/yang-data+json"
    }
    print(f"\nExecutando POST em: {path}")
    
    response = requests.post(url, headers=headers, auth=credenciais, data=json.dumps(payload), verify=False)
    tratar_resposta(response)

def main():
    exibir_cabecalho()
    base_url, user, password = coletar_credenciais()
    credenciais = (user, password) # Tupla exigida pelo módulo requests para Basic Auth

    while True:
        print("\n" + "=" * 58)
        print("                      MENU DEVNET                         ")
        print("=" * 58)
        print("1. Obter Configuração Global (Cisco-IOS-XE-native)")
        print("2. Obter Configuração GigabitEthernet1 (Native)")
        print("3. Obter Configuração GigabitEthernet1 (OpenConfig)")
        print("4. Criar Interface Loopback 100 (Native)")
        print("5. Criar Interface Loopback 101 (OpenConfig)")
        print("6. Obter Configuração Loopback 100 (Native)")
        print("7. Obter Configuração Loopback 101 (OpenConfig)")
        print("8. Salvar Running-Config para Startup-Config (Operação)")
        print("9. Sair")
        print("=" * 58)
        
        opcao = input("Escolha uma opção [1-9]: ").strip()

        if opcao == '1':
            restconf_get(base_url, credenciais, "/restconf/data/Cisco-IOS-XE-native:native/")
            
        elif opcao == '2':
            restconf_get(base_url, credenciais, "/restconf/data/Cisco-IOS-XE-native:native/interface/GigabitEthernet=1")
            
        elif opcao == '3':
            restconf_get(base_url, credenciais, "/restconf/data/openconfig-interfaces:interfaces/interface=GigabitEthernet1")
            
        elif opcao == '4':
            payload_native = {
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
            restconf_put(base_url, credenciais, "/restconf/data/Cisco-IOS-XE-native:native/interface/Loopback=100", payload_native)
            
        elif opcao == '5':
            payload_oc = {
              "openconfig-interfaces:interface": [
                {
                  "name": "Loopback101",
                  "config": {
                    "name": "Loopback101",
                    "type": "iana-if-type:softwareLoopback",
                    "enabled": True, # Note a diferença: em Python usamos True com T maiúsculo
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
            restconf_put(base_url, credenciais, "/restconf/data/openconfig-interfaces:interfaces/interface=Loopback101", payload_oc)
            
        elif opcao == '6':
            restconf_get(base_url, credenciais, "/restconf/data/Cisco-IOS-XE-native:native/interface/Loopback=100")
            
        elif opcao == '7':
            restconf_get(base_url, credenciais, "/restconf/data/openconfig-interfaces:interfaces/interface=Loopback101")
            
        elif opcao == '8':
            restconf_post(base_url, credenciais, "/restconf/operations/cisco-ia:save-config", {})
            
        elif opcao == '9':
            print("\nEncerrando o script...")
            break
            
        else:
            print("\nOpção inválida. Tente novamente.")
            
        input("\nPressione ENTER para continuar...")

if __name__ == "__main__":
    main()