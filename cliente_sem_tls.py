import socket
from rich.console import Console

# define o endereço IP do servidor e a porta a ser usada
HOST = '127.0.0.1'
PORT = 65105

c = Console()

# cria um socket do tipo AF_INET (IPv4) e SOCK_STREAM (TCP)
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    # conecta-se ao servidor
    s.connect((HOST, PORT))

    #----
    # Fazer a aplicação cliente pegar input da entrada padrão, e enviar para o servidor
    while 1:
        try:
            c.rule('Digite um comando. As opções são: [green]adicionar[/], [blue]alterar[/], [red]remover[/] ou [yellow]consultar[/]')
            command = input('->')
            # envia comando para o servidor
            s.sendall(command.encode())
            
            # Se o comando for 'Adeus', encerra o processo
            if command == 'Adeus':
                break
            
            # o servidor envia duas mensagens por vez, a primeira é uma string (código) dizendo se a operação funcionou
            # e a segunda é o próprio banco de dados atualizado
            
            # espera resposta do servidor sobre o código
            code_data = s.recv(1024)
            # espera resposta do servidor sobre o banco de dados
            bd_data = s.recv(1024)
            
            # imprime a string que contém o código, bem como o banco de dados atualizado
            c.print('[white on blue reverse bold] Mensagem recebida do servidor:[/]')
            c.rule('[white on blue bold] Código de resposta e estado do banco de dados correntemente:[/]')
            c.print(code_data.decode())
            c.print_json(bd_data.decode())
            
        except KeyboardInterrupt:
            # Ctrl^C termina o processo
            break
        except ConnectionResetError:
            c.print('[red] O servidor não aceitou a conexão por você não apresentar seu certificado SSL[/]')
            exit()
