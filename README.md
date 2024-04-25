
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


O código SQL usado na aplicação é dividida em três partes. A primeira é reponsável por calcular a quantidade de dias úteis contando a partir dos 3 ultimos meses até o dia corrente do mês atual.Essa consulta gera apenas um campo com a quantidade de dias.

```bash
    SELECT 60+count(diavendas) FROM PCDIASUTEIS 
    WHERE DIAVENDAS='S' 
    AND CODFILIAL=6 
    AND DATA BETWEEN TRUNC(SYSDATE, 'MM')
    AND TRUNC(SYSDATE) - 1
```
A segunda parte do código é responsável por fazer o update com a quantidade dos dias úteis. O NVL é necessário para considerar como zero os campos com valor nulo. Se o valor nulo for incluido no cálculo o valor do giro também fica nulo.

```bash
UPDATE PCEST SET QTGIRODIA=round((NVL(QTVENDMES,0)+NVL(QTVENDMES1,0)+NVL(QTVENDMES2,0)+NVL(QTVENDMES3,0))/{},2) 
WHERE CODFILIAL IN (1,3,4,5,6,7,70,14,17,18,19,20,61)
```

A terceira parte é responsável por gerar algumas informações e armazenar em um arquivo de log. Dentre as informações estão: quantidades de linhas afetadas na atualização, quantidade de itens com giro e quantidade de itens sem giro.
```bash
# Gera o nome do arquivo de log com a data atual
    nome_arquivo = dia_atual_inicio.strftime("%d-%m-%Y") + ".txt"
    nome_arquivo_completo = diretorio_logs + nome_arquivo
    
    cursor.execute("""SELECT COUNT (*) 
                    FROM PCEST 
                    WHERE CODFILIAL IN (1,3,4,5,6,7,70,14,17,18,19,20,61)""")
    contagem_geral = cursor.fetchone()[0]
    
    cursor.execute("""SELECT COUNT (*)
                    FROM PCEST 
                    WHERE QTGIRODIA = 0
                    AND CODFILIAL IN (1,3,4,5,6,7,70,14,17,18,19,20,61)""")
    contagem_sem_giro = cursor.fetchone()[0]
    
    cursor.execute("""SELECT COUNT (*)
                    FROM PCEST
                    WHERE QTGIRODIA > 0
                    AND CODFILIAL IN (1,3,4,5,6,7,70,14,17,18,19,20,61)""")
    contagem_com_giro = cursor.fetchone()[0]
```


## Aplicação
Este é o coração da aplicação. A função atualiza_giro() possui 3 partes principais: calcular a quantidade de dias úteis, fazer a atualização no banco de dados e criar um arquivo de log para fins de controle e consulta posteriores.


```bash
def atualiza_giro():
    dia_atual_inicio = datetime.datetime.now()
    print('---------------------------------------------------')
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
    sql_giro = 'UPDATE PCEST SET QTGIRODIA=round((NVL(QTVENDMES,0)+NVL(QTVENDMES1,0)+NVL(QTVENDMES2,0)+NVL(QTVENDMES3,0))/{},2) WHERE CODFILIAL IN (1,3,4,5,6,7,70,14,17,18,19,20,61)'.format(
        dias_uteis)
    cursor.execute(sql_giro)
    print('Fazendo COMMIT...')
    cursor.execute('COMMIT')
    dia_atual_fim = datetime.datetime.now()
    print('Giro atualizado! - {} -'.format(dia_atual_fim))
    print('---------------------------------------------------')
    
    # Gera o nome do arquivo de log com a data atual
    nome_arquivo = dia_atual_inicio.strftime("%d-%m-%Y") + ".txt"
    nome_arquivo_completo = diretorio_logs + nome_arquivo
    
    cursor.execute("""SELECT COUNT (*) 
                    FROM PCEST 
                    WHERE CODFILIAL IN (1,3,4,5,6,7,70,14,17,18,19,20,61)""")
    contagem_geral = cursor.fetchone()[0]
    
    cursor.execute("""SELECT COUNT (*)
                    FROM PCEST 
                    WHERE QTGIRODIA = 0
                    AND CODFILIAL IN (1,3,4,5,6,7,70,14,17,18,19,20,61)""")
    contagem_sem_giro = cursor.fetchone()[0]
    
    cursor.execute("""SELECT COUNT (*)
                    FROM PCEST
                    WHERE QTGIRODIA > 0
                    AND CODFILIAL IN (1,3,4,5,6,7,70,14,17,18,19,20,61)""")
    contagem_com_giro = cursor.fetchone()[0]
    
    # Executa o select para obter os dados
    sql_select_geral = cursor.execute("""
    SELECT CODFILIAL, CODPROD, QTEST, DTULTSAIDA, QTVENDMES, QTVENDMES1, QTVENDMES2, QTVENDMES3, QTGIRODIA 
    FROM PCEST 
    WHERE CODFILIAL IN (1,3,4,5,6,7,70,14,17,18,19,20,61)
    ORDER BY CODFILIAL""")

    # Abre o arquivo de log para escrita
    with open(nome_arquivo_completo, "w") as arquivo:
        arquivo.write("Data e hora da atualização do giro: {}\n".format(dia_atual_inicio))
        arquivo.write("Dias úteis calculados: {}\n".format(dias_uteis))
        arquivo.write("Linhas afetadas: {}\n".format(contagem_geral))
        arquivo.write("Itens sem giro: {}\n".format(contagem_sem_giro))
        arquivo.write("Itens com giro: {}\n".format(contagem_com_giro))
        arquivo.write("Data e hora do fim da atualização: {}\n".format(dia_atual_fim))
        
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
```
# Conclusão

Ao automatizar minhas tarefas, estou menos suscetível à falhas humanas como por exemplo esquecer de executa-las. Ganho mais tempo "livre" para pensar em outras soluções que possam otimizar os meus processos ou de outros colaboradores da empresa, ganhando tempo e diminuindo a chance de erros manuais.
SEGUIMOS AUTOMATIZANDO TUDO QUANDO FOR POSSÍVEL!!
