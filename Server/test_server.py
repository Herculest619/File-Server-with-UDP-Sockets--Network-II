import socket, sys, os, random, time

HOST = '127.0.0.1'  # endereço IP
PORT = 1999         # Porta utilizada pelo servidor
BUFFER_SIZE = 1460  # tamanho do buffer para recepção dos dados
WINDOW_SIZE = 5     # Tamanho da janela deslizante
TIMEOUT = 2         # Timeout para esperar ACKs (em segundos)

def main(argv):
    try:
        UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        UDPServerSocket.bind((HOST, PORT))
        print("\nServidor UDP ativo e aguardando conexões")

        while True:
            bytesAddressPair = UDPServerSocket.recvfrom(BUFFER_SIZE)
            endereco = bytesAddressPair[1]
            print(f"\nCliente conectado: {endereco}")

            # Listar arquivos disponíveis
            caminho_atual = os.path.dirname(os.path.abspath(__file__))
            arquivos = os.listdir(caminho_atual)
            arquivos = [arquivo for arquivo in arquivos if arquivo != 'Server_teste.py']
            arquivos = {i: arquivo for i, arquivo in enumerate(arquivos)}
            print("\nArquivos disponíveis: ")
            print(arquivos)

            # Enviar lista de arquivos ao cliente
            UDPServerSocket.sendto(str(arquivos).encode(), endereco)

            # Receber opção do cliente
            bytesAddressPair = UDPServerSocket.recvfrom(BUFFER_SIZE)
            opcao = int(bytesAddressPair[0].decode())
            print("\nOpção escolhida pelo cliente: ", opcao)

            arquivo = arquivos[opcao]
            caminho_arquivo = os.path.join(caminho_atual, arquivo)
            print("\nCaminho do arquivo: ", caminho_arquivo)

            with open(caminho_arquivo, 'rb') as file:
                seq_num = 0
                window_start = 0
                packets_in_window = {}

                # Carregar pacotes na janela deslizante
                while True:
                    # Enviar pacotes dentro da janela
                    while seq_num < window_start + WINDOW_SIZE:
                        dados = file.read(BUFFER_SIZE - 1)  # Ler dados do arquivo
                        if not dados:
                            break  # Fim do arquivo

                        # Contagem circular de sequência
                        seq_num = seq_num % 256

                        # Criar pacote com número de sequência
                        packet = bytes([seq_num]) + dados

                        # Simular perda de pacotes (95% de sucesso)
                        if random.random() < 0.95:
                            UDPServerSocket.sendto(packet, endereco)
                            print(f"Enviando pacote {seq_num}")
                        else:
                            print(f"Pacote {seq_num} perdido")

                        packets_in_window[seq_num] = packet
                        seq_num += 1

                    # Esperar por ACKs dentro da janela
                    try:
                        UDPServerSocket.settimeout(TIMEOUT)
                        ack_from_client, _ = UDPServerSocket.recvfrom(BUFFER_SIZE)
                        ack_num = int(ack_from_client.decode().split()[1])
                        print(f"ACK recebido: {ack_num}")

                        # Atualizar janela apenas se o ACK for maior ou igual ao início da janela
                        if ack_num >= window_start:
                            # Mover a janela para o próximo pacote a ser enviado
                            window_start = ack_num + 1
                            print(f"Movendo janela: {window_start} - {window_start + WINDOW_SIZE - 1}")

                            # Remover pacotes reconhecidos da janela
                            packets_in_window = {k: v for k, v in packets_in_window.items() if k > ack_num}

                    except socket.timeout:
                        # Retransmitir pacotes não reconhecidos (dentro da janela)
                        print("Timeout - Retransmitindo pacotes na janela")
                        for i in range(window_start, min(window_start + WINDOW_SIZE, seq_num)):
                            if i in packets_in_window:
                                UDPServerSocket.sendto(packets_in_window[i], endereco)
                                print(f"Retransmitindo pacote {i}")

                    if not dados and len(packets_in_window) == 0:
                        break  # Fim da transmissão quando todos os pacotes forem enviados e recebidos

            print("\nArquivo enviado com sucesso!!")

    except Exception as error:
        print("Erro na execução do servidor!!")
        print(error)

if __name__ == "__main__":   
    main(sys.argv[1:])
