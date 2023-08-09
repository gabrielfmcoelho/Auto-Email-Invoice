from connection import DBConnection
import pandas as pd

class Query:

    def query_teste(self):
        with DBConnection() as conn:
            try:
                response = conn.execute(self)
                if response.rowcount > 0:
                    print("Comando SQL executado corretamente.")
                    response.close()
                    return 1
                else:
                    print("Ocorreu um erro ao executar o comando SQL.")
                    response.close()
                    return 0
            except Exception as e:
                print("Ocorreu um erro na execução do SQL:", e)

    def query(self):
        with DBConnection() as conn:
            df_base = pd.read_sql_query(self, conn)
            print(df_base)
            return df_base