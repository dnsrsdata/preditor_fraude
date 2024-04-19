import os
import joblib
import uvicorn
import asyncpg
import pandas as pd
from fastapi import FastAPI
from dotenv import load_dotenv
from pydantic import BaseModel
from src.build_features.preprocess import (
    make_continents,
    make_time_based_cols,
    fill_nans,
    drop_unused_cols
)

# Iniciando a API
api = FastAPI()

# Carregando as variáveis de conexão do BD
load_dotenv()
username = os.environ.get('USERNAME')
password = os.environ.get('PASSWORD')
host = os.environ.get('HOST')
db_name = os.environ.get('DATABASE')
port = os.environ.get('PORT')

# Definindo o tipo padrão das variáveis de entrada conforme os dados raw
class Transacao(BaseModel):

    score_1: int
    score_2: float
    score_3: float
    score_4: float
    score_5: float
    score_6: float
    pais: object
    score_7: int
    produto: object
    categoria_produto: object
    score_8: float
    score_9: float
    score_10: float
    entrega_doc_1: int
    entrega_doc_2: object
    entrega_doc_3: object
    data_compra: object
    valor_compra: float

# Criando um processo para mandar as transações para um BD
async def armazenar_dados(transacao: dict, predicao: int):

    # Conectando ao banco de dados
    conn = await asyncpg.connect(f"postgresql://{username}:{password}@{host}:{port}/{db_name}?sslmode=require")

    try:
        # Inserindo os dados da transação na tabela principal
        transacao_id = await conn.fetchval(
            """
            INSERT INTO transacoes (
                score_1, score_2, score_3, score_4, score_5, score_6, pais, score_7,
                produto, categoria_produto, score_8, score_9, score_10, entrega_doc_1,
                entrega_doc_2, entrega_doc_3, data_compra, valor_compra
            ) VALUES (
                $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18
            ) RETURNING id
            """,
            *transacao.values()
        )

        # Inserindo a previsão associada ao ID da transação na tabela de previsões
        await conn.execute(
            """
            INSERT INTO previsoes (transacao_id, predicao) VALUES ($1, $2)
            """,
            transacao_id, predicao
        )

    finally:
        # Fechar a conexão com o banco de dados
        await conn.close()


# Definindo a API
@api.post("/prever")
async def prever_fraude(transacao: Transacao):
    
    # Carregando o modelo
    pipeline = joblib.load("models/pipe.pkl")
    
    # Carregando os dados no formato json
    json = transacao.model_dump()

    # Convertendo em dataframe
    data = pd.DataFrame.from_dict([json])

    # Criando a coluna 'continente'
    data["continente"] = make_continents(data, "pais")
     
    # Criando as colunas baseadas na coluna datetime
    data = make_time_based_cols(data, "data_compra") 
    
    # Definindo as colunas para preenchimentop de missing
    cols_to_fill = ["entrega_doc_1", "entrega_doc_2", "entrega_doc_3"] 
    
    # Preenchendo o missing
    data[cols_to_fill] = fill_nans(data, cols_to_fill) 
    
    # Definindo as colunas para dropar
    cols_to_drop = ["produto", "data_compra"] 
    
    # Dropando as colunas
    data = drop_unused_cols(data, cols_to_drop)
    
    # Calculando a previsão
    label = (pipeline.predict_proba(data)[:, 1] >= 0.66).astype(int)
    
    # Salvando a previsão e a info dos dados no banco de dados
    await armazenar_dados(json, label)
    
    return {"Predicao": str(label)}


if __name__ == "__main__":

    uvicorn.run(api, host="0.0.0.0", port=8000)
