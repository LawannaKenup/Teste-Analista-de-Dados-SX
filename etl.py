import pyspark
from pyspark.sql import SparkSession
from pyspark.sql import DataFrame
import mysql.connector
from mysql.connector import Error

def main():
    print('Iniciando ETL')

    # Inicializando Spark
    spark = SparkSession.builder \
        .appName("Teste_SX") \
        .getOrCreate()

    # Localização da base
    base_path = '/app/staging/DADOS/MICRODADOS_ENEM_2020.csv'  
    print('Lendo dados do arquivo CSV')
    
    # Lendo o CSV
    df = read_csv(spark, base_path)

    # Processando os dados
    df = process_data(df)

    # Escrevendo no banco de dados
    write_mysql(df)

    print('ETL concluído com sucesso')


def read_csv(spark, path):
    """Lê o CSV e retorna um DataFrame."""
    return spark.read.format('csv') \
        .option("sep", ";") \
        .option("header", "true") \
        .option("inferSchema", "true") \
        .load(path)


def process_data(df: DataFrame) -> DataFrame:
    """Seleciona as colunas que são relevantes e remove duplicatas."""
    colunas = ['NU_INSCRICAO', 'NU_ANO', 'TP_FAIXA_ETARIA', 'TP_SEXO', 'TP_ST_CONCLUSAO',
                'TP_COR_RACA', 'TP_ESCOLA', 'TP_PRESENCA_CN', 'TP_PRESENCA_CH', 'TP_PRESENCA_LC', 
                'TP_PRESENCA_MT', 'CO_PROVA_CN', 'CO_PROVA_CH', 'CO_PROVA_LC', 'CO_PROVA_MT',
                'NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'TP_STATUS_REDACAO', 
                'NU_NOTA_REDACAO', 'Q001', 'Q002', 'Q003', 'Q004', 'Q005', 'Q006']

    df = df.select(*colunas)
    print('Removendo duplicatas')
    df = df.dropDuplicates()

    return df


def write_mysql(df: DataFrame):
    """Escreve o DataFrame no MySQL usando o MySQL Connector."""
    
    # SQL para criar a tabela, caso não exista
    create_table_query = """
    CREATE TABLE IF NOT EXISTS ENEM_TABLE (
        NU_INSCRICAO INT NOT NULL PRIMARY KEY,
        NU_ANO INT,
        TP_FAIXA_ETARIA INT,
        TP_SEXO VARCHAR(1),
        TP_COR_RACA INT,
        TP_ESCOLA INT,
        TP_PRESENCA_CN INT,
        TP_PRESENCA_CH INT,
        TP_PRESENCA_LC INT,
        TP_PRESENCA_MT INT,
        CO_PROVA_CN INT,
        CO_PROVA_CH INT,
        CO_PROVA_LC INT,
        CO_PROVA_MT INT,
        NU_NOTA_CN FLOAT,
        NU_NOTA_CH FLOAT,
        NU_NOTA_LC FLOAT,
        NU_NOTA_MT FLOAT,
        TP_STATUS_REDACAO INT,
        NU_NOTA_REDACAO FLOAT,
        Q001 VARCHAR(1),
        Q002 VARCHAR(1),
        Q003 VARCHAR(1),
        Q004 VARCHAR(1),
        Q005 VARCHAR(1),
        Q006 VARCHAR(1)
    )
    """
    
    connection = None  # Inicialize a variável connection como None
    
    try:
        # Conectando ao MySQL
        connection = mysql.connector.connect(
            host='mysql',  
            user='user',    
            password='root', 
            database='ENEM'
        )

        cursor = connection.cursor()

        # Criar a tabela se não existir
        cursor.execute(create_table_query)
        connection.commit()

        # Escrevendo os dados linha a linha
        for row in df.collect():
            # Montar a consulta SQL
            insert_query = """INSERT INTO ENEM_TABLE (NU_INSCRICAO, NU_ANO, TP_FAIXA_ETARIA, TP_SEXO, 
                             TP_COR_RACA, TP_ESCOLA, TP_PRESENCA_CN, TP_PRESENCA_CH, 
                             TP_PRESENCA_LC, TP_PRESENCA_MT, CO_PROVA_CN, CO_PROVA_CH, 
                             CO_PROVA_LC, CO_PROVA_MT, NU_NOTA_CN, NU_NOTA_CH, NU_NOTA_LC, 
                             NU_NOTA_MT, TP_STATUS_REDACAO, NU_NOTA_REDACAO, Q001, 
                             Q002, Q003, Q004, Q005, Q006)
                             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                             %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

            # Execute a consulta
            cursor.execute(insert_query, tuple(row))

        connection.commit()  # Salvar as alterações
        print('Dados inseridos com sucesso no MySQL')

    except Error as e:
        print(f'Erro ao conectar ao MySQL: {e}')
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


if __name__ == "__main__":
    main()
