import socket
import sys
import os
import struct

HOST = '127.0.0.1'  # endereço IP
PORT = 1999          # Porta utilizada pelo servidor
BUFFER_SIZE = 1460   # tamanho do buffer para recepção dos dados

def main(argv): 
    try:
        with socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM) as UDPClientSocket:
            UDPClientSocket.sendto("texto".encode(), (HOST, PORT)) 

            msgFromServer = UDPClientSocket.recvfrom(BUFFER_SIZE)  # Recebe a mensagem do servidor
            msg = msgFromServer[0].decode()  # Decodifica a mensagem recebida para uma string

            arquivos = eval(msg)  # Usando eval para converter a string de volta para um dicionário
            print("\nLista de arquivos do servidor:" + "\n")
            for indice, nome_arquivo in arquivos.items():
                print(f"{indice}: {nome_arquivo}")  # Exibe o índice e o nome do arquivo, um por linha

            opcao = input("\nDigite o índice do arquivo a ser baixado: ")
            UDPClientSocket.sendto(opcao.encode(), (HOST, PORT))

            # Recebe o arquivo, ele virá em partes
            opcao = int(opcao)
            file_name = arquivos[opcao]
            current_directory = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(current_directory, file_name)

            with open(file_path, 'wb') as arquivo:
                expected_seq_num = 0  # Espera pelo número de sequência 0
                received_packets = {}  # Dicionário para armazenar pacotes recebidos fora de ordem
                while True:
                    try:
                        msgFromServer = UDPClientSocket.recvfrom(BUFFER_SIZE)
                        pacote = msgFromServer[0]

                        # Desempacota o número de sequência
                        seq_num = struct.unpack('I', pacote[:4])[0]
                        dados = pacote[4:]

                        # Verifica se o número de sequência está correto
                        if seq_num == expected_seq_num:
                            arquivo.write(dados)  # Escreve os dados no arquivo
                            print(f"Recebido pacote {seq_num}")
                            expected_seq_num += 1  # Espera o próximo pacote

                            # Envia ACK para o servidor
                            UDPClientSocket.sendto(str(seq_num).encode(), msgFromServer[1])

                            # Processa pacotes recebidos fora de ordem
                            while expected_seq_num in received_packets:
                                arquivo.write(received_packets[expected_seq_num])  # Escreve os dados do pacote armazenado
                                print(f"Processando pacote fora de ordem: {expected_seq_num}")
                                del received_packets[expected_seq_num]  # Remove o pacote da lista
                                expected_seq_num += 1  # Espera o próximo pacote

                        elif seq_num > expected_seq_num:
                            # Armazena pacotes fora de ordem
                            received_packets[seq_num] = dados
                            print(f"Pacote fora de ordem recebido: {seq_num}. Esperando {expected_seq_num}.")
                            
                        # Para o loop se não houver mais dados
                        if len(dados) < BUFFER_SIZE - 4:
                            break  # Se os dados recebidos foram menores que o buffer, significa que é o último pacote

                    except socket.timeout:
                        print(f"Timeout - Pacote {expected_seq_num} não recebido. Retransmitindo ACK.")
                        UDPClientSocket.sendto(str(expected_seq_num - 1).encode(), msgFromServer[1])  # Retransmite o último ACK

            print(f"\nArquivo '{file_name}' baixado com sucesso!\n")

    except Exception as error:
        print("Exceção - Programa será encerrado!")
        print(error)
        return

if __name__ == "__main__":   
    main(sys.argv[1:])
