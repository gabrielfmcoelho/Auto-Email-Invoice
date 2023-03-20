from email.message import EmailMessage
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
import openpyxl
import ssl
import smtplib
import os
import time

class emailcon:
    
    def __init__(self, lista_emails, hoje, df_base, df_agg):
        self.df_base = df_base
        self.df_agg = df_agg
        self.hoje = hoje
        self.lista_emails = lista_emails
        with open('chave_de_acesso.txt','r', encoding='utf8') as f: # Abre o arquivo
            arquivo = f.readlines() # Le o arquivo
            self.email_remetente = arquivo[0] # Pega o email
            self.email_senha = arquivo[1] # Pega a senha

        self.email_destinatario = lista_emails # Transforma a coluna de emails do df_emails em uma lista e armazena

        self.Subject = f'Invoice base de clientes - {self.hoje.date()}'

    def enviar_emails(self):
        try:
            ultimo_gerente = ''
            for gerente in self.df_agg.Gerente.unique(): # Loop para percorrer todos os RCAs unicos na base
                print(f"Começando {gerente}")
                if gerente == ultimo_gerente:
                    continue  
                ultimo_gerente=gerente

                df_temp = self.df_agg.loc[(self.df_agg['Gerente'] == gerente)].copy().reset_index(drop=True) # Cria um df temporario com os dados do RCA atual
                
                df_temp2 = self.df_base.loc[(self.df_base['nomegerente'] == gerente)].copy().reset_index(drop=True) # Cria um df temporario com os dados dos clientes do RCA atual
                
                if df_temp.Email[0] == 'Nao encontrado': # Se o email do RCA atual nao for encontrado na base de emails, pula para o proximo RCA
                    continue # Pula para o proximo RCA

                msg = MIMEMultipart() # Cria o objeto msg
                msg['Subject'] = self.Subject # Adiciona o assunto ao objeto msg
                msg['From'] = self.email_remetente # Adiciona o email de remetente ao objeto msg
                msg['To'] = df_temp.Email[0] # Adiciona o email de destinatario ao objeto msg
                

                # Cria o corpo do email em html
                html = MIMEText(f""" 
                <html>
                    <head>
                        <style>
                            table {{
                                font-family: arial, sans-serif;
                                border-collapse: collapse;
                                width: 100%;
                            }}
                    
                            td, th {{
                                border: 1px solid #dddddd;
                                text-align: left;
                                padding: 8px;
                            }}
                        
                            tr:nth-child(even) {{
                                background-color: #dddddd;
                                }}
                        </style>
                    </head>
                    <body>
                            
                        <h2>Base de clientes - {self.hoje.date()}</h2>
                        
                        <p>Prezado(a) {df_temp.Supervisor[0]},</p>
                        <p>Segue em anexo a base de clientes atualizada por consutor</p>
                        <p>Logo abaixo no corpo deste email segue o resumo dos clientes categorizados:</p>

                        {df_temp.drop(columns='Email').to_html(index=False)}
                            
                    </body>
                </html>
                """, 'html')

                msg.attach(html) # Adiciona o corpo do email ao objeto msg
                
                os.makedirs('./rcas', exist_ok=True) # Cria a pasta para armazenar as planilhas temporarias de excel dos rcas caso nao exista
                df_temp3 = self.df_base.loc[(self.df_base['superv'] == gerente)].copy().reset_index(drop=True) # Cria um df df_finalorario com os dados de todos os clientes do RCA atual
                df_temp3.to_excel(f'./rcas/base_clientes_{gerente}.xlsx', index=False) # Cria uma planilha de excel temporaria com os dados de todos os clientes do RCA atual

                with open(f'./rcas/base_clientes_{gerente}.xlsx', 'rb') as f: # Abre a planilha de excel temporaria do RCA atual
                    xlsx = MIMEApplication(f.read()) # Cria o objeto xlsx com os dados da planilha de excel temporaria do RCA atual
                    xlsx.add_header('Content-Disposition', 'attachment', filename=f'base_clientes_{gerente}_{self.hoje.date()}.xlsx') # Adiciona o nome da planilha de excel temporaria do RCA atual ao objeto xlsx
                    msg.attach(xlsx) # Adiciona a planilha de excel temporaria do RCA atual ao objeto msg
                
                msg = msg.as_string() # Converte o objeto msg para string
                msg = msg.encode('utf-8') # Codifica o objeto msg para utf-8

                context = ssl.create_default_context() # Cria certificado ssl para segurança da conexão

                with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp: # Conecta ao servidor smtp do gmail
                    try: # Tenta logar no gmail
                        smtp.login(self.email_remetente, self.email_senha) # Loga no gmail
                    except: # Se nao conseguir logar no gmail, aguarda 5 minutos e tenta novamente
                        #print('Erro ao logar no gmail, aguardando 5 minutos para tentar novamente') # Descomentar para ver o erro
                        time.sleep(300)  # Aguarda 5 minutos
                        smtp.login(self.email_remetente, self.email_senha) # Loga no gmail
                    try: # Tenta enviar o email
                        smtp.sendmail(self.email_remetente, df_temp.Email[0], msg) # Envia o email
                        print(f'Enviado para {gerente} pelo contato:', df_temp.Email[0]) # Descomentar para ver o email enviado
                    except: # Se nao conseguir enviar o email apresenta o erro
                        #print('Erro ao enviar para: ', df_temp.Email[0]) # Descomentar para ver o erro
                        pass # Passa para o proximo loop

                os.remove(f'./rcas/base_clientes_{gerente}.xlsx') # Apaga a planilha de excel temporaria do RCA atual
            
            #fim do loop
        except:
            print('Erro ao enviar os emails')
            pass
