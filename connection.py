import oracledb as db
from sqlalchemy import create_engine

class DBConnection:

    def __init__(self):
        with open('chave_de_acesso.txt','r', encoding='utf8') as f: # Abre o arquivo
            arquivo = f.readlines() # Le o arquivo
            conn_string = arquivo[2] 
        self.__connection_string = conn_string
        self.__engine = self.__create_database_engine()

    def __create_database_engine(self):
        lib_dir_oracle = r"C:\Oracle\instantclient_19_9"
        db.init_oracle_client(lib_dir=lib_dir_oracle)
        engine = create_engine(self.__connection_string)
        return engine

    def __enter__(self):
        return self.__engine.connect()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__engine.dispose()