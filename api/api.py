import joblib
import uvicorn
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel
from src.build_features.preprocess import (
    make_continents,
    make_time_based_cols,
    fill_nans,
    drop_unused_cols
)

api = FastAPI()


# Definindo o tipo padrão das variáveis conforme os dados raw
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


# Definindo a API
@api.post("/prever")
def prever_fraude(transacao: Transacao):
    
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
    print("As colunas indo para a previsão são:", data.columns)
    
    # Calculando a previsão
    prob = (pipeline.predict_proba(data)[:, 1] >= 0.66).astype(int)
    
    return {"Predicao": str(prob)}


if __name__ == "__main__":

    uvicorn.run(api, host="0.0.0.0", port=8000)
