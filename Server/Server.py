import socket, sys, os, random, hashlib
from threading import Thread

HOST = '127.0.0.1'
PORT = 2002
BUFFER_SIZE = 1460
TIMEOUT = 0.2

# Função para calcular o hash MD5 de um arquivo
def calcular_hash_md5(caminho_arquivo):
    md5_hash = hashlib.md5()
    with open(caminho_arquivo, 'rb') as f:
        while chunk := f.read(BUFFER_SIZE):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()

def envia_arquivo(arquivo, endereco, caminho_arquivo, UDPServerSocket):
    with open(caminho_arquivo, 'rb') as file:
        i = 0
        while True:
            dados = file.read(BUFFER_SIZE)
            if not dados:
                break
            while True:
                if random.random() < 0.95:
                    UDPServerSocket.sendto(dados, endereco)
                else:
                    print(f"Falha simulada de envio de pacote {i}")
                    continue

                try:
                    UDPServerSocket.settimeout(TIMEOUT)
                    ack, _ = UDPServerSocket.recvfrom(BUFFER_SIZE)
                    if ack.decode() == 'ACK':
                        i += 1
                        break
                    else:
                        print(f"Falha ao receber ACK do pacote {i}")
                except socket.timeout:
                    print(f"Timeout no pacote {i}, reenviando...")

    print("\nArquivo enviado com sucesso!!")
    print(f"Foram enviados {i} pacotes\n")

    # Calcular e enviar o hash MD5 do arquivo
    hash_md5 = calcular_hash_md5(caminho_arquivo)
    UDPServerSocket.sendto(hash_md5.encode(), endereco)
    print(f"Hash MD5 do arquivo enviado: {hash_md5}")

def receber_arquivo(UDPServerSocket, endereco, nome_arquivo):
    try:
        caminho_atual = os.path.dirname(os.path.abspath(__file__))
        caminho_arquivo = os.path.join(caminho_atual, nome_arquivo)

        with open(caminho_arquivo, 'wb') as arquivo:
            while True:
                dados, addr = UDPServerSocket.recvfrom(BUFFER_SIZE)
                if random.random() < 0.95:
                    arquivo.write(dados)
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
        UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        UDPServerSocket.bind((HOST, PORT))
        print("\nUDP server up and listening")

        while True:
            bytesAddressPair = UDPServerSocket.recvfrom(BUFFER_SIZE)
            endereco = bytesAddressPair[1]
            
            if bytesAddressPair[0].decode() == 'UPLOAD':
                nome_arquivo, _ = UDPServerSocket.recvfrom(BUFFER_SIZE)
                nome_arquivo = nome_arquivo.decode()
                print(f"Cliente deseja enviar o arquivo: {nome_arquivo}")
                receber_arquivo(UDPServerSocket, endereco, nome_arquivo)
                break

            elif bytesAddressPair[0].decode() == 'DOWNLOAD':
                clientIP = f"Client IP Address: {endereco}"
                print("\n" + clientIP)

                caminho_atual = os.path.dirname(os.path.abspath(__file__))
                arquivos = os.listdir(caminho_atual)
                arquivos = [arquivo for arquivo in arquivos if not arquivo.endswith('.py')]
                arquivos = {i: arquivo for i, arquivo in enumerate(arquivos)}
                print("\nArquivos disponíveis: ")
                print(arquivos)

                UDPServerSocket.sendto(str(arquivos).encode(), endereco)
                bytesAddressPair = UDPServerSocket.recvfrom(BUFFER_SIZE)
                opcao = int(bytesAddressPair[0].decode())
                print(f"\nOpção escolhida pelo cliente: {opcao}")

                arquivo = arquivos[opcao]
                print(f"\nArquivo escolhido pelo cliente: {arquivo}")
                caminho_arquivo = os.path.join(caminho_atual, arquivo)
                print(f"\nCaminho do arquivo: {caminho_arquivo}")

                envia_arquivo(arquivo, endereco, caminho_arquivo, UDPServerSocket)
                break
    except Exception as error:
        print("Erro na execução do servidor!!")
        print(error)
        return

if __name__ == "__main__":
    while True:
        main(sys.argv[1:])
