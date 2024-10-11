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
    try:
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
                    print("Falha simulada de perda de pacote!")

            print(f"\nArquivo '{file_name}' baixado com sucesso!\n")

        # Receber e verificar o hash MD5
        hash_md5_servidor, _ = UDPClientSocket.recvfrom(BUFFER_SIZE)
        hash_md5_servidor = hash_md5_servidor.decode()
        print(f"Hash MD5 recebido do servidor: {hash_md5_servidor}")

        # Calcular o hash MD5 do arquivo recebido
        hash_md5_local = calcular_hash_md5(file_path)
        print(f"Hash MD5 do arquivo baixado: {hash_md5_local}")

        if hash_md5_servidor == hash_md5_local:
            print("Verificação concluída com sucesso: os hashes coincidem.\n")
        else:
            print("Falha na verificação: os hashes não coincidem.\n")
    except Exception as e:
        print(f"Erro ao receber o arquivo: {e}")

def envia_arquivo(arquivo, endereco, caminho_arquivo, UDPClientSocket):
    try:
        with open(caminho_arquivo, 'rb') as file:
            i = 0
            while True:
                dados = file.read(BUFFER_SIZE)
                if not dados:
                    break
                while True:
                    if random.random() < 0.95:
                        UDPClientSocket.sendto(dados, endereco)
                    else:
                        print(f"Falha simulada de envio de pacote {i}")
                        continue

                    try:
                        UDPClientSocket.settimeout(TIMEOUT)
                        ack, _ = UDPClientSocket.recvfrom(BUFFER_SIZE)
                        if ack == b'ACK':  # Verificar o ACK como bytes
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
        UDPClientSocket.sendto(hash_md5.encode(), endereco)
        print(f"Hash MD5 do arquivo enviado: {hash_md5}")
    except Exception as e:
        print(f"Erro ao enviar o arquivo: {e}")


def main(argv):
    try:
        with socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM) as UDPClientSocket:
            opcao = input("\nDeseja baixar ou enviar arquivo?\n 1: DOWNLOAD \n 2: UPLOAD \n\n").lower()

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
                UDPClientSocket.sendto("UPLOAD".encode(), (HOST, PORT))

                # Pede a senha ao usuário para enviar o arquivo
                senha = input("\nDigite a senha para enviar o arquivo: ")
                UDPClientSocket.sendto(senha.encode(), (HOST, PORT))

                # Recebe a resposta do servidor sobre a senha
                resposta, _ = UDPClientSocket.recvfrom(BUFFER_SIZE)
                resposta = resposta.decode()
                print(resposta)
                if resposta == "Senha incorreta!":
                    print("Conexão encerrada.\n\n")
                    exit()

                caminho_atual = os.path.dirname(os.path.abspath(__file__))
                arquivos = os.listdir(caminho_atual)
                arquivos = [arquivo for arquivo in arquivos if not arquivo.endswith('.py')]
                arquivos = {i: arquivo for i, arquivo in enumerate(arquivos)}
                print("\nArquivos disponíveis: ")
                print(arquivos)

                opcao = input("\nDigite o índice do arquivo a ser enviado: ")
                opcao = int(opcao)
                file_name = arquivos[opcao]

                
                UDPClientSocket.sendto(file_name.encode(), (HOST, PORT))
                envia_arquivo(file_name, (HOST, PORT), os.path.join(caminho_atual, file_name), UDPClientSocket) 

    except Exception as error:
        print("Exceção - Programa será encerrado!")
        print(error)
        return

if __name__ == "__main__":
    main(sys.argv[1:])
