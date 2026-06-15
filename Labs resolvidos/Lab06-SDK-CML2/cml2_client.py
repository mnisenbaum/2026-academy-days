from virl2_client import ClientLibrary

URL = "https://10.10.14.121/"
USERNAME = "admin"
PASSWORD = "Cml2@123"

client = ClientLibrary(
    url=URL,
    username=USERNAME,
    password=PASSWORD,
    ssl_verify=False,
)

info = client.system_info()
print(f"Conectado ao CML2 v{info['version']}  (ready={info['ready']})")
print()

labs = client.all_labs()
if labs:
    print(f"{'ID':<40} {'Título':<30} {'Estado':<10}")
    print("-" * 80)
    for lab in labs:
        estado = "running" if lab.state == "STARTED" else "stopped"
        print(f"{lab.id:<40} {lab.title:<30} {estado:<10}")
else:
    print("Nenhum lab encontrado.")
