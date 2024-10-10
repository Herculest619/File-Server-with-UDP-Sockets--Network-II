import socket, sys, os, random
from threading import Thread

HOST = '127.0.0.1'  # endereço IP
PORT = 1999         # Porta utilizada pelo servidor
BUFFER_SIZE = 1460  # tamanho do buffer para recepção dos dados
WINDOW_SIZE = 5     # Tamanho da janela deslizante

def enviar_pacotes(UDPServerSocket, endereco, caminho_arquivo):
    with open(caminho_arquivo, 'rb') as file:
        base = 0
        next_seq_num = 0
        pacotes = []
        acked = set()

        # Ler arquivo e criar pacotes
        while True:
            dados = file.read(BUFFER_SIZE)
            if not dados:
                break
            pacotes.append(dados)

        total_pacotes = len(pacotes)

        # Transmissão com janela deslizante
        while base < total_pacotes:
            # Envia pacotes dentro da janela
            while next_seq_num < base + WINDOW_SIZE and next_seq_num < total_pacotes:
                # Simula a chance de perda de 5%
                if random.random() > 0.05:  # 95% de chance de enviar o pacote
                    UDPServerSocket.sendto(pacotes[next_seq_num], endereco)
                    print(f"Enviando pacote {next_seq_num}")
                else:
                    print(f"Perda do pacote {next_seq_num} simulada")
                
                next_seq_num += 1

            try:
                # Espera pelo ACK
                UDPServerSocket.settimeout(2.0)  # Timeout de 2 segundos
                ack_data, _ = UDPServerSocket.recvfrom(BUFFER_SIZE)
                ack_num = int(ack_data.decode())
                print(f"ACK recebido: {ack_num}")
                if ack_num >= base:
                    base = ack_num + 1  # Mover base da janela

            except socket.timeout:
                print("Timeout - Retransmitindo pacotes na janela")
                next_seq_num = base  # Retransmite pacotes não reconhecidos

        # Envia pacote de término
        UDPServerSocket.sendto(b"END_OF_TRANSMISSION", endereco)
        print("Transmissão concluída - Enviando pacote de término.")

def main(argv):
    try:
        UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        UDPServerSocket.bind((HOST, PORT))  # Escuta na porta especificada
        print("\nUDP server up and listening")

        while True:
            try:
                # Recebe mensagem do cliente
                UDPServerSocket.settimeout(None)  # Desativa o timeout para novas conexões
                bytesAddressPair = UDPServerSocket.recvfrom(BUFFER_SIZE)
                endereco = bytesAddressPair[1]
                print("\nConectado ao cliente:", endereco)

                caminho_atual = os.path.dirname(os.path.abspath(__file__))
                arquivos = os.listdir(caminho_atual)
                arquivos = [arquivo for arquivo in arquivos if arquivo != 'Server.py']
                arquivos = {i: arquivo for i, arquivo in enumerate(arquivos)}

                print("\nArquivos disponíveis: ", arquivos)
                UDPServerSocket.sendto(str(arquivos).encode(), endereco)

                # Recebe a opção do cliente
                bytesAddressPair = UDPServerSocket.recvfrom(BUFFER_SIZE)
                opcao = int(bytesAddressPair[0].decode())

                arquivo = arquivos[opcao]
                caminho_arquivo = os.path.join(caminho_atual, arquivo)
                print(f"\nEnviando arquivo: {arquivo}")

                # Enviar pacotes usando janela deslizante
                enviar_pacotes(UDPServerSocket, endereco, caminho_arquivo)

            except socket.timeout:
                print("Timeout - Nenhuma nova conexão recebida.")
                continue  # Reinicia o loop para aguardar novas conexões

    except Exception as error:
        print("Erro na execução do servidor!!")
        print(error)

if __name__ == "__main__":   
    main(sys.argv[1:])
