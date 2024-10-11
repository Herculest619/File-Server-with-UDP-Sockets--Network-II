import socket, sys, os, random
from threading import Thread, Timer

HOST = '127.0.0.1'
PORT = 1999
BUFFER_SIZE = 1460
WINDOW_SIZE = 5
TIMEOUT = 2.0  # Timeout de 2 segundos

# Função para enviar pacotes
def enviar_pacotes(UDPServerSocket, endereco, caminho_arquivo):
    with open(caminho_arquivo, 'rb') as file:
        base = 0
        next_seq_num = 0
        pacotes = []
        acks_recebidos = [False] * 10000  # Inicializa uma lista para acompanhar os ACKs
        timer = None

        # Ler o arquivo e dividir em pacotes
        while True:
            dados = file.read(BUFFER_SIZE)
            if not dados:
                break
            pacotes.append(dados)

        total_pacotes = len(pacotes)

        # Função para retransmitir pacotes em caso de timeout
        def timeout_handler():
            nonlocal next_seq_num
            print(f"Timeout - Retransmitindo pacotes da janela {base} a {base + WINDOW_SIZE - 1}")
            next_seq_num = base  # Voltar para o início da janela para retransmissão
            enviar_pacotes_janela()  # Chamar envio de pacotes novamente

        # Função para enviar pacotes dentro da janela
        def enviar_pacotes_janela():
            nonlocal timer
            for i in range(base, min(base + WINDOW_SIZE, total_pacotes)):
                if not acks_recebidos[i]:
                    # Simulação de perda de pacote
                    if random.random() > 0.05:
                        UDPServerSocket.sendto(pacotes[i], endereco)
                        print(f"Enviando pacote {i}")
                    else:
                        print(f"Perda do pacote {i} simulada")
            # Reiniciar o timer após enviar a janela
            if timer:
                timer.cancel()
            timer = Timer(TIMEOUT, timeout_handler)
            timer.start()

        # Transmissão usando a janela deslizante
        while base < total_pacotes:
            # Envia pacotes na janela atual
            enviar_pacotes_janela()

            try:
                # Espera por ACK
                ack_data, _ = UDPServerSocket.recvfrom(BUFFER_SIZE)
                ack_num = int(ack_data.decode())
                print(f"ACK recebido: {ack_num}")

                if ack_num >= base:
                    acks_recebidos[ack_num] = True  # Marca o pacote como recebido

                    # Avança a base da janela para o próximo pacote não confirmado
                    while base < total_pacotes and acks_recebidos[base]:
                        base += 1

            except socket.timeout:
                print("Timeout - Retransmitindo pacotes da janela")
                enviar_pacotes_janela()

        # Envia o pacote de término
        if timer:
            timer.cancel()
        UDPServerSocket.sendto(b"END_OF_TRANSMISSION", endereco)
        print("Transmissão concluída - Enviando pacote de término.")

def main(argv):
    try:
        UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        UDPServerSocket.bind((HOST, PORT))
        print("\nUDP server up and listening")

        while True:
            try:
                # Recebe mensagem do cliente
                UDPServerSocket.settimeout(None)
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
