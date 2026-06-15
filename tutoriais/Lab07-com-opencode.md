# Roteiro de Laboratório: Criação de Topologia CML2 via MCP

## 1. Objetivo

Criar um laboratório no Cisco Modeling Labs 2 (CML2) utilizando o protocolo MCP
(Model Context Protocol) com 4 roteadores IOL-XE em topologia quadrada,
endereçamento IPv4 10.x.y.0/24, loopbacks x.x.x.x/24 e OSPFv2 área 0.

## 2. Pré-requisitos

- Servidor CML2 acessível via HTTPS
- Cliente MCP (OpenCode, Claude Desktop, Cursor ou similar)
- Servidor MCP `cml-mcp` instalado e configurado
- `uv` (gerenciador de pacotes Python) instalado

## 3. Configuração do Servidor MCP

Configure o servidor MCP do CML2 no arquivo `opencode.json` (ou equivalente do
seu cliente):

```json
{
  "mcpServers": {
    "cml": {
      "command": "uvx",
      "args": ["cml-mcp[pyats]"],
      "env": {
        "CML_URL": "https://<CML_SERVER>",
        "CML_USERNAME": "<username>",
        "CML_PASSWORD": "<password>",
        "CML_VERIFY_SSL": "false",
        "PYATS_USERNAME": "<username>",
        "PYATS_PASSWORD": "<password>"
      }
    }
  }
}
```

Substitua os valores entre `< >` pelas credenciais do seu servidor CML2.

## 4. Prompt para o Agente de IA

```
Faça o planejamento da criação de um lab no CML2 via MCP

1. Criar um laboratório com o nome "opencode-MCP-externo"
2. Adicionar 4 routers IOL-xe formando os vértices de um quadrado
3. Conectar os roteadores de modo que os links são os vértices do quadrado
4. O endereçamento IP dos links será 10.x.y.0/24 onde x < y são os números
   dos roteadores conectados
5. Crie uma interface loopback em cada roteador com o endereço x.x.x.x/24
   onde x é o número do roteador
6. Levante o OSPF em todos os routers e anuncie todos links
```

## 5. Topologia

```
        R1 ──────────── R2
         │               │
         │               │
         │               │
        R4 ──────────── R3
```

### Endereçamento IP

| Link   | Sub-rede     | Roteador A | Roteador B |
|--------|--------------|------------|------------|
| R1-R2  | 10.1.2.0/24  | .1         | .2         |
| R2-R3  | 10.2.3.0/24  | .1         | .2         |
| R3-R4  | 10.3.4.0/24  | .1         | .2         |
| R4-R1  | 10.1.4.0/24  | .1         | .2         |

### Loopbacks

| Roteador | Loopback     |
|----------|--------------|
| R1       | 1.1.1.1/24   |
| R2       | 2.2.2.2/24   |
| R3       | 3.3.3.3/24   |
| R4       | 4.4.4.4/24   |

### Interfaceamento IOL-XE

Cada nó IOL-XE possui 4 interfaces Ethernet físicas por padrão (`Ethernet0/0`
a `Ethernet0/3`) mais uma `Loopback0`. Utilizamos:

- `Ethernet0/0` — primeiro link
- `Ethernet0/1` — segundo link

## 6. Ferramentas MCP Utilizadas

O servidor `cml-mcp` expõe 51 ferramentas. As utilizadas neste roteiro:

| Nº | Ferramenta MCP           | Descrição                     | Qtde |
|----|--------------------------|-------------------------------|------|
| 1  | `create_empty_lab`       | Criar laboratório vazio       | 1    |
| 2  | `add_node_to_cml_lab`    | Adicionar nó IOL-XE           | 4    |
| 3  | `add_interface_to_node`  | Criar interface física        | 8    |
| 4  | `get_interfaces_for_node`| Listar interfaces do nó       | 4    |
| 5  | `connect_two_nodes`      | Criar link entre interfaces   | 4    |
| 6  | `configure_cml_node`     | Aplicar startup config        | 4    |
| 7  | `start_cml_lab`          | Iniciar laboratório           | 1    |

**Total: 26 chamadas**

## 7. Sequência de Operações (REST API)

Abaixo, as chamadas REST equivalentes ao que as ferramentas MCP executam no
servidor CML2.

### 7.1 Criar laboratório

```
POST /api/v0/labs
{
  "title": "opencode-MCP-externo",
  "description": "Lab 4x iol-xe quadrado com OSPFv2"
}
```

### 7.2 Adicionar nós

```
POST /api/v0/labs/{lab_id}/nodes
{
  "label": "R1",
  "node_definition": "iol-xe",
  "image_definition": "iol-xe-17-18-02",
  "x": 100, "y": 100
}
```

Repetir para R2 (400,100), R3 (400,400), R4 (100,400).

### 7.3 Criar interfaces

```
POST /api/v0/labs/{lab_id}/interfaces
{ "node": "{node_id}", "slot": 0 }
```

Repetir para slot 1 em cada nó (8 chamadas).

### 7.4 Obter UUIDs das interfaces

```
GET /api/v0/labs/{lab_id}/nodes/{node_id}/interfaces?data=true
```

Mapear os UUIDs de `Ethernet0/0` e `Ethernet0/1` de cada nó.

### 7.5 Criar links

```
POST /api/v0/labs/{lab_id}/links
{ "src_int": "{id_R1_E0/0}", "dst_int": "{id_R2_E0/0}" }
```

| Link   | src_int           | dst_int           |
|--------|-------------------|-------------------|
| R1-R2  | R1 Ethernet0/0    | R2 Ethernet0/0    |
| R2-R3  | R2 Ethernet0/1    | R3 Ethernet0/0    |
| R3-R4  | R3 Ethernet0/1    | R4 Ethernet0/0    |
| R4-R1  | R4 Ethernet0/1    | R1 Ethernet0/1    |

### 7.6 Aplicar configurações

```
PATCH /api/v0/labs/{lab_id}/nodes/{node_id}
{ "configuration": "..." }
```

Configurações completas na seção 8.

### 7.7 Iniciar laboratório

```
PUT /api/v0/labs/{lab_id}/start
```

## 8. Configurações dos Roteadores

### R1

```
hostname R1
!
interface Loopback0
 ip address 1.1.1.1 255.255.255.0
 ip ospf 1 area 0
!
interface Ethernet0/0
 ip address 10.1.2.1 255.255.255.0
 ip ospf 1 area 0
 no shutdown
!
interface Ethernet0/1
 ip address 10.1.4.1 255.255.255.0
 ip ospf 1 area 0
 no shutdown
!
router ospf 1
 router-id 1.1.1.1
 passive-interface Loopback0
 network 1.1.1.0 0.0.0.255 area 0
 network 10.1.2.0 0.0.0.255 area 0
 network 10.1.4.0 0.0.0.255 area 0
!
end
```

### R2

```
hostname R2
!
interface Loopback0
 ip address 2.2.2.2 255.255.255.0
 ip ospf 1 area 0
!
interface Ethernet0/0
 ip address 10.1.2.2 255.255.255.0
 ip ospf 1 area 0
 no shutdown
!
interface Ethernet0/1
 ip address 10.2.3.1 255.255.255.0
 ip ospf 1 area 0
 no shutdown
!
router ospf 1
 router-id 2.2.2.2
 passive-interface Loopback0
 network 2.2.2.0 0.0.0.255 area 0
 network 10.1.2.0 0.0.0.255 area 0
 network 10.2.3.0 0.0.0.255 area 0
!
end
```

### R3

```
hostname R3
!
interface Loopback0
 ip address 3.3.3.3 255.255.255.0
 ip ospf 1 area 0
!
interface Ethernet0/0
 ip address 10.2.3.2 255.255.255.0
 ip ospf 1 area 0
 no shutdown
!
interface Ethernet0/1
 ip address 10.3.4.1 255.255.255.0
 ip ospf 1 area 0
 no shutdown
!
router ospf 1
 router-id 3.3.3.3
 passive-interface Loopback0
 network 3.3.3.0 0.0.0.255 area 0
 network 10.2.3.0 0.0.0.255 area 0
 network 10.3.4.0 0.0.0.255 area 0
!
end
```

### R4

```
hostname R4
!
interface Loopback0
 ip address 4.4.4.4 255.255.255.0
 ip ospf 1 area 0
!
interface Ethernet0/0
 ip address 10.3.4.2 255.255.255.0
 ip ospf 1 area 0
 no shutdown
!
interface Ethernet0/1
 ip address 10.1.4.2 255.255.255.0
 ip ospf 1 area 0
 no shutdown
!
router ospf 1
 router-id 4.4.4.4
 passive-interface Loopback0
 network 4.4.4.0 0.0.0.255 area 0
 network 10.3.4.0 0.0.0.255 area 0
 network 10.1.4.0 0.0.0.255 area 0
!
end
```

## 9. Verificação

Após o lab iniciar e convergir, os seguintes comandos podem ser executados via
pyATS ou console para validar:

```
show ip ospf neighbor
show ip route ospf
show ip interface brief
ping 2.2.2.2 source 1.1.1.1
```

## 10. Limpeza

Para remover o laboratório:

```
DELETE /api/v0/labs/{lab_id}
```

Ou via ferramenta MCP: `delete_cml_lab`.
