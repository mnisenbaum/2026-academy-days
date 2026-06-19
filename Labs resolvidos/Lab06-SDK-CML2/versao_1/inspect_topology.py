from virl2_client import ClientLibrary

client = ClientLibrary("https://10.10.14.121", "admin", "Cml2@123", ssl_verify=False)
lab = client.join_existing_lab("17e2d11d-7a5c-4dc6-bfa0-11f44127a82a")

for l in lab.links():
    ifaces = l.interfaces
    n1 = ifaces[0].node.label
    i1 = ifaces[0].label
    n2 = ifaces[1].node.label
    i2 = ifaces[1].label
    print(f"Link: {n1}:{i1} <-> {n2}:{i2}")
