import schedule
import time
import datetime
import cx_Oracle

host = 'xx'
servico = 'xx'
usuario = 'xx'
senha = 'xx'

# Encontra o arquivo que aponta para o banco de dados
cx_Oracle.init_oracle_client(lib_dir="./instantclient_21_10")

# Faz a conexão ao banco de dados
conecta_banco = cx_Oracle.connect(usuario, senha, f'{host}/{servico}')

# Cria um cursor no banco para que seja possível fazer consultas e alterações no banco de dados
cursor = conecta_banco.cursor()

dia_atual = datetime.datetime.now()

def atualiza_giro():
    
    print('---------------------------------------------------')
    print('Calculando dias uteis...')
    sql_dias_uteis = """
    SELECT 60+count(diavendas) FROM PCDIASUTEIS 
    WHERE DIAVENDAS='S' 
    AND CODFILIAL=6 
    AND DATA BETWEEN TRUNC(SYSDATE, 'MM')
    AND TRUNC(SYSDATE) - 1
    """
    cursor.execute(sql_dias_uteis)
    dias_uteis = cursor.fetchone()[0]
    print('Qt. dias uteis: {}'.format(dias_uteis))
    
    print('Atualizando Giro Dia...')
    sql_giro = 'UPDATE PCEST SET QTGIRODIA=round((QTVENDMES+QTVENDMES1+QTVENDMES2+QTVENDMES3)/{},2) WHERE CODFILIAL IN (3,4,5,6,7,70,14,17,18,19,20,61)'.format(dias_uteis)
    cursor.execute(sql_giro)
    print('Fazendo COMMIT...')
    cursor.execute('COMMIT')
    print('Giro atualizado! - {} -'.format(dia_atual))
    print('---------------------------------------------------')
    
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