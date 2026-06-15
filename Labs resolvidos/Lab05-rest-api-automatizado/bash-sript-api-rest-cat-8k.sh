#!/bin/bash

# ==========================================
# Automação RESTCONF - Cisco Catalyst 8000V
# ==========================================

# Coleta de informações de acesso
echo "=========================================================="
echo "    Configuração de Acesso RESTCONF - Cisco Cat8k"
echo "=========================================================="
read -p "Endereço IP ou Hostname (ex: 44.201.40.38): " HOST
read -p "Porta (ex: 443): " PORT
read -p "Usuário: " USER
read -s -p "Senha: " PASS
echo -e "\n==========================================================\n"

# Função base para realizar as requisições GET
function restconf_get() {
    local url_path=$1
    echo "Executando GET em: $url_path"
    curl -s -k -u "$USER:$PASS" \
         -X GET "https://$HOST:$PORT$url_path" \
         -H "Accept: application/yang-data+json" | jq .
}

# Função base para realizar requisições PUT (Modificações)
function restconf_put() {
    local url_path=$1
    local payload=$2
    echo "Executando PUT em: $url_path"
    curl -s -k -u "$USER:$PASS" \
         -X PUT "https://$HOST:$PORT$url_path" \
         -H "Content-Type: application/yang-data+json" \
         -H "Accept: application/yang-data+json" \
         -d "$payload"
    echo -e "\nComando enviado. Verifique o status acima (vazio = sucesso no PUT)."
}

# Função base para realizar requisições POST (Ações/Operações)
function restconf_post() {
    local url_path=$1
    local payload=$2
    echo "Executando POST em: $url_path"
    curl -s -k -u "$USER:$PASS" \
         -X POST "https://$HOST:$PORT$url_path" \
         -H "Content-Type: application/yang-data+json" \
         -H "Accept: application/yang-data+json" \
         -d "$payload" | jq .
}

# Loop do Menu Interativo
while true; do
    echo " "
    echo "=========================================================="
    echo "                      MENU DEVNET                         "
    echo "=========================================================="
    echo "1. Obter Configuração Global (Cisco-IOS-XE-native)"
    echo "2. Obter Configuração GigabitEthernet1 (Native)"
    echo "3. Obter Configuração GigabitEthernet1 (OpenConfig)"
    echo "4. Criar Interface Loopback 100 (Native)"
    echo "5. Criar Interface Loopback 101 (OpenConfig)"
    echo "6. Obter Configuração Loopback 100 (Native)"
    echo "7. Obter Configuração Loopback 101 (OpenConfig)"
    echo "8. Salvar Running-Config para Startup-Config (Operação)"
    echo "9. Sair"
    echo "=========================================================="
    read -p "Escolha uma opção [1-9]: " OPCAO

    case $OPCAO in
        1)
            restconf_get "/restconf/data/Cisco-IOS-XE-native:native/"
            ;;
        2)
            restconf_get "/restconf/data/Cisco-IOS-XE-native:native/interface/GigabitEthernet=1"
            ;;
        3)
            restconf_get "/restconf/data/openconfig-interfaces:interfaces/interface=GigabitEthernet1"
            ;;
        4)
            PAYLOAD_NATIVE='{
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
            }'
            restconf_put "/restconf/data/Cisco-IOS-XE-native:native/interface/Loopback=100" "$PAYLOAD_NATIVE"
            ;;
        5)
            PAYLOAD_OC='{
              "openconfig-interfaces:interface": [
                {
                  "name": "Loopback101",
                  "config": {
                    "name": "Loopback101",
                    "type": "iana-if-type:softwareLoopback",
                    "enabled": true,
                    "description": "Configured via RESTCONF and OpenConfig models"
                  },
                  "subinterfaces": {
                    "subinterface": [
                      {
                        "index": 0,
                        "config": {
                          "index": 0,
                          "enabled": true,
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
            }'
            restconf_put "/restconf/data/openconfig-interfaces:interfaces/interface=Loopback101" "$PAYLOAD_OC"
            ;;
        6)
            restconf_get "/restconf/data/Cisco-IOS-XE-native:native/interface/Loopback=100"
            ;;
        7)
            restconf_get "/restconf/data/openconfig-interfaces:interfaces/interface=Loopback101"
            ;;
        8)
            restconf_post "/restconf/operations/cisco-ia:save-config" "{}"
            ;;
        9)
            echo "Encerrando o script..."
            exit 0
            ;;
        *)
            echo "Opção inválida. Tente novamente."
            ;;
    esac
    
    # Pausa antes de retornar ao menu para permitir a leitura do resultado
    echo ""
    read -n 1 -s -r -p "Pressione qualquer tecla para continuar..."
done