import socket, sys, os, random

HOST = '127.0.0.1'  # endereço IP
PORT = 1999         # Porta utilizada pelo servidor
BUFFER_SIZE = 1460  # tamanho do buffer para recepção dos dados
WINDOW_SIZE = 5     # Tamanho da janela deslizante

def main(argv):
    try:
        UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        UDPServerSocket.bind((HOST, PORT))
        print("\nUDP server up and listening")

        while True:
            bytesAddressPair = UDPServerSocket.recvfrom(BUFFER_SIZE)
            endereco = bytesAddressPair[1]
            print(f"\nClient IP Address: {endereco}")

            caminho_atual = os.path.dirname(os.path.abspath(__file__))
            arquivos = os.listdir(caminho_atual)
            arquivos = [arquivo for arquivo in arquivos if arquivo != 'Server_teste.py']
            arquivos = {i: arquivo for i, arquivo in enumerate(arquivos)}
            print("\nArquivos disponíveis: ")
            print(arquivos)

            UDPServerSocket.sendto(str(arquivos).encode(), endereco)

            bytesAddressPair = UDPServerSocket.recvfrom(BUFFER_SIZE)
            opcao = int(bytesAddressPair[0].decode())
            print("\nOpção escolhida pelo cliente: ", opcao)

            arquivo = arquivos[opcao]
            caminho_arquivo = os.path.join(caminho_atual, arquivo)
            print("\nCaminho do arquivo: ", caminho_arquivo)

            with open(caminho_arquivo, 'rb') as file:
                seq_num = 0
                while True:
                    dados = file.read(BUFFER_SIZE - 1)  # Ler dados, garantindo que o pacote não exceda o BUFFER_SIZE
                    if not dados:
                        break

                    # Contagem circular de sequência
                    seq_num = seq_num % 256

                    # Enviar pacote com número de sequência
                    packet = bytes([seq_num]) + dados  # Inclui o número de sequência como um byte
                    # Simula perda de pacotes, sucesso de 95%
                    if random.random() < 0.95:
                        UDPServerSocket.sendto(packet, endereco)
                        print(f"Enviando pacote {seq_num}")
                    else:
                        print(f"Pacote {seq_num} perdido")
                    seq_num += 1

                    # Espera por ACK do cliente
                    ack_from_client, _ = UDPServerSocket.recvfrom(BUFFER_SIZE)
                    ack_num = int(ack_from_client.decode().split()[1])
                    print(f"ACK recebido: {ack_num}")

            print("\nArquivo enviado com sucesso!!")

    except Exception as error:
        print("Erro na execução do servidor!!")
        print(error)        

if __name__ == "__main__":   
    main(sys.argv[1:])
