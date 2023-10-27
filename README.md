
# Automatização de tarefas em banco Oracle utilizando Python

Esta é uma simples aplicação desenvolvida com a finalidade de automatizar um processo diário que era feito por mim na empresa onde trabalho. Vez ou outra eu acabava esquecendo ou atrasando esta tarefa por conta da alta demanda de trabalho. Então resolvi automatizar o processo e garantir que todos os dias da semana em um horário específico o processo iria ser executado independente de qualquer coisa. 


# Desenvolvimento...

Esta aplicação foi até tranquila de fazer, já que a parte mais difícil eu já dominei em projetos passados, que é a conexão da aplicação com o banco ORACLE. As demais funcionalidades com um pouco de pesquisa ou perguntando ao ChatGPT é simples encontrar as informações necessárias.

## Conectando ao banco

Primeiramente, instalar e importar a biblioteca cx_Oracle. Depois criei variáveis que contém as informações específicas do banco de dados  que eu irei conectar, seguido das linhas de código responsáveis por fazer a conexão ao banco e criar um cursor para que seja possível fazer interações com o banco.

```bash
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
```

## SQL e o 'giro'

Afinal, o que diacho é o giro??? O setor de compras da empresa que trabalho abastece o centro de distribuição com mercadoria baseado na venda realizada nos dias úteis dos meses passados. Esse cálculo que chamamos de 'giro', calcula o que foi vendido por dia útil e faz uma projeção futura de quanto de mercadoria deve ser comprada levando em consideração a mercadoria que já foi comprada e ainda não chegou e o estoque disponível.

##

O código SQL usado na aplicação é dividida em duas partes. A primeira é reponsável por calcular a quantidade de dias úteis contando a partir dos 3 ultimos meses até o dia corrente do mês atual.Essa consulta gera apenas um campo com a quantidade de dias.

```bash
    SELECT 60+count(diavendas) FROM PCDIASUTEIS 
    WHERE DIAVENDAS='S' 
    AND CODFILIAL=6 
    AND DATA BETWEEN TRUNC(SYSDATE, 'MM')
    AND TRUNC(SYSDATE) - 1
```
A segunda parte do código é responsável por fazer o update com a quantidade dos dias úteis.

```bash
UPDATE PCEST SET QTGIRODIA=round((QTVENDMES+QTVENDMES1+QTVENDMES2+QTVENDMES3)/{},2) 
WHERE CODFILIAL IN (3,4,5,6,7,70,14,17,18,19,20,61)
```

## Aplicação
Bem simples e sem complicação! Existem apenas duas funções no código, uma responável por calcular o giro e fazer o update no banco e outra função responsável por agendar e executar a função anterior.

```bash
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
```
# Conclusão

Ao automatizar minhas tarefas, estou menos suscetível à falhas humanas como por exemplo esquecer de executa-las. Ganho mais tempo "livre" para pensar em outras soluções que possam otimizar os meus processos ou de outros colaboradores da empresa, ganhando tempo e diminuindo a chance de erros manuais.
SEGUIMOS AUTOMATIZANDO TUDO QUANDO FOR POSSÍVEL!!
