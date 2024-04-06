#import joblib
from fastapi import FastAPI
from pydantic import BaseModel
#import pandas as pd

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
    print(transacao)
    
    return {"mensagem": "Transacao concluída com sucesso"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(api, host="0.0.0.0", port=8000)