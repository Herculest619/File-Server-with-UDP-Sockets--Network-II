import socket, os, sys, random

HOST = '127.0.0.1'  # endereço IP
PORT = 2002         # Porta utilizada pelo servidor
BUFFER_SIZE = 1460  # tamanho do buffer para recepção dos dados
TIMEOUT = 0.2       # Timeout de 1 segundo

def receber_arquivo(UDPClientSocket, file_name):
    current_directory = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_directory, file_name)

    with open(file_path, 'wb') as arquivo:
                while True:
                    
                    msgFromServer = UDPClientSocket.recvfrom(BUFFER_SIZE)
                    # Simula uma perda de pacote de 5%
                    if random.random() < 0.95:
                        data = msgFromServer[0]
                        arquivo.write(data)

                        # Envia um ACK para o servidor
                        UDPClientSocket.sendto("ACK".encode(), (HOST, PORT))

                        if len(data) < BUFFER_SIZE:
                            break
                    else:
                        print("Falha simula de perda de pacote!")

                print(f"\nArquivo '{file_name}' baixado com sucesso!\n")


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

                    # Esperar confirmação do servidor
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
        # Cria o socket UDP
        with socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM) as UDPClientSocket:
            
            opcao = input("\nDeseja baixar ou enviar arquivo?\n 1:DONLOAD \n 2:UPLOAD \n").lower()
            
            if opcao == '1':
                UDPClientSocket.sendto("DOWNLOAD".encode(), (HOST, PORT))  # Solicita a lista de arquivos
                # (código para download permanece igual)
                msgFromServer = UDPClientSocket.recvfrom(BUFFER_SIZE)  # Recebe a mensagem do servidor
                msg = msgFromServer[0].decode()  # Decodifica a mensagem recebida para uma string

                arquivos = eval(msg)  # Converte a string de volta para um dicionário

                # Formata a mensagem de forma legível
                print("\nLista de arquivos do servidor:\n")
                for indice, nome_arquivo in arquivos.items():
                    print(f"{indice}: {nome_arquivo}")  # Exibe o índice e o nome do arquivo, um por linha

                # Recebe o índice do arquivo a ser baixado
                opcao = input("\nDigite o índice do arquivo a ser baixado: ")
                UDPClientSocket.sendto(opcao.encode(), (HOST, PORT))

                # Recebe o arquivo, ele virá em partes devido ao tamanho do buffer de 1460 bytes
                opcao = int(opcao)
                file_name = arquivos[opcao]

                receber_arquivo(UDPClientSocket, file_name)
                
            elif opcao == '2':
                caminho_atual = os.path.dirname(os.path.abspath(__file__))  # Caminho absoluto do arquivo atual
                arquivos = os.listdir(caminho_atual)  # Lista de arquivos da pasta atual, usando dicionário
                arquivos = [arquivo for arquivo in arquivos if not arquivo.endswith('.py')]  # Filtrar arquivos para não listar arquivos .py
                arquivos = {i: arquivo for i, arquivo in enumerate(arquivos)}  # Adicionar um número identificador para cada arquivo
                print("\nArquivos disponíveis: ")
                print(arquivos)

                opcao = input("\nDigite o índice do arquivo a ser enviado: ")
                opcao = int(opcao)
                file_name = arquivos[opcao] # Nome do arquivo a ser enviado

                UDPClientSocket.sendto("UPLOAD".encode(), (HOST, PORT))  # Informa o servidor que quer fazer upload
                UDPClientSocket.sendto(file_name.encode(), (HOST, PORT))  # Envia o nome do arquivo
                envia_arquivo(UDPClientSocket, file_name)  # Envia o arquivo


    except Exception as error:
        print("Exceção - Programa será encerrado!")
        print(error)
        return

if __name__ == "__main__":
    main(sys.argv[1:])
