import socket, sys, os, time

HOST = '127.0.0.1'  # endereço IP
PORT = 1999         # Porta utilizada pelo servidor
BUFFER_SIZE = 1460  # tamanho do buffer para recepção dos dados
WINDOW_SIZE = 5     # Tamanho da janela deslizante
TIMEOUT = 2         # Timeout para retransmissão (em segundos)

def main(argv):
    try:
        with socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM) as UDPClientSocket:
            UDPClientSocket.settimeout(TIMEOUT)

            # Solicitar lista de arquivos ao servidor
            UDPClientSocket.sendto("LIST".encode(), (HOST, PORT))

            # Receber lista de arquivos
            msgFromServer = UDPClientSocket.recvfrom(BUFFER_SIZE)
            arquivos = eval(msgFromServer[0].decode())

            print("\nLista de arquivos do servidor:\n")
            for indice, nome_arquivo in arquivos.items():
                print(f"{indice}: {nome_arquivo}")

            # Escolher arquivo para baixar
            opcao = input("\nDigite o índice do arquivo a ser baixado: ")
            UDPClientSocket.sendto(opcao.encode(), (HOST, PORT))

            opcao = int(opcao)
            file_name = arquivos[opcao]
            current_directory = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(current_directory, file_name)

            expected_sequence_number = 0
            received_data = {}
            packets_received = 0
            last_ack_sent = -1

            while True:
                try:
                    msgFromServer, _ = UDPClientSocket.recvfrom(BUFFER_SIZE)
                    sequence_number = msgFromServer[0]  # O primeiro byte é o número de sequência
                    data = msgFromServer[1:]  # O restante é o dado do arquivo

                    # Verificar se o pacote está dentro da janela
                    if expected_sequence_number <= sequence_number < expected_sequence_number + WINDOW_SIZE:
                        # Adiciona o pacote no buffer de dados
                        received_data[sequence_number] = data
                        packets_received += 1

                        # Enviar ACK de volta ao servidor
                        last_ack_sent = sequence_number
                        UDPClientSocket.sendto(f"ACK {sequence_number}".encode(), (HOST, PORT))

                        # Se o pacote atual for o esperado, incremente o número de sequência esperado
                        if sequence_number == expected_sequence_number:
                            expected_sequence_number += 1

                    # Detectar fim da transmissão (último pacote)
                    if len(data) < BUFFER_SIZE - 1:
                        break

                except socket.timeout:
                    # Se houver timeout, retransmitir o último ACK
                    if last_ack_sent >= 0:
                        UDPClientSocket.sendto(f"ACK {last_ack_sent}".encode(), (HOST, PORT))

            # Salvar o arquivo recebido
            with open(file_path, 'wb') as arquivo:
                for seq_num in sorted(received_data.keys()):
                    arquivo.write(received_data[seq_num])

            print(f"\nArquivo '{file_name}' baixado com sucesso!\n")

    except Exception as error:
        print("Exceção - Programa será encerrado!")
        print(error)

if __name__ == "__main__":   
    main(sys.argv[1:])
