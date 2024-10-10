import socket, sys, os, time

HOST = '127.0.0.1'  # endereço IP
PORT = 1999         # Porta utilizada pelo servidor
BUFFER_SIZE = 1460  # tamanho do buffer para recepção dos dados
WINDOW_SIZE = 5     # Tamanho da janela deslizante

def receber_arquivo(UDPClientSocket, file_path):
    with open(file_path, 'wb') as arquivo:
        expected_seq_num = 0

        while True:
            msgFromServer = UDPClientSocket.recvfrom(BUFFER_SIZE)
            dados = msgFromServer[0]

            # Verifica se é o pacote de término
            if dados == b"END_OF_TRANSMISSION":
                print("Pacote de término recebido. Transmissão completa.")
                break

            # Escreve os dados no arquivo
            arquivo.write(dados)
            #print(f"Pacote {expected_seq_num} recebido")

            # Envia ACK
            UDPClientSocket.sendto(str(expected_seq_num).encode(), (HOST, PORT))
            #print(f"ACK enviado: {expected_seq_num}")
            expected_seq_num += 1

def main(argv):
    try:
        with socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM) as UDPClientSocket:
            UDPClientSocket.sendto("texto".encode(), (HOST, PORT))

            msgFromServer = UDPClientSocket.recvfrom(BUFFER_SIZE)
            arquivos = eval(msgFromServer[0].decode())

            print("\nLista de arquivos do servidor:")
            for indice, nome_arquivo in arquivos.items():
                print(f"{indice}: {nome_arquivo}")

            opcao = input("\nDigite o índice do arquivo a ser baixado: ")
            UDPClientSocket.sendto(opcao.encode(), (HOST, PORT))

            opcao = int(opcao)
            file_name = arquivos[opcao]
            current_directory = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(current_directory, file_name)

            receber_arquivo(UDPClientSocket, file_path)

            print(f"\nArquivo '{file_name}' baixado com sucesso!\n")

    except Exception as error:
        print("Exceção - Reconectando ao servidor...")
        print(error)
        # Espera 1 segundo para tentar rodar o programa novamente
        time.sleep(1)
        # Limapa a tela
        os.system('cls' if os.name == 'nt' else 'clear')
        main(argv)

if __name__ == "__main__":
    main(sys.argv[1:])
