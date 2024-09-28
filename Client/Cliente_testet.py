import socket, sys
import os

HOST = '127.0.0.1'  # endereço IP
PORT = 1999         # Porta utilizada pelo servidor
BUFFER_SIZE = 1460  # tamanho do buffer para recepção dos dados
WINDOW_SIZE = 5     # Tamanho da janela deslizante

def main(argv): 
    try:
        with socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM) as UDPClientSocket:
            UDPClientSocket.sendto("texto".encode(), (HOST, PORT))

            msgFromServer = UDPClientSocket.recvfrom(BUFFER_SIZE)
            msg = msgFromServer[0].decode()

            arquivos = eval(msg)

            print("\nLista de arquivos do servidor:"+ "\n")
            for indice, nome_arquivo in arquivos.items():
                print(f"{indice}: {nome_arquivo}")

            opcao = input("\nDigite o índice do arquivo a ser baixado: ")
            UDPClientSocket.sendto(opcao.encode(), (HOST, PORT))

            opcao = int(opcao)
            file_name = arquivos[opcao]
            current_directory = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(current_directory, file_name)

            expected_sequence_number = 0
            packets_received = 0
            received_data = []

            while True:
                msgFromServer, _ = UDPClientSocket.recvfrom(BUFFER_SIZE)
                sequence_number = msgFromServer[0]  # O primeiro byte é o número de sequência
                data = msgFromServer[1:]  # O restante é o dado do arquivo

                # Contagem circular para número de sequência
                if sequence_number == expected_sequence_number % 256:
                    received_data.append(data)
                    packets_received += 1
                    expected_sequence_number += 1

                    # Enviar ACK de volta ao servidor
                    UDPClientSocket.sendto(f"ACK {sequence_number}".encode(), (HOST, PORT))

                if len(data) < BUFFER_SIZE - 1:
                    break  # Último pacote

            # Salvar o arquivo recebido
            with open(file_path, 'wb') as arquivo:
                for data in received_data:
                    arquivo.write(data)

            print(f"\nArquivo '{file_name}' baixado com sucesso!\n")

    except Exception as error:
        print("Exceção - Programa será encerrado!")
        print(error)

if __name__ == "__main__":   
    main(sys.argv[1:])
