import hydra
import numpy as np
import pandas as pd

def read_data(datapath_raw:str, file_raw:str):
    """Lê os dados raw

    Args:
        datapath_raw (str): path para os dados raw
        file_raw (str): nome do arquivo raw

    Returns:
        pd.DataFrame: dataset com os dados
    """ 
    return pd.read_csv(f"{datapath_raw}/{file_raw}.csv")

def save_data(dataset:pd.DataFrame, datapath_processed:str, filename:str):
    """Lê os dados raw

    Args:
        dataset (pd.DataFrame): conjunto de dados que será salvo
        datapath_processed (str): path para a pasta onde os dados serão salvos
        filename (str): nome do arquivo 

    Returns:
    """ 
    return dataset.to_csv(f"{datapath_processed}/{filename}.csv")


def make_continents(dataset:pd.DataFrame, col_name:str):
    """Retorna o continente de cada país 

    Args:
        dataset (pd.DataFrame): conjunto de dados
        col_name (str): nome da coluna com a sigla dos países

    Returns:
        pd.Series: serie pandas com o nome dos continentes de cada registro
    """
    america = ['US', 'MX', 'CA', 'PR', 'BR', 'AR', 'UY', 'CO', 'CL', 'PE', 'PY', 'EC', 'BO', 'CR', 'PA', 'HN', 'NI', 'BS', "DO"]
    europa = ['SE', 'RU', 'ES', 'GB', 'FR', 'IT', 'PT', 'DE', 'UA', 'BE', 'CH', 'NL', 'AE', 'AD', 'GE', 'GR', 'TR', 'FI', 'NO', 'IL']
    asia = ['CN', 'KR', 'IN', 'TW', "JP", "LB", "PH"]
    oceania = ['AU', 'NZ']
    africa = ['ZA', 'EG', 'GH']

    # Definindo uma função para aplicar o agrupamento
    continent_encoder = lambda sigla: "Africa" if sigla in africa else("Oceania" if sigla in oceania else ("Asia" if sigla in asia else ("America" if sigla in america else ("Europa" if sigla in europa else np.nan))))

    # Aplicando a função
    return dataset[col_name].apply(continent_encoder)

def make_time_based_cols(dataset:pd.DataFrame, col_name:str):
    """cria colunas derivadas da coluna original de tempo

    Args:
        dataset (pd.DataFrame): conjunto de dados 
        col_name (str): coluna contendo os dados no formato datetime

    Returns:
       pd.DataFrame: dataset contendo as colunas modificadas
    """
    # Mudando o tipo para datetime
    dataset[col_name] = pd.to_datetime(dataset[col_name])
    
    # Dividindo a coluna de data em novos valores
    dataset["dia_compra"] = dataset[col_name].dt.day
    dataset["nome_dia_compra"] = dataset[col_name].dt.day_name()
    dataset["hora_compra"] = dataset[col_name].dt.hour

    # Criando novas features a partir das colunas
    weekend = ["Saturday", "Sunday"]
    dataset["dia_compra_classe"] = dataset["nome_dia_compra"].apply(lambda dia: "Fim de semana" if dia in weekend else "Dia de semana")

    # Dividindo os horários em turnos
    madrugada = [0, 1, 2, 3, 4, 5]
    manha = [6 ,7 , 8, 9, 10, 11, 12]
    tarde = [13, 14, 15, 16, 17]
    dataset["turno_compra"] = dataset["hora_compra"].apply(lambda hora: "madrugada" if hora in madrugada else("manha" if hora in manha else("tarde" if hora in tarde else "noite")))

    # Criando variável de hora comercial
    dataset["horario_comercial_compra"] = dataset["hora_compra"].apply(lambda hora: "Comercial" if 8 <= hora >= 18 else "Não Comercial")

    return dataset

def fill_nans(dataset:pd.DataFrame, entrega_docs:list):
    """Preenche os valores ausentes das colunas especificadas para 'N'

    Args:
        dataset (pd.DataFrame): conjunto de dados
        entrega_docs (list): lista com as colunas referentes a documentação

    Returns:
        pd.Series: colunas com os valores ausentes preenchidos
    """
    return dataset[entrega_docs].fillna("N")

def drop_unused_cols(dataset:pd.DataFrame, cols_to_drop:list):
    """Dropa as colunas que não serão utilizadas

    Args:
        dataset (pd.DataFrame): _description_
        cols_to_drop (list): _description_

    Returns:
        _type_: _description_
    """
    return dataset.drop(cols_to_drop, axis=1)

@hydra.main(config_path="../../conf", config_name="config", version_base=None)
def main(cfg):
    
    # Lendos os dados
    data = read_data(f"{cfg.paths.data_raw}", f"{cfg.arquivos.raw}")
    
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
    
    # Salvando os dados
    save_data(data, f"{cfg.paths.data_processed}", f"{cfg.arquivos.processed}")

if __name__=="__main__":
    main()

