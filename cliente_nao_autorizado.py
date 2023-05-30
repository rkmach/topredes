import socket
import ssl

# define o endereço IP do servidor e a porta a ser usada
HOST = '127.0.0.1'
PORT = 65105

# path = os.path.dirname(os.path.abspath(__file__))
# certificate_path = os.path.join(path, 'cert.pem')
# keyfile_path = os.path.join(path, 'key.pem')

# cria um socket do tipo AF_INET (IPv4) e SOCK_STREAM (TCP)
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    # conecta-se ao servidor
    s.connect((HOST, PORT))
    # configura o contexto SSL/TLS do cliente
    # ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    # ssl_context.load_verify_locations(certificate_path)

    # # faz o handshake SSL/TLS com o servidor
    # ssl_conn = ssl_context.wrap_socket(s, server_hostname=HOST)
    

    #----
    # Fazer a aplicação cliente pegar input da entrada padrão, e enviar para o servidor
    while 1:
        try:
            command = input("Por favor, digite um comando:\n")
            # envia comando para o servidor
            s.sendall(command.encode())
            if command == 'Adeus':
                break
            # espera resposta do servidor
            received_data = s.recv(1024)
            print(f'Mensagem recebida do servidor: {received_data.decode()}')
        except KeyboardInterrupt:
            break
        except ssl.SSLError:
            print("Erro: Você não apresentou seu certificado. A comunicação não prosseguirá!")
            break
    
    print(f'Processo cliente encerrado!!')
