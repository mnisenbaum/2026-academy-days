import time
from netmiko import ConnectHandler, redispatch

# Definição de credenciais globais para o laboratório
USERNAME = 'admin'
PASSWORD = 'admin'
SECRET = 'enable_password'

# IP externo de gerenciamento do R1
R1_EXTERNAL_IP = '10.10.14.82'

# Dicionário focado na verificação (apenas IPs e flag de gateway)
topology_data = {
    'R1': {'ip': R1_EXTERNAL_IP, 'is_gateway': True},
    'R2': {'ip': '2.2.2.2', 'is_gateway': False},
    'R3': {'ip': '3.3.3.3', 'is_gateway': False},
    'R4': {'ip': '4.4.4.4', 'is_gateway': False}
}

# Comando de verificação escolhido
VERIFY_COMMAND = 'show interfaces description'

def run_verification():
    # Parâmetros de conexão base para o R1
    r1_device = {
        'device_type': 'cisco_ios',
        'host': topology_data['R1']['ip'],
        'username': USERNAME,
        'password': PASSWORD,
        'secret': SECRET,
        'global_delay_factor': 2, # Um pequeno delay ajuda na estabilidade de leituras
    }

    print("\n" + "#"*60)
    print(" INICIANDO AUDITORIA DE DESCRIÇÕES DE INTERFACES ".center(60, '#'))
    print("#"*60 + "\n")

    # ----------------------------------------------------
    # Passo 1: Verificar R1 diretamente
    # ----------------------------------------------------
    print(f"[*] Coletando dados do R1 ({R1_EXTERNAL_IP})...")
    net_connect = ConnectHandler(**r1_device)
    net_connect.enable()
    
    output_r1 = net_connect.send_command(VERIFY_COMMAND)
    net_connect.disconnect()
    
    print("-" * 60)
    print(f" SAÍDA R1 ".center(60))
    print("-" * 60)
    print(output_r1)
    print("-" * 60 + "\n")

    # ----------------------------------------------------
    # Passo 2: Verificar R2, R3 e R4 via Jump (R1)
    # ----------------------------------------------------
    for router_name, data in topology_data.items():
        if data['is_gateway']:
            continue
        
        print(f"[*] Coletando dados do {router_name} via salto pelo R1...")
        
        # Conecta no R1
        net_connect = ConnectHandler(**r1_device)
        net_connect.enable()
        
        # Inicia SSH para o roteador interno
        ssh_command = f"ssh -l {USERNAME} {data['ip']}\n"
        net_connect.write_channel(ssh_command)
        
        time.sleep(2)
        output = net_connect.read_channel()
        
        # Insere a senha se solicitado
        if "password" in output.lower() or "senha" in output.lower():
            net_connect.write_channel(f"{PASSWORD}\n")
            time.sleep(2)
        
        # Troca o contexto para o roteador de destino
        redispatch(net_connect, device_type='cisco_ios')
        net_connect.enable()
        
        # Executa o comando de verificação no roteador interno
        output_router = net_connect.send_command(VERIFY_COMMAND)
        net_connect.disconnect()
        
        # Imprime o resultado formatado
        print("-" * 60)
        print(f" SAÍDA {router_name} ".center(60))
        print("-" * 60)
        print(output_router)
        print("-" * 60 + "\n")

    print("#"*60)
    print(" AUDITORIA CONCLUÍDA ".center(60, '#'))
    print("#"*60 + "\n")

if __name__ == '__main__':
    run_verification()