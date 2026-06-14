#!/bin/bash

# Configurações básicas do ambiente Sandbox DevNet
HOSTNAME="devnetsandboxiosxec8k.cisco.com"
PORT="443"
BASE_URL="https://${HOSTNAME}:${PORT}"

# Cabeçalhos padrão para RESTCONF
HEADERS=(
  -H "Content-Type: application/yang-data+json"
  -H "Accept: application/yang-data+json"
)

# Solicitação de credenciais ao usuário
echo "=== Conexão RESTCONF Cisco Catalyst 8000V (DevNet Sandbox) ==="
read -p "Digite o usuário (padrão: npe-restconf): " USERNAME
USERNAME=${USERNAME:-"npe-restconf"}

# Lê a senha de forma oculta
read -s -p "Digite a senha: " PASSWORD
echo ""

AUTH_USER="${USERNAME}:${PASSWORD}"

# Função auxiliar para exibir a resposta do curl formatada
enviar_requisicao() {
  local metodo=$1
  local path=$2
  local dados=$3

  echo -e "\n----------------------------------------"
  echo -e "Executando: $metodo $BASE_URL$path"
  echo -e "----------------------------------------\n"

  if [ "$metodo" == "GET" ]; then
    curl -s -k -X GET "${BASE_URL}${path}" -u "$AUTH_USER" "${HEADERS[@]}" | python3 -m json.tool
  elif [ "$metodo" == "POST" ] || [ "$metodo" == "PUT" ]; then
    curl -s -k -X "$metodo" "${BASE_URL}${path}" -u "$AUTH_USER" "${HEADERS[@]}" -d "$dados" | python3 -m json.tool
  fi

  echo -e "\nPressione [ENTER] para voltar ao menu..."
  read -r
}

# Submenu: 01 - Get Device Config
menu_folder_01() {
  while true; do
    clear
    echo "=== [01] Get Device Config ==="
    echo "1) Get Device Config (Top Level) [Cisco-IOS-XE-native]"
    echo "0) Voltar ao Menu Principal"
    read -p "Escolha uma opção: " opt

    case $opt in
      1) enviar_requisicao "GET" "/restconf/data/Cisco-IOS-XE-native:native/" ;;
      0) break ;;
      *) echo "Opção inválida!"; sleep 1 ;;
    esac
  done
}

# Submenu: 02 - Get Physical Interface Information
menu_folder_02() {
  while true; do
    clear
    echo "=== [02] Get Physical Interface Information ==="
    echo "1) Get GE1 Config (OpenConfig)"
    echo "2) Get GE1 Config (Cisco Native)"
    echo "3) Get GE1 Description (OpenConfig)"
    echo "4) Get GE1 Description (Cisco Native)"
    echo "0) Voltar ao Menu Principal"
    read -p "Escolha uma opção: " opt

    case $opt in
      1) enviar_requisicao "GET" "/restconf/data/openconfig-interfaces:interfaces/interface=GigabitEthernet1" ;;
      2) enviar_requisicao "GET" "/restconf/data/Cisco-IOS-XE-native:native/interface/GigabitEthernet=1" ;;
      3) enviar_requisicao "GET" "/restconf/data/openconfig-interfaces:interfaces/interface=GigabitEthernet1/config/description" ;;
      4) enviar_requisicao "GET" "/restconf/data/Cisco-IOS-XE-native:native/interface/GigabitEthernet=1/description" ;;
      0) break ;;
      *) echo "Opção inválida!"; sleep 1 ;;
    esac
  done
}

# Submenu: 03 & 05 - Get/Validate Loopback
menu_folder_03_05() {
  while true; do
    clear
    echo "=== Get / Validate Loopback Configuration ==="
    echo "1) Get Loopback 100 Config (Cisco Native)"
    echo "2) Get Loopback 101 Config (OpenConfig)"
    echo "0) Voltar ao Menu Principal"
    read -p "Escolha uma opção: " opt

    case $opt in
      1) enviar_requisicao "GET" "/restconf/data/Cisco-IOS-XE-native:native/interface/Loopback=100" ;;
      2) enviar_requisicao "GET" "/restconf/data/openconfig-interfaces:interfaces/interface=Loopback101" ;;
      0) break ;;
      *) echo "Opção inválida!"; sleep 1 ;;
    esac
  done
}

# Submenu: 04 - Create Loopback Interface
menu_folder_04() {
  while true; do
    clear
    echo "=== [04] Create Loopback Interface ==="
    echo "1) Create Loopback 100 (Cisco Native - IP 192.0.2.100)"
    echo "2) Create Loopback 101 (OpenConfig - IP 192.0.3.101)"
    echo "0) Voltar ao Menu Principal"
    read -p "Escolha uma opção: " opt

    case $opt in
      1)
        PAYLOAD_CISCO='{"Cisco-IOS-XE-native:Loopback":[{"name":100,"description":"Created via RESTCONF","ip":{"address":{"primary":{"address":"192.0.2.100","mask":"255.255.255.255"}}}}]}'
        enviar_requisicao "PUT" "/restconf/data/Cisco-IOS-XE-native:native/interface/Loopback=100" "$PAYLOAD_CISCO"
        ;;
      2)
        PAYLOAD_OC='{"openconfig-interfaces:interface":[{"name":"Loopback101","config":{"name":"Loopback101","type":"iana-if-type:softwareLoopback","enabled":true,"description":"Configured via RESTCONF and OpenConfig models"},"subinterfaces":{"subinterface":[{"index":0,"config":{"index":0,"enabled":true,"description":"Configured via RESTCONF and OpenConfig models"},"openconfig-if-ip:ipv4":{"addresses":{"address":[{"ip":"192.0.3.101","config":{"ip":"192.0.3.101","prefix-length":32}}]}}}]}}]}'
        enviar_requisicao "PUT" "/restconf/data/openconfig-interfaces:interfaces/interface=Loopback101" "$PAYLOAD_OC"
        ;;
      0) break ;;
      *) echo "Opção inválida!"; sleep 1 ;;
    esac
  done
}

# Menu Principal
while true; do
  clear
  echo "================================================="
  echo "          MENU RESTCONF - CAT8000V               "
  echo "================================================="
  echo "1) [01] Get Device Config"
  echo "2) [02] Get Physical Interface Information"
  echo "3) [03/05] Get / Validate Loopback Configuration"
  echo "4) [04] Create Loopback Interface (PUT)"
  echo "5) [06] Save Running Config to Startup (POST)"
  echo "0) Sair"
  echo "================================================="
  read -p "Escolha uma pasta/ação: " main_opt

  case $main_opt in
    1) menu_folder_01 ;;
    2) menu_folder_02 ;;
    3) menu_folder_03_05 ;;
    4) menu_folder_04 ;;
    5) enviar_requisicao "POST" "/restconf/operations/cisco-ia:save-config" "{}" ;;
    0) echo "Saindo..."; exit 0 ;;
    *) echo "Opção inválida!"; sleep 1 ;;
  esac
done