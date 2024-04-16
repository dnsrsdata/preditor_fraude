CREATE TABLE IF NOT EXISTS previsoes (
                id SERIAL PRIMARY KEY,
                transacao_id INT,
                predicao INT
            );