CREATE TABLE IF NOT EXISTS transacoes (
                id SERIAL PRIMARY KEY,
                score_1 INT,
                score_2 FLOAT,
                score_3 FLOAT,
                score_4 FLOAT,
                score_5 FLOAT,
                score_6 FLOAT,
                pais TEXT,
                score_7 INT,
                produto TEXT,
                categoria_produto TEXT,
                score_8 FLOAT,
                score_9 FLOAT,
                score_10 FLOAT,
                entrega_doc_1 INT,
                entrega_doc_2 TEXT,
                entrega_doc_3 TEXT,
                data_compra TEXT,
                valor_compra FLOAT
            );