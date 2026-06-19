## Lab 01

```
Instruções: 1) Links: 10.x.y.0/24 onde x < y são os número dos roteadores 2) Loopback: x.x.x.x/32 onde x é o número do routeador 3) OSPFv2 area 0 em todos links

```


```
Você é um especialista cisco ganhador de vários premios, e um execlente professor. Esta é uma topologia do CML2. Crie os scripts de configuração de todos roteadores para sere copiados e colados na "Config" deles. Siga as orientações do texto da tela
```

# Lab 02

```
en 
conf t 
ip domain name cisco.com 
crypto key gen rsa mod 2048 
ip ssh version 2 
user admin priv 15 secret admin 
line vty 0 4 
transport input ssh 
login local 
end 
wr
```

```
Tenho essa topologia com o endereçamento IP conforme as instruções. Conseguimos acessar o R1 usando o ip: 10.10.14.69 Credenciais: admin / admin com priv 15. Todos os roteadores têm as mesmas credenciais e devem ser acessados via loopback 2.2.2.2 (R2), 3.3.3.3 (R3), etc. Crie um script python usando a biblioteca Netmiko que configure as "descriptions" de todas interfaces de todos roteadores. Para isso, acesse R1 por SSH, de R1 acesse R2, de R2 acesse R3 e de R3 acesse R4. A descrição deverá seguir o modelo: "Link de Rx para Ry" ou "Loopback de Rx"
Ficou alguma dúvida?
```