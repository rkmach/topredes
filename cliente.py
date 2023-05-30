import socket
import ssl
import os
from rich.console import Console
from rich.markdown import Markdown

# define o endereço IP do servidor e a porta a ser usada

# a rede 127.0.0.0 é usada para testes de loopback, ou seja, usada para que o dispositivo 
# se comunique consigo mesmo através da pilha TCP/IP

path = os.path.dirname(os.path.abspath(__file__))
certificate_path = os.path.join(path, 'cert.pem')
keyfile_path = os.path.join(path, 'key.pem')
client_certificate = os.path.join(path, 'client.crt')
client_key = os.path.join(path, 'client.key')

c = Console()

usage = """
# Modo de Usar:

Esse é um cliente de um servidor que guarda informações sobre o paradigma chave-valor (KVS).  
Os comandos para consultar, adicionar, remover ou atualizar um par chave-valor serão mostrados a seguir. 

--- 

## Adicionar:
$> adicionar chave valor  
$> adicionar chave valor0,valor1,valor2,...

---

## Alterar:
$> alterar chave valor  
$> alterar chave valor0,valor1,valor2,...  
$> alterar chave valor valor_atualizado

---

## Remover:
$> remover chave  
$> remover chave valor0,valor1,valor2,...

---

## Consultar:
$> consultar

---
"""

c.print(Markdown(usage, justify='center'))

ip = '127.0.0.1'
port = 65105

# cria um socket do tipo AF_INET (IPv4) e SOCK_STREAM (TCP)
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    # conecta-se ao servidor
    s.connect((ip, port))
    # configura o contexto SSL/TLS do cliente
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ssl_context.load_verify_locations(certificate_path)
    ssl_context.load_cert_chain(client_certificate, client_key)
    # faz o handshake SSL/TLS com o servidor
    ssl_conn = ssl_context.wrap_socket(s, server_hostname=ip)
    
    
    #----
    # Fazer a aplicação cliente pegar input da entrada padrão, e enviar para o servidor
    while 1:
        try:
            c.rule('Digite um comando. As opções são: [green]adicionar[/], [blue]alterar[/], [red]remover[/] ou [yellow]consultar[/]')
            command = input('->')
            # envia comando para o servidor
            ssl_conn.sendall(command.encode())
            
            # Se o comando for 'Adeus', encerra o processo
            if command == 'Adeus':
                break
            
            # o servidor envia duas mensagens por vez, a primeira é uma string (código) dizendo se a operação funcionou
            # e a segunda é o próprio banco de dados atualizado
            
            # espera resposta do servidor sobre o código
            code_data = ssl_conn.recv()
            # espera resposta do servidor sobre o banco de dados
            bd_data = ssl_conn.recv()
            
            # imprime a string que contém o código, bem como o banco de dados atualizado
            c.print('[white on blue reverse bold] Mensagem recebida do servidor:[/]')
            c.rule('[white on blue bold] Código de resposta e estado do banco de dados correntemente:[/]')
            c.print(code_data.decode())
            c.print_json(bd_data.decode())
            
        except KeyboardInterrupt:
            # Ctrl^C termina o processo
            break
    
    print('Processo cliente encerrado!!')
