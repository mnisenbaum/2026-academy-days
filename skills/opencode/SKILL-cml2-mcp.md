---
name: cml2-mcp
description: >-
  Gerenciar laboratórios de rede no Cisco Modeling Labs 2 (CML2) via MCP —
  criar, configurar e iniciar labs com roteadores, switches e links
license: MIT
compatibility: opencode
metadata:
  audience: network-engineers
  source: cml2-mcp-opencode-guide
---

## Quando usar

Use esta skill quando o usuário pedir para criar, modificar, inspecionar ou
gerenciar laboratórios de rede no Cisco Modeling Labs 2 (CML2), incluindo
tarefas como adicionar roteadores, conectar interfaces, aplicar configurações
de startup ou iniciar/parar labs.

## Pré-requisito

O servidor MCP `cml-mcp` deve estar configurado no `opencode.jsonc` com o
campo `"environment"` (NÃO `"env"`) contendo `CML_URL`, `CML_USERNAME`,
`CML_PASSWORD` e `CML_VERIFY_SSL`. Verifique com `opencode mcp list` se o
status é "connected". Se não estiver disponível, avise o usuário e oriente
a configuração.

## Ferramentas MCP disponíveis

### Laboratórios
- `get_cml_labs()` — lista todos os labs
- `get_cml_lab_by_title(title)` — busca lab por título exato
- `create_empty_lab(title, description?)` — cria lab vazio, retorna UUID
- `modify_cml_lab(lab_id, title?, description?)` — altera título/descrição
- `create_full_lab_topology(lab_id, topology)` — importa topologia JSON/YAML
- `clone_cml_lab(lab_id, title?)` — clona lab existente
- `start_cml_lab(lab_id)` — inicializa todos os nós
- `stop_cml_lab(lab_id)` — para todos os nós
- `wipe_cml_lab(lab_id)` — limpa dados dos nós
- `delete_cml_lab(lab_id)` — remove o lab
- `download_lab_topology(lab_id)` — exporta topologia como YAML
- `set_cml_lab_permissions(lab_id, groups?, users?)` — permissões

### Nós
- `get_nodes_for_cml_lab(lab_id)` — lista nós do lab
- `add_node_to_cml_lab(lab_id, node_definition, label, x, y)` — adiciona nó
- `configure_cml_node(lab_id, node_id, config)` — aplica startup config
- `start_cml_node(lab_id, node_id)` — inicia nó específico
- `stop_cml_node(lab_id, node_id)` — para nó específico
- `wipe_cml_node(lab_id, node_id)` — limpa disco do nó
- `delete_cml_node(lab_id, node_id)` — remove nó

### Interfaces e Links
- `get_interfaces_for_node(lab_id, node_id)` — lista interfaces
- `add_interface_to_node(lab_id, node_id, slot, type, label?)`
- `connect_two_nodes(lab_id, src_int, dst_int)` — cria link
- `get_all_links_for_lab(lab_id)` — lista links do lab
- `apply_link_conditioning(lab_id, link_id, latency?, loss?, jitter?)`
- `start_cml_link(lab_id, link_id)` — ativa link
- `stop_cml_link(lab_id, link_id)` — desativa link

### Descoberta
- `get_cml_node_definitions()` — lista tipos de nós disponíveis (iosv, csr1000v, etc.)
- `get_node_definition_detail(node_definition)` — detalhes de um tipo de nó

## Fluxo típico

Ao criar um laboratório do zero, siga esta sequência:

1. **Criar lab** → `create_empty_lab(title="...")` → guardar `lab_id`
2. **Descoberta** (se necessário) → `get_cml_node_definitions()` para ver tipos disponíveis
3. **Adicionar nós** → `add_node_to_cml_lab(lab_id, node_definition="iosv", label="R1", x, y)` para cada nó
4. **Ver interfaces** → `get_interfaces_for_node(lab_id, node_id)` nos nós adicionados
5. **Conectar** → `connect_two_nodes(lab_id, src_int_id, dst_int_id)` para cada link
6. **Configurar** → `configure_cml_node(lab_id, node_id, config="...")` com a config desejada
7. **Iniciar** → `start_cml_lab(lab_id)`

## Exemplo de diálogo

**Usuário:** "Crie um lab com 2 roteadores IOSv chamados R1 e R2, conecte a Gi0/0 de um na Gi0/0 do outro, aplique configurações OSPF e inicie o lab."

**Sequência de tools:**
```
1. create_empty_lab(title="Lab OSPF")
2. get_cml_node_definitions()
3. add_node_to_cml_lab(lab_id, "iosv", "R1", 0, 0)
4. add_node_to_cml_lab(lab_id, "iosv", "R2", 200, 0)
5. get_interfaces_for_node(lab_id, r1_id)
6. get_interfaces_for_node(lab_id, r2_id)
7. connect_two_nodes(lab_id, r1_g0_0, r2_g0_0)
8. configure_cml_node(lab_id, r1_id, config="...")
9. configure_cml_node(lab_id, r2_id, config="...")
10. start_cml_lab(lab_id)
```

## Troubleshooting

| Sintoma | Causa | Solução |
|---------|-------|---------|
| MCP server "error" ou "disconnected" | `"env"` em vez de `"environment"` no config | Corrigir campo no `opencode.jsonc` |
| Timeout ao conectar | CML2 lento ou timeout padrão (5s) pequeno | Adicionar `"timeout": 15000` |
| `CML_URL not set` | Variáveis de ambiente não passadas | Verificar se campo é `"environment"` |
| `401 Unauthorized` | Credenciais erradas | Verificar `CML_USERNAME` e `CML_PASSWORD` |
| SSL Error | Certificado auto-assinado | Usar `"CML_VERIFY_SSL": "false"` |

## Notas importantes

- O campo de configuração no `opencode.jsonc` chama-se **`"environment"`** (NÃO `"env"`) — este foi o bug crítico descoberto durante a implementação
- `CML_URL` deve ser a URL base do servidor CML2 **sem** `/api/v0` no final
- Para certificados auto-assinados, use `"CML_VERIFY_SSL": "false"`
- O servidor `cml-mcp` roda em modo `stdio` (não HTTP) — comunicando via JSON-RPC 2.0
