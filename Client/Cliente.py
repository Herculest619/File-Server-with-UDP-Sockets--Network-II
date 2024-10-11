import socket, os, sys, random, hashlib

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

def receber_arquivo(UDPClientSocket, file_name):
    current_directory = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_directory, file_name)

    with open(file_path, 'wb') as arquivo:
        while True:
            msgFromServer = UDPClientSocket.recvfrom(BUFFER_SIZE)
            if random.random() < 0.95:
                data = msgFromServer[0]
                arquivo.write(data)
                UDPClientSocket.sendto("ACK".encode(), (HOST, PORT))

                if len(data) < BUFFER_SIZE:
                    break
            else:
                print("Falha simula de perda de pacote!")

        print(f"\nArquivo '{file_name}' baixado com sucesso!\n")

    # Receber e verificar o hash MD5
    hash_md5_servidor, _ = UDPClientSocket.recvfrom(BUFFER_SIZE)
    hash_md5_servidor = hash_md5_servidor.decode()
    print(f"Hash MD5 recebido do servidor: {hash_md5_servidor}")

    # Calcular o hash MD5 do arquivo recebido
    hash_md5_local = calcular_hash_md5(file_path)
    print(f"Hash MD5 do arquivo baixado: {hash_md5_local}")

    if hash_md5_servidor == hash_md5_local:
        print("Verificação concluída com sucesso: os hashes coincidem.")
    else:
        print("Falha na verificação: os hashes não coincidem.")

def envia_arquivo(UDPClientSocket, file_name):
    try:
        current_directory = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_directory, file_name)

        with open(file_path, 'rb') as arquivo:
            i = 0
            while True:
                dados = arquivo.read(BUFFER_SIZE)
                if not dados:
                    break
                while True:
                    if random.random() < 0.95:
                        UDPClientSocket.sendto(dados, (HOST, PORT))
                    else:
                        print(f"Simulação de falha de envio do pacote {i}")
                        continue

                    try:
                        UDPClientSocket.settimeout(TIMEOUT)
                        ack, _ = UDPClientSocket.recvfrom(BUFFER_SIZE)
                        if ack.decode() == 'ACK':
                            i += 1
                            break
                    except socket.timeout:
                        print(f"Timeout no pacote {i}, reenviando...")
        print(f"\nArquivo '{file_name}' enviado com sucesso!\n")
    except Exception as e:
        print(f"Erro ao enviar o arquivo: {e}")

def main(argv):
    try:
        with socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM) as UDPClientSocket:
            opcao = input("\nDeseja baixar ou enviar arquivo?\n 1: DOWNLOAD \n 2: UPLOAD \n").lower()

            if opcao == '1':
                UDPClientSocket.sendto("DOWNLOAD".encode(), (HOST, PORT))
                msgFromServer = UDPClientSocket.recvfrom(BUFFER_SIZE)
                msg = msgFromServer[0].decode()
                arquivos = eval(msg)

                print("\nLista de arquivos do servidor:\n")
                for indice, nome_arquivo in arquivos.items():
                    print(f"{indice}: {nome_arquivo}")

                opcao = input("\nDigite o índice do arquivo a ser baixado: ")
                UDPClientSocket.sendto(opcao.encode(), (HOST, PORT))

                opcao = int(opcao)
                file_name = arquivos[opcao]
                receber_arquivo(UDPClientSocket, file_name)

            elif opcao == '2':
                caminho_atual = os.path.dirname(os.path.abspath(__file__))
                arquivos = os.listdir(caminho_atual)
                arquivos = [arquivo for arquivo in arquivos if not arquivo.endswith('.py')]
                arquivos = {i: arquivo for i, arquivo in enumerate(arquivos)}
                print("\nArquivos disponíveis: ")
                print(arquivos)

                opcao = input("\nDigite o índice do arquivo a ser enviado: ")
                opcao = int(opcao)
                file_name = arquivos[opcao]

                UDPClientSocket.sendto("UPLOAD".encode(), (HOST, PORT))
                UDPClientSocket.sendto(file_name.encode(), (HOST, PORT))
                envia_arquivo(UDPClientSocket, file_name)

    except Exception as error:
        print("Exceção - Programa será encerrado!")
        print(error)
        return

if __name__ == "__main__":
    main(sys.argv[1:])
