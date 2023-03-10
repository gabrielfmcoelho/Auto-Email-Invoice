from query import Query # Classe para execução de SQL.
from manipulation import manipulation # Classe para manipulação de dados.
from emailcon import emailcon # Classe para envio de emails.

if __name__ == "__main__":

    with open('consulta.txt','r', encoding='utf8') as f: # Abre o arquivo
        query_sql = f.read()

    #Query.query_teste(query_sql)
    df_base = Query.query(query_sql)

    manipulacao = manipulation(df_base)
    df_base = manipulacao.tratamento_base(df_base)
    df_agg = manipulacao.tratamento_agg()
    hoje = manipulacao.dt_hoje()
    emails = manipulacao.lista_emails_agg()

    envio = emailcon(emails, hoje, df_base, df_agg)
    envio.enviar_emails()