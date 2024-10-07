# Dockerfile para o projeto de ETL utilizando PySpark
FROM apache/spark-py:latest

USER root

# Cria um diretório de trabalho dentro do contêiner
RUN mkdir -p /app/staging/DADOS
WORKDIR /app

# Copia o arquivo CSV de dados para o diretório de trabalho
COPY staging/DADOS/MICRODADOS_ENEM_2020.csv ./staging/DADOS/

# Copia o script do ETL para o diretório de trabalho
COPY etl.py ./etl.py

# Instala o PySpark e outras dependências
RUN pip install pyspark mysql-connector-python

# Executa o script Python quando o contêiner for iniciado
CMD ["sh", "-c", "python3 etl.py"]
