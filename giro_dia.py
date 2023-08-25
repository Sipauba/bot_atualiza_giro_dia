import schedule
import time
import datetime

def minha_tarefa():
    print("Tarefa executada!")

# Agendar a tarefa para ser executada de segunda a sexta-feira às 10:00 AM
for dia_da_semana in range(0, 5):  # Segunda a sexta correspondem aos dias 0 a 4
    schedule.every().day.at("10:00").do(minha_tarefa).when(lambda: datetime.datetime.today().weekday() == dia_da_semana)

# Loop para manter o programa em execução enquanto aguarda a execução das tarefas agendadas
while True:
    schedule.run_pending()
    time.sleep(1)
