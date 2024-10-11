import socket
import sys
import os

HOST = '127.0.0.1'  # endereço IP
PORT = 1999        # Porta utilizada pelo servidor
BUFFER_SIZE = 1460  # tamanho do buffer para recepção dos dados

def main(argv):
    try:
        # Cria o socket UDP
        with socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM) as UDPClientSocket:
            UDPClientSocket.sendto("LIST".encode(), (HOST, PORT))  # Solicita a lista de arquivos

            msgFromServer = UDPClientSocket.recvfrom(BUFFER_SIZE)  # Recebe a mensagem do servidor
            msg = msgFromServer[0].decode()  # Decodifica a mensagem recebida para uma string

            arquivos = eval(msg)  # Converte a string de volta para um dicionário

            # Formata a mensagem de forma legível
            print("\nLista de arquivos do servidor:\n")
            for indice, nome_arquivo in arquivos.items():
                print(f"{indice}: {nome_arquivo}")  # Exibe o índice e o nome do arquivo, um por linha

            # Recebe o índice do arquivo a ser baixado
            opcao = input("\nDigite o índice do arquivo a ser baixado: ")
            UDPClientSocket.sendto(opcao.encode(), (HOST, PORT))

            # Recebe o arquivo, ele virá em partes devido ao tamanho do buffer de 1460 bytes
            opcao = int(opcao)
            file_name = arquivos[opcao]
            current_directory = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(current_directory, file_name)

            with open(file_path, 'wb') as arquivo:
                while True:
                    msgFromServer = UDPClientSocket.recvfrom(BUFFER_SIZE)
                    data = msgFromServer[0]
                    arquivo.write(data)

                    # Envia um ACK para o servidor
                    UDPClientSocket.sendto("ACK".encode(), (HOST, PORT))

                    if len(data) < BUFFER_SIZE:
                        break
            print(f"\nArquivo '{file_name}' baixado com sucesso!\n")

    except Exception as error:
        print("Exceção - Programa será encerrado!")
        print(error)
        return

if __name__ == "__main__":
    main(sys.argv[1:])
