import urllib3
from virl2_client import ClientLibrary

# Desabilita avisos de certificado SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CML_URL = "https://10.10.14.121/"
CML_USER = "admin"
CML_PASS = "Cml2@123"

def main():
    print("Conectando ao CML2 para listar as imagens disponíveis...\n")
    client = ClientLibrary(CML_URL, CML_USER, CML_PASS, ssl_verify=False)
    
    # Captura a resposta bruta do servidor
    definitions = client.definitions.node_definitions()
    
    print(f"{'ID (Use no seu script)':<25} | {'Label (Nome Amigável)':<30}")
    print("-" * 60)
    
    for node in definitions:
        # Extrai os dados tratando estritamente como dicionário puro
        node_id = node.get("id", "N/A")
        
        # O label geralmente fica dentro de uma subchave 'ui'
        ui_data = node.get("ui", {})
        label = ui_data.get("label", "N/A") if isinstance(ui_data, dict) else "N/A"
        
        print(f"{node_id:<25} | {label:<30}")

if __name__ == "__main__":
    main()