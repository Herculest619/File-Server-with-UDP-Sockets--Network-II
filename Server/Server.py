import socket, sys, os, random, hashlib
from threading import Thread

HOST = '127.0.0.1'
PORT = 2002
BUFFER_SIZE = 1460
TIMEOUT = 0.2
PASSWORD = "1234"

# Função para calcular o hash MD5 de um arquivo
def calcular_hash_md5(caminho_arquivo):
    md5_hash = hashlib.md5()
    with open(caminho_arquivo, 'rb') as f:
        while chunk := f.read(BUFFER_SIZE):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()

def envia_arquivo(arquivo, endereco, caminho_arquivo, UDPServerSocket):
    try:
        with open(caminho_arquivo, 'rb') as file:
            i = 0
            while True:
                dados = file.read(BUFFER_SIZE) # Lê os dados do arquivo
                if not dados:
                    break
                # Envia os dados para o cliente com uma probabilidade de 95% de sucesso
                while True:
                    if random.random() < 0.95:
                        UDPServerSocket.sendto(dados, endereco)
                    else:
                        print(f"Falha simulada de envio de pacote {i}")
                        continue

                    # Recebe o ACK do cliente, em caso de timeout reenvia o pacote
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

    except Exception as e:
        print(f"Erro ao enviar o arquivo: {e}") 

def receber_arquivo(UDPServerSocket, file_name):
    try:
        current_directory = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_directory, file_name)

        with open(file_path, 'wb') as arquivo:
            while True:
                try:
                    data, endereco = UDPServerSocket.recvfrom(BUFFER_SIZE)
                    if random.random() < 0.95:
                        arquivo.write(data)
                        UDPServerSocket.sendto(b"ACK", endereco)  # Enviar ACK como bytes

                        if len(data) < BUFFER_SIZE:
                            break
                    else:
                        print("Falha simulada de perda de pacote!")
                except socket.timeout:
                    print("Timeout na recepção do pacote, aguardando novo pacote...")

            print(f"\nArquivo '{file_name}' recebido com sucesso!\n")

        # Receber e verificar o hash MD5
        hash_md5_servidor, _ = UDPServerSocket.recvfrom(BUFFER_SIZE)
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

def main(argv):
    try:
        UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM) # socket.socket(socket.AF_INET, socket.SOCK_DGRAM) é um construtor de objetos de soquete
        UDPServerSocket.bind((HOST, PORT)) # Associa o socket a um endereço e porta específicos
        print("\nUDP server up and listening")

        while True:
            # Recebe dados do soquete. O valor de retorno é um par (bytes, endereço), onde bytes é um objeto de bytes que representa os dados recebidos e endereço é o endereço do soquete enviador.
            bytesAddressPair = UDPServerSocket.recvfrom(BUFFER_SIZE) 
            endereco = bytesAddressPair[1] # Endereço do cliente
            
            if bytesAddressPair[0].decode() == 'UPLOAD':
                print(f"\nCliente conectado: {endereco}")
                # Testa senha recebida validando com a senha do servidor
                senha, _ = UDPServerSocket.recvfrom(BUFFER_SIZE)    
                senha = senha.decode()
                if senha != PASSWORD:
                    print("Senha incorreta!")
                    # Retorna para o cliente que a senha está incorreta
                    UDPServerSocket.sendto("Senha incorreta!".encode(), endereco)

                    print("Encerrando conexão com o cliente...")
                    # Encerra a conexão com o cliente
                    UDPServerSocket.close()
                    break

                print("Senha correta!")
                UDPServerSocket.sendto("Senha correta!".encode(), endereco)

                nome_arquivo, _ = UDPServerSocket.recvfrom(BUFFER_SIZE)
                nome_arquivo = nome_arquivo.decode()
                print(f"Cliente deseja enviar o arquivo: {nome_arquivo}")
                receber_arquivo(UDPServerSocket, nome_arquivo)
                break

            elif bytesAddressPair[0].decode() == 'DOWNLOAD':
                clientIP = f"Client IP Address: {endereco}"
                print("\n" + clientIP)

                # Lê os arquivos disponíveis no diretório do servidor
                caminho_atual = os.path.dirname(os.path.abspath(__file__))
                arquivos = os.listdir(caminho_atual)
                arquivos = [arquivo for arquivo in arquivos if not arquivo.endswith('.py')] # Exclui arquivos .py
                arquivos = {i: arquivo for i, arquivo in enumerate(arquivos)} # Enumera os arquivos
                print("\nArquivos disponíveis: ")
                print(arquivos)

                # Envia a lista de arquivos para o cliente
                UDPServerSocket.sendto(str(arquivos).encode(), endereco) # Envia a lista de arquivos para o cliente
                bytesAddressPair = UDPServerSocket.recvfrom(BUFFER_SIZE) # Recebe a opção escolhida pelo cliente
                opcao = int(bytesAddressPair[0].decode()) # Converte a opção para inteiro
                print(f"\nOpção escolhida pelo cliente: {opcao}")

                arquivo = arquivos[opcao]
                print(f"\nArquivo escolhido pelo cliente: {arquivo}")
                caminho_arquivo = os.path.join(caminho_atual, arquivo) # Caminho do arquivo escolhido
                print(f"\nCaminho do arquivo: {caminho_arquivo}")

                # Função para enviar o arquivo para o cliente
                envia_arquivo(arquivo, endereco, caminho_arquivo, UDPServerSocket)
                break

    except Exception as error:
        print("Erro na execução do servidor!!")
        print(error)
        return

if __name__ == "__main__":
    while True:
        main(sys.argv[1:])
