import socket, sys ,os, random
from threading import Thread

HOST = '127.0.0.1'  # endereço IP
PORT = 2002         # Porta utilizada pelo servidor
BUFFER_SIZE = 1460  # tamanho do buffer para recepção dos dados
TIMEOUT = 0.2       # Timeout de 1 segundo

def envia_arquivo(arquivo, endereco, caminho_arquivo, UDPServerSocket):
    # Enviar o arquivo para o cliente, fragmentando em 1460 bytes devido ao tamanho do buffer
    with open(caminho_arquivo, 'rb') as file:
        i = 0
        while True:
            dados = file.read(BUFFER_SIZE)
            if not dados:
                break
            while True:
                # Simulate a 5% error rate
                if random.random() < 0.95:
                    # Enviar pacote
                    UDPServerSocket.sendto(dados, endereco)
                else:
                    print(f"Falha simulada de envio de pacote {i}")
                    continue

                # Esperar confirmação do cliente
                try:
                    UDPServerSocket.settimeout(TIMEOUT)  # Timeout de 1 segundo
                    ack, _ = UDPServerSocket.recvfrom(BUFFER_SIZE)
                    if ack.decode() == 'ACK':
                        #print(f"pacote {i} enviado com sucesso")
                        i += 1
                        break
                    else:
                        print(f"Falha ao receber ACK do pacote {i}")
                except socket.timeout:
                    print(f"Timeout no pacote {i}, reenviando...")
    print("\nArquivo enviado com sucesso!!")
    print("Foram enviados ", i, " pacotes\n\n")


def receber_arquivo(UDPServerSocket, endereco, nome_arquivo):
    try:
        # Caminho para salvar o arquivo recebido
        caminho_atual = os.path.dirname(os.path.abspath(__file__))
        caminho_arquivo = os.path.join(caminho_atual, nome_arquivo)

        with open(caminho_arquivo, 'wb') as arquivo:
            while True:
                # Recebe dados do cliente
                dados, addr = UDPServerSocket.recvfrom(BUFFER_SIZE)
                if random.random() < 0.95:
                    arquivo.write(dados)

                    # Envia um ACK para o cliente
                    UDPServerSocket.sendto("ACK".encode(), endereco)

                    if len(dados) < BUFFER_SIZE:
                        break
                else:
                    print("Simulação de perda de pacote.")
        print(f"\nArquivo '{nome_arquivo}' recebido com sucesso!\n")
    except Exception as e:
        print(f"Erro ao receber o arquivo: {e}")


def main(argv):
    try:
        # Cria um socket UDP
        UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        UDPServerSocket.bind((HOST, PORT))  # Escuta na porta especificada
        print("\nUDP server up and listening")

        # Espera por conexões
        while True:
            bytesAddressPair = UDPServerSocket.recvfrom(BUFFER_SIZE)  # recebe a mensagem do cliente
            endereco = bytesAddressPair[1]  # endereço do cliente
            
            if bytesAddressPair[0].decode() == 'UPLOAD':
                # Receber nome do arquivo
                nome_arquivo, _ = UDPServerSocket.recvfrom(BUFFER_SIZE)
                nome_arquivo = nome_arquivo.decode()
                print(f"Cliente deseja enviar o arquivo: {nome_arquivo}")

                # Chamar a função para receber o arquivo
                receber_arquivo(UDPServerSocket, endereco, nome_arquivo)
                break

            elif bytesAddressPair[0].decode() == 'DOWNLOAD':
                clientIP = "Client IP Address:{}".format(endereco)  # endereço do cliente
                print("\n" + clientIP)

                caminho_atual = os.path.dirname(os.path.abspath(__file__))  # Caminho absoluto do arquivo atual
                arquivos = os.listdir(caminho_atual)  # Lista de arquivos da pasta atual, usando dicionário
                arquivos = [arquivo for arquivo in arquivos if not arquivo.endswith('.py')]  # Filtrar arquivos para não listar arquivos .py
                arquivos = {i: arquivo for i, arquivo in enumerate(arquivos)}  # Adicionar um número identificador para cada arquivo
                print("\nArquivos disponíveis: ")
                print(arquivos)

                # Enviar a lista de arquivos para o cliente
                UDPServerSocket.sendto(str(arquivos).encode(), endereco)

                # Receber a opção do cliente para download
                bytesAddressPair = UDPServerSocket.recvfrom(BUFFER_SIZE)
                opcao = int(bytesAddressPair[0].decode())
                print("\nOpção escolhida pelo cliente: ", opcao)

                # Enviar o arquivo escolhido pelo cliente
                arquivo = arquivos[opcao]
                print("\nArquivo escolhido pelo cliente: ", arquivo)
                caminho_arquivo = os.path.join(caminho_atual, arquivo)
                print("\nCaminho do arquivo: ", caminho_arquivo)

                envia_arquivo(arquivo, endereco, caminho_arquivo, UDPServerSocket)
                break
            
    except Exception as error:
        print("Erro na execução do servidor!!")
        print(error)
        return


if __name__ == "__main__":
    while True:
        main(sys.argv[1:])

