import socket
import ssl
import os
from server_handler import handle, get_current_db
import json

# define o endereço IP do servidor e a porta a ser usada
HOST = '127.0.0.1'
PORT = 65105

path = os.path.dirname(os.path.abspath(__file__))
certificate_path = os.path.join(path, 'cert.pem')
keyfile_path = os.path.join(path, 'key.pem')
json_path = os.path.join(path, 'data.json')
client_certificate = os.path.join(path, 'client.crt')
client_key = os.path.join(path, 'client.key')


# cria um socket do tipo AF_INET (IPv4) e SOCK_STREAM (TCP)
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as data_socket:
    # associa o socket ao endereço e porta especificados
    data_socket.bind((HOST, PORT))
    
    # coloca o socket em modo de escuta
    data_socket.listen()
    print(f'Servidor esperando conexão em {HOST}:{PORT}...')
    
    # espera por uma conexão
    conn, addr = data_socket.accept()
    with conn:
        # conexão estabelecida!
        print('Conexão estabelecida por', addr)
        
        # configura o contexto SSL/TLS do servidor
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.verify_mode = ssl.CERT_REQUIRED
        ssl_context.load_cert_chain(certificate_path, keyfile_path)
        ssl_context.load_verify_locations(cafile=client_certificate)
        
        # faz o handshake SSL/TLS com o cliente
        try:
            ssl_conn = ssl_context.wrap_socket(conn, server_side=True)
        except ssl.SSLError:
            print("Erro: O cliente não apresentou seu certificado. A comunicação não prosseguirá!")
            exit()
        
        # espera por uma mensagem do cliente
        data = ssl_conn.recv(1024)
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
            ssl_conn.sendall(code.encode())
            
            bd = get_current_db()
            ssl_conn.sendall(bd.encode())
            
            # espera por uma mensagem do cliente
            data = ssl_conn.recv(1024)
        
        print("Encerrando processo servidor!!")
