import socket
import sys
import os
import struct
import random

HOST = '127.0.0.1'  # endereço IP
PORT = 1999          # Porta utilizada pelo servidor
BUFFER_SIZE = 1460   # tamanho do buffer para recepção dos dados
LOSS_PROBABILITY = 0.05  # 5% de probabilidade de perda de pacotes

def main(argv):
    try:
        UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        UDPServerSocket.bind((HOST, PORT))  # Escuta na porta especificada
        print("\nUDP server up and listening")

        while True:
            bytesAddressPair = UDPServerSocket.recvfrom(BUFFER_SIZE)  # recebe a mensagem do cliente
            endereco = bytesAddressPair[1]  # endereço do cliente
            print(f"\nCliente conectado: {endereco}")

            caminho_atual = os.path.dirname(os.path.abspath(__file__))  # Caminho absoluto do arquivo atual
            arquivos = os.listdir(caminho_atual)  # Lista de arquivos da pasta atual
            arquivos = [arquivo for arquivo in arquivos if arquivo != 'Server.py']  # Filtra arquivos
            arquivos = {i: arquivo for i, arquivo in enumerate(arquivos)}  # Dicionário de arquivos
            print("\nArquivos disponíveis: ")
            print(arquivos)

            # Enviar a lista de arquivos para o cliente
            UDPServerSocket.sendto(str(arquivos).encode(), endereco)

            # Receber a opção do cliente para download
            bytesAddressPair = UDPServerSocket.recvfrom(BUFFER_SIZE)
            opcao = int(bytesAddressPair[0].decode())
            print("\nOpção escolhida pelo cliente: ", opcao)

            arquivo = arquivos[opcao]
            caminho_arquivo = os.path.join(caminho_atual, arquivo)
            print("\nCaminho do arquivo: ", caminho_arquivo)

            # Enviar o arquivo para o cliente, fragmentando em 1460 bytes
            with open(caminho_arquivo, 'rb') as file:
                seq_num = 0  # Inicia o número de sequência em 0
                while True:
                    dados = file.read(BUFFER_SIZE - 4)  # Lê até 1460 bytes menos o espaço para o número de sequência
                    if not dados:
                        break

                    # Empacota o número de sequência junto com os dados
                    pacote_completo = struct.pack('I', seq_num) + dados

                    # Simula a perda de pacotes
                    if random.random() < LOSS_PROBABILITY:
                        print(f"Pacote {seq_num} perdido (simulação de erro).")
                    else:
                        UDPServerSocket.sendto(pacote_completo, endereco)
                        print(f"Enviando pacote {seq_num}")

                        # Aguarda o ACK do cliente
                        while True:
                            UDPServerSocket.settimeout(2)  # Timeout para aguardar ACK
                            try:
                                ack_data, _ = UDPServerSocket.recvfrom(BUFFER_SIZE)
                                ack_num = int(ack_data.decode())
                                print(f"ACK recebido para o pacote {ack_num}")
                                break  # Sai do loop se ACK é recebido
                            except socket.timeout:
                                print(f"Timeout - Pacote {seq_num} não reconhecido, retransmitindo.")
                                UDPServerSocket.sendto(pacote_completo, endereco)  # Retransmite o pacote se não houver ACK

                    seq_num += 1  # Incrementa o número de sequência

            print("\nArquivo enviado com sucesso!")

    except Exception as error:
        print("Erro na execução do servidor!!")
        print(error)
        return

if __name__ == "__main__":
    main(sys.argv[1:])
