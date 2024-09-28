'''
Server de arquivos UDP
a. O servidor deve disponibilizar uma lista de todos os arquivos para o cliente que conectar.
b. Criar uma senha para somente o cliente com a senha poder enviar arquivos para o servidor.
'''

import socket, sys, os
from threading import Thread

HOST = '127.0.0.1'  # endereço IP
PORT = 1999        # Porta utilizada pelo servidor
BUFFER_SIZE = 1460  # tamanho do buffer para recepção dos dados

def main(argv):
    try:
        # Cria um socket UDP
        # AF_INET: Família de endereços, neste caso, IPv4
        # SOCK_DGRAM: Tipo de socket, neste caso, UDP
        UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        UDPServerSocket.bind((HOST, PORT)) # Escuta na porta especificada
        print("\nUDP server up and listening")

        # Espera por conexões
        while(True):
            bytesAddressPair = UDPServerSocket.recvfrom(BUFFER_SIZE) # recebe a mensagem do cliente
            endereco = bytesAddressPair[1] # endereço do cliente
            # clientMsg = "Mensagem do cliente:{}".format(mensagem) # mensagem do cliente
            clientIP  = "Client IP Address:{}".format(endereco) # endereço do cliente
            print("\n"+clientIP)

            caminho_atual = os.path.dirname(os.path.abspath(__file__)) # Caminho absoluto do arquivo atual
            arquivos = os.listdir(caminho_atual) # Lista de arquivos da pasta atual, usando dicionário
            arquivos = [arquivo for arquivo in arquivos if arquivo != 'Server.py'] # Filtrar arquivos para não listar o arquivo Server.py
            arquivos = {i: arquivo for i, arquivo in enumerate(arquivos)} # Adicionar um número identificador para cada arquivo
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

            # Enviar o arquivo para o cliente, fragmentando em 1460 bytes devivo ao tamanho do buffer
            with open(caminho_arquivo, 'rb') as file:
                i=0
                while True:
                    dados = file.read(BUFFER_SIZE)
                    if not dados:
                        break
                    #print("Enviando fragmento: ", i)
                    i+=1
                    UDPServerSocket.sendto(dados, endereco)
            print("\nArquivo enviado com sucesso!!")



    except Exception as error:
        print("Erro na execução do servidor!!")
        print(error)        
        return             



if __name__ == "__main__":   
    main(sys.argv[1:])