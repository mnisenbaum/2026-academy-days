import time
from netmiko import ConnectHandler, redispatch

# Definição de credenciais globais para o laboratório (ajuste conforme necessário)
USERNAME = 'admin'
PASSWORD = 'admin'
SECRET = 'enable_password'

# IP externo de gerenciamento do R1 (Interface e0/2) - ATUALIZADO
R1_EXTERNAL_IP = '10.10.14.82'

# Dicionário estruturado com os dados de destino e comandos de configuração
topology_data = {
    'R1': {
        'ip': R1_EXTERNAL_IP,
        'is_gateway': True,
        'commands': [
            'interface Loopback0',
            'description Loopback Principal - R1',
            'interface Ethernet0/0',
            'description Link de Conexao para R2',
            'interface Ethernet0/1',
            'description Link de Conexao para R4',
            'interface Ethernet0/2',
            'description Interface de Acesso Externo (Gerenciamento)'
        ]
    },
    'R2': {
        'ip': '2.2.2.2',  # Acessível via OSPF a partir de R1
        'is_gateway': False,
        'commands': [
            'interface Loopback0',
            'description Loopback Principal - R2',
            'interface Ethernet0/0',
            'description Link de Conexao para R1',
            'interface Ethernet0/1',
            'description Link de Conexao para R3'
        ]
    },
    'R3': {
        'ip': '3.3.3.3',  # Acessível via OSPF a partir de R1
        'is_gateway': False,
        'commands': [
            'interface Loopback0',
            'description Loopback Principal - R3',
            'interface Ethernet0/0',
            'description Link de Conexao para R4',
            'interface Ethernet0/1',
            'description Link de Conexao para R2'
        ]
    },
    'R4': {
        'ip': '4.4.4.4',  # Acessível via OSPF a partir de R1
        'is_gateway': False,
        'commands': [
            'interface Loopback0',
            'description Loopback Principal - R4',
            'interface Ethernet0/0',
            'description Link de Conexao para R3',
            'interface Ethernet0/1',
            'description Link de Conexao para R1'
        ]
    }
}

def run_configuration():
    # Parâmetros de conexão base para o R1
    r1_device = {
        'device_type': 'cisco_ios',
        'host': topology_data['R1']['ip'],
        'username': USERNAME,
        'password': PASSWORD,
        'secret': SECRET,
    }

    # ----------------------------------------------------
    # Passo 1: Configurar as descrições no próprio R1
    # ----------------------------------------------------
    print("=== Conectando diretamente ao R1 ===")
    net_connect = ConnectHandler(**r1_device)
    net_connect.enable()
    
    print("Aplicando descrições de interface no R1...")
    net_connect.send_config_set(topology_data['R1']['commands'])
    net_connect.disconnect()
    print("R1 configurado com sucesso e desconectado.\n")

    # ----------------------------------------------------
    # Passo 2: Configurar R2, R3 e R4 saltando por dentro de R1
    # ----------------------------------------------------
    for router_name, data in topology_data.items():
        if data['is_gateway']:
            continue  # Pula o R1 pois já foi configurado
        
        print(f"=== Iniciando processo para o {router_name} ===")
        print(f"Conectando ao Gateway (R1) para iniciar o salto para o IP {data['ip']}...")
        
        # Abre nova conexão com o R1 para servir de rota de salto
        net_connect = ConnectHandler(**r1_device)
        net_connect.enable()
        
        # Dispara o comando SSH de dentro do prompt do R1 para o roteador interno
        ssh_command = f"ssh -l {USERNAME} {data['ip']}\n"
        net_connect.write_channel(ssh_command)
        
        # Aguarda a resposta do canal para capturar a solicitação de credenciais
        time.sleep(2)
        output = net_connect.read_channel()
        
        # Trata o envio da senha se o prompt interno solicitar
        if "password" in output.lower() or "senha" in output.lower():
            net_connect.write_channel(f"{PASSWORD}\n")
            time.sleep(2)
        
        # Altera o contexto do Netmiko de R1 para o roteador de destino interno (Redispatch)
        redispatch(net_connect, device_type='cisco_ios')
        
        print(f"Sessão SSH estabelecida com sucesso no {router_name}!")
        net_connect.enable()
        
        print(f"Enviando comandos de descrição de interface para o {router_name}...")
        net_connect.send_config_set(data['commands'])
        
        # Fecha a sessão
        net_connect.disconnect()
        print(f"{router_name} configurado e sessão encerrada com sucesso.\n")

if __name__ == '__main__':
    run_configuration()