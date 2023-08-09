import pandas as pd
import numpy as np

class manipulation:
    
    def __init__(self, df_base):
        self.df_base = df_base

    def dt_hoje(self):
        self.hoje = pd.to_datetime('today')
    
    def tratamento_base(self):
        self.__tratamento_inicial_base()
        self.df_base['hoje'] = hoje
        hoje = pd.to_datetime('today')
        self.__criando_indicadores_base()
        return self.df_base

    def __tratamento_inicial_base(self):
        try:
            for campo in self.colunas_interesse[:3]:
                self.df_base[campo] = self.df_base[campo].str[:10]
                self.df_base[campo] = pd.to_datetime(self.df_base[campo], format='%d/%m/%Y', errors='raise')
            print('tratamento inicial base - sucesso')
        except:
            print('tratamento inicial base - erro')
        return print("tratamento inicial base - concluido")
    
    def __criando_indicadores_base(self):
        try:
            self.df_base = self.df_base.loc[(self.df_base['DTEXCLUSAO'].isnull())].reset_index(drop=True)
            self.df_base['temp_empresa'] = self.df_base.apply(lambda x: (x['hoje'] - x['DTCADASTRO']).days/30, axis = 1)
            self.df_base['temp_empresa'] = self.df_base['temp_empresa'].map(lambda x: int(round(x,0)))
            self.df_base['dias_ult_comp'] = self.df_base.apply(lambda x: (x['hoje'] - x['DTULTCOMP']),axis = 1)
            self.df_base['dias_ult_comp'] = self.df_base.apply(lambda x: (x['hoje'] - x['DTULTCOMP']) if pd.isnull(x['DTULTCOMP']) else x['dias_ult_comp'], axis=1)
            self.df_base['dias_ult_comp'] = self.df_base['dias_ult_comp'].map(lambda x: x.days)
            self.df_base['inativos'] = self.df_base['dias_ult_comp'].apply(lambda x: (x-90) if x>90 else 0)
            self.df_base['hoje'] = pd.to_datetime(self.df_base['hoje'],format='%d/%m/%Y', errors='raise')
            self.df_base['Sit'] = self.df_base['dias_ult_comp'].map(lambda x: 'Inativo' if x>90 else ('Ativo' if x<=90 else 'não comprou'))

            def flag_clientes(df):
                if df['dias_ult_comp'] <=80:
                    return 'Ativo'
                elif ((df['dias_ult_comp'] >80)&(df['dias_ult_comp']<=90)):
                    return 'Proximo a inativar'
                elif ((df['dias_ult_comp'] >90)&(df['dias_ult_comp']<=180)):  
                    return 'Inativo 90 a 180 dias'
                else :
                    return 'Mais 180 dias'
            
            self.df_base['flag'] = self.df_base.apply(flag_clientes, axis=1)
            print("criação de indicadores - sucesso")
        except:
            print('criação de indicadores - erro')
        return print("criação de indicadores - concluido")

    
    def tratamento_agg(self):
        self.df_emails = pd.read_csv('emails.csv', sep=';')
        self.__tratamento_inicial_emails_agg()
        self.__criando_flags_agg()
        self.__indicadores_agg()
        self.__merge_emails_agg()
        return self.df_agg
    
    def __tratamento_inicial_emails_agg(self):
        self.df_emails = self.df_emails.replace(np.nan, '', regex=True)
        return print("tratamento inicial emails - concluido")
    
    def lista_emails_agg(self):
        return self.df_emails['email'].tolist()

    def __criando_flags_agg(self):
        try:
            date_col  = pd.DatetimeIndex(self.df_base['DTCADASTRO'])
            self.df_base['mes_cad'] = date_col.month
            self.df_base['Ano_cad'] = date_col.year

            date_col = pd.DatetimeIndex(self.df_base['DTEXCLUSAO'])
            self.df_base['mes_exclusao'] = date_col.month
            self.df_base['Ano_exclusao'] = date_col.year

            date_col = pd.DatetimeIndex(self.df_base['hoje'])
            self.df_base['hoje_Mes'] = date_col.month
            self.df_base['hoje_ano'] = date_col.year

            def qtdcad(df_cad):
                if ((df_cad['hoje_ano'] == df_cad['Ano_cad']) & (df_cad['mes_cad']==df_cad['hoje_Mes'])):
                    return 1
                else:
                    return 0 
                
            def qtdexcluido(df_excl):
                if ((df_excl['hoje_ano'] == df_excl['Ano_exclusao']) & (df_excl['mes_exclusao']==df_excl['hoje_Mes'])):
                    return 1
                else:
                    return 0 
            
            self.df_base['novos_cad'] = self.df_base.apply(qtdcad, axis=1)
            self.df_base['qtd_excluido'] = self.df_base.apply(qtdexcluido, axis=1)

            def ativos(x):
                return len( x.loc[x=='Ativo'])
            def novos_cadastros(x):
                return len(x.loc[x==1]) 
            def cad_excluidos(x):
                return len(x.loc[x==1])   
            def inativos(x):
                return len( x.loc[x=='Inativo'])
            def px_inat(x):
                return len( x.loc[x=='Proximo_a_inativar'])
            def a90_a_180(x):
                return len( x.loc[x=='Inativo_90_a_180_dias'])
            def a180(x):
                return len( x.loc[x=='Mais_180_dias']) 
            
            self.df_agg = self.df_base.groupby(['NOMEGERENTE','SUPERV','CONSULTOR']).agg({'Sit':[ativos,inativos],'flag':[px_inat,a90_a_180,a180],'novos_cad':[novos_cadastros],'qtd_excluido':[cad_excluidos]})
            self.df_base.drop(columns=['DTEXCLUSAO','hoje','mes_cad','Ano_cad','mes_exclusao','Ano_exclusao', 'hoje_Mes', 'hoje_ano', 'novos_cad', 'qtd_excluido', 'temp_empresa'],inplace=True)
            self.df_agg.columns=['Ativos','Inativos','px_a_inativar','px_90_a_180_dias', 'maior_180_dias','novos_cad','qtd_excluidos']
            self.df_agg = self.df_agg.loc[self.df_agg['Ativos'] >0].reset_index()
            print("criação de flags - sucesso")
        except:
            print('criação de flags - erro')
        return print("criação de flags - concluido")
    
    def __indicadores_agg(self):
        try:
            self.df_agg['pc_inativos'] = self.df_agg.apply(lambda x: (x['Inativos'] / x['Ativos']),axis=1)
            self.df_agg['pc_px_inativos'] = self.df_agg.apply(lambda x: (x['px_a_inativar'] / x['Ativos']),axis=1)

            def formatar(valor):
                return '{: ,.2%}'.format(valor)
            
            self.df_agg['pc_inativos'] = self.df_agg['pc_inativos'].apply(formatar)
            self.df_agg['pc_px_inativos'] = self.df_agg['pc_px_inativos'].apply(formatar)
            self.df_agg = self.df_agg.loc[self.df_agg['Ativos'] >0].reset_index()
            print("criação de indicadores - sucesso")
        except:
            print('criação de indicadores - erro')
        return print("criação de indicadores - concluido")
    
    def __merge_emails_agg(self):
        try:
            self.df_agg = self.df_agg.merge(self.df_emails, on='SUPERV', how='left')
            self.df_agg.drop(columns=['level_0','index'], inplace=True)
            self.df_agg['emails'] = self.df_agg['emails'].fillna('Nao encontrado')
            self.df_agg.columns=['Gerente','Supervisor','Consultor','Ativos','Inativos','Proximos a Inativar','90 A 180 Dias','Maior 180 dias','Novos Cadastros','Excluidos','% Inativos','% Px a Inativar','Email']
            print("merge emails - sucesso")
        except:
            print('merge emails - erro')
        return print("merge emails - concluido")