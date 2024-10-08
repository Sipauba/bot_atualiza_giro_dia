import schedule
import time
import datetime
import cx_Oracle

host = ''
servico = ''
usuario = ''
senha = ''

# Define o diretório onde os arquivos de log serão armazenados
diretorio_logs = "logs/"

# Encontra o arquivo que aponta para o banco de dados
cx_Oracle.init_oracle_client(lib_dir="P://instantclient_21_10")

# Faz a conexão ao banco de dados
conecta_banco = cx_Oracle.connect(usuario, senha, f'{host}/{servico}')

# Cria um cursor no banco para que seja possível fazer consultas e alterações no banco de dados
cursor = conecta_banco.cursor()

print('Aplicação iniciada!')

def atualiza_giro():
    dia_atual_inicio = datetime.datetime.now()
    print('----------------------------------------------------------------')
    print('Calculando dias úteis... => {}'.format(dia_atual_inicio))
    sql_dias_uteis = """
    SELECT 60+count(diavendas) FROM PCDIASUTEIS 
    WHERE DIAVENDAS='S' 
    AND CODFILIAL=6 
    AND DATA BETWEEN TRUNC(SYSDATE, 'MM')
    AND TRUNC(SYSDATE) - 1
    """
    cursor.execute(sql_dias_uteis)
    dias_uteis = cursor.fetchone()[0]
    print('Qt. dias úteis: {}'.format(dias_uteis))

    print('Atualizando Giro Dia...')
    sql_giro = 'UPDATE PCEST SET QTGIRODIA=round((NVL(QTVENDMES,0)+NVL(QTVENDMES1,0)+NVL(QTVENDMES2,0)+NVL(QTVENDMES3,0))/{},2) WHERE CODFILIAL IN (1,11,17,19,20,21,61)'.format(
        dias_uteis)
    cursor.execute(sql_giro)
    print('Fazendo COMMIT...')
    cursor.execute('COMMIT')
    dia_atual_fim = datetime.datetime.now()
    print('Giro atualizado! => {} '.format(dia_atual_fim))
    print('Giro aplicado às filiais: 1,11,17,19,20,21,61')
    print('----------------------------------------------------------------')
    
    # Gera o nome do arquivo de log com a data atual
    nome_arquivo = dia_atual_inicio.strftime("%d-%m-%Y") + ".txt"
    nome_arquivo_completo = diretorio_logs + nome_arquivo
    
    cursor.execute("""SELECT COUNT (*) 
                    FROM PCEST 
                    WHERE CODFILIAL IN (1,11,17,19,20,21,61)""")
    contagem_geral = cursor.fetchone()[0]
    
    cursor.execute("""SELECT COUNT (*)
                    FROM PCEST 
                    WHERE QTGIRODIA = 0
                    AND CODFILIAL IN (1,11,17,19,20,21,61)""")
    contagem_sem_giro = cursor.fetchone()[0]
    
    cursor.execute("""SELECT COUNT (*)
                    FROM PCEST
                    WHERE QTGIRODIA > 0
                    AND CODFILIAL IN (1,11,17,19,20,21,61)""")
    contagem_com_giro = cursor.fetchone()[0]
    
    # Executa o select para obter os dados
    sql_select_geral = cursor.execute("""
    SELECT CODFILIAL, CODPROD, QTEST, DTULTSAIDA, QTVENDMES, QTVENDMES1, QTVENDMES2, QTVENDMES3, QTGIRODIA 
    FROM PCEST 
    WHERE CODFILIAL IN (1,11,17,19,20,21,61)
    ORDER BY CODFILIAL""")

    # Abre o arquivo de log para escrita
    with open(nome_arquivo_completo, "w") as arquivo:
        arquivo.write("Data e hora da atualização do giro: {}\n".format(dia_atual_inicio))
        arquivo.write("Dias úteis calculados: {}\n".format(dias_uteis))
        arquivo.write("Linhas afetadas: {}\n".format(contagem_geral))
        arquivo.write("Itens sem giro: {}\n".format(contagem_sem_giro))
        arquivo.write("Itens com giro: {}\n".format(contagem_com_giro))
        arquivo.write("Data e hora do fim da atualização: {}\n".format(dia_atual_fim))
        arquivo.write("Giro aplicado às filiais: 1,11,17,19,20,21,61")
        
        """
        # Escreve os cabeçalhos das colunas
        arquivo.write("CODFILIAL, CODPROD, QTEST, DTULTSAIDA, QTVENDMES, QTVENDMES1, QTVENDMES2, QTVENDMES3, QTGIRODIA\n")
        # Escreve os dados no arquivo de log
        for linha in cursor:
            arquivo.write(",".join(map(str, linha)) + "\n")
        """
    
atualiza_giro()

def agendamento():
    schedule.every().monday.at("07:00").do(atualiza_giro)
    schedule.every().tuesday.at("07:00").do(atualiza_giro)
    schedule.every().wednesday.at("07:00").do(atualiza_giro)
    schedule.every().thursday.at("07:00").do(atualiza_giro)
    schedule.every().friday.at("07:00").do(atualiza_giro)

    while True:
        schedule.run_pending()
        time.sleep(1)

agendamento()
