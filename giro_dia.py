import schedule
import time
import datetime
import cx_Oracle

host = 'x.x.x.x'
servico = 'xxxx'
usuario = 'xxxxxx'
senha = 'xxxxxxxxxxx'

# Encontra o arquivo que aponta para o banco de dados
cx_Oracle.init_oracle_client(lib_dir="./instantclient_21_10")

# Faz a conexão ao banco de dados
conecta_banco = cx_Oracle.connect(usuario, senha, f'{host}/{servico}')

# Cria um cursor no banco para que seja possível fazer consultas e alterações no banco de dados
cursor = conecta_banco.cursor()

def minha_tarefa():
    print("Tarefa executada!")
    sql_dias_uteis = """
    SELECT 60+count(diavendas) FROM PCDIASUTEIS 
    WHERE DIAVENDAS='S' 
    AND CODFILIAL=6 
    AND DATA BETWEEN TRUNC(SYSDATE, 'MM')
    AND TRUNC(SYSDATE) - 1
    """
    cursor.execute(sql_dias_uteis)
    dias_uteis = cursor.fetchone()[0]
    
    sql_giro = """UPDATE PCEST 
    SET QTGIRODIA=round((QTVENDMES+QTVENDMES1+QTVENDMES2+QTVENDMES3)/{},2)
    WHERE CODFILIAL IN (3,4,5,6,7,70,14,17,18,19,20,61);
    COMMIT;
    """.format(dias_uteis)
    cursor.execute(sql_giro)

# Agendar a tarefa para ser executada de segunda a sexta-feira às 10:00 AM
for dia_da_semana in range(0, 5):  # Segunda a sexta correspondem aos dias 0 a 4
    schedule.every().day.at("10:00").do(minha_tarefa).when(lambda: datetime.datetime.today().weekday() == dia_da_semana)

# Loop para manter o programa em execução enquanto aguarda a execução das tarefas agendadas
while True:
    schedule.run_pending()
    time.sleep(1)
