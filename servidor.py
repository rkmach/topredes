import socket
import ssl
import os
from server_handler import handle, get_current_db
import json
from threading import Thread, Lock

clients = set()
clients_lock = Lock()

path = os.path.dirname(os.path.abspath(__file__))
certificate_path = os.path.join(path, 'cert.pem')
keyfile_path = os.path.join(path, 'key.pem')
json_path = os.path.join(path, 'data.json')
client_certificate = os.path.join(path, 'client.crt')
client_key = os.path.join(path, 'client.key')


def handle_request(tls_data_socket):
    # Essa função é executada por uma thread
    with tls_data_socket:
        with clients_lock:
            # adiciona a conexão ao conjunto de conexões abertas
            clients.add(tls_data_socket)

        # espera por uma mensagem do cliente
        data = tls_data_socket.recv(1024)
        while data != b'Adeus':
            
            # conexão com o banco de dados
            f = open(json_path, 'r+')
            # `db` eh um dicionário
            try:
                db = json.load(f)
            except Exception:
                print("Erro ao acessar o banco de dados")
                exit()
            
            # tratamento do comando enviado pelo cliente
            return_code = handle(data, f, db)
            f.close()
            
            # elabora a resposta do cliente, mostrando o codigo de retorno e a situação atual do banco de dados
            # envia a resposta para o cliente
            code = f'Código: {return_code}'
            tls_data_socket.sendall(code.encode())
            
            bd = get_current_db()
            tls_data_socket.sendall(bd.encode())
            
            # espera por uma mensagem do cliente
            data = tls_data_socket.recv(1024)
            
        with clients_lock:
            # remove a conexão do conjunto de conexões abertas
            clients.remove(tls_data_socket)
            # fecha a conexão
            tls_data_socket.close()

# define o endereço IP do servidor e a porta a ser usada
ip = '127.0.0.1'
port = 65105

# cria um socket do tipo AF_INET (IPv4) e SOCK_STREAM (TCP)
listerner_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# associa o socket ao endereço e porta especificados
listerner_sock.bind((ip, port))

# coloca o socket em modo de escuta
listerner_sock.listen()
print(f'Servidor esperando conexão em {ip}:{port}...')

# configura o contexto SSL/TLS do servidor
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.verify_mode = ssl.CERT_REQUIRED
ssl_context.load_cert_chain(certificate_path, keyfile_path)
ssl_context.load_verify_locations(cafile=client_certificate)


import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--unsafe', action='store_true',
                    help='Um booleano que define se a conexão ocorrerá com ou sem TLS')

args = parser.parse_args()

if not args.unsafe:
    try:
        # "Embrulha" o socket com o TLS
        tls_listerner_sock = ssl_context.wrap_socket(listerner_sock, server_side=True)
    except ssl.SSLError:
        print("Erro: O cliente não apresentou seu certificado. A comunicação não prosseguirá!")

while 1:
    # espera por uma conexão, então faz o handshake SSL/TLS com o cliente
    try:
        if args.unsafe:
            unsafe_data_socket, addr = listerner_sock.accept()
        else:
            tls_data_socket, addr = tls_listerner_sock.accept()
    except ssl.SSLError:
        print("Erro: O cliente não apresentou seu certificado. A comunicação não prosseguirá!")
        continue
    
    # conexão estabelecida!
    print('Conexão estabelecida por', addr)
    # Toda vez que uma nova conexão é estabelecida, cria uma thread para cuidar do socket referente a essa comunicação
    if not args.unsafe:
        Thread(target=handle_request, args=(tls_data_socket,)).start()
    else:
        Thread(target=handle_request, args=(unsafe_data_socket,)).start()
