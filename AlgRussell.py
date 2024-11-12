'''
Olá pessoal, este código tem como finalidade exercitar um pouco mais do domínio de modelagem de dados a partir das bibliotecas pandas e numpy, trata-se de uma resolução para o problema de transporte denominado
Método de Russell.
'''

#imports
import pandas as pd
import numpy as np

#Criando um df de saída
out = pd.DataFrame(columns= ["CDs", "Clientes", "Quant"])
out2 = pd.DataFrame(columns= ["CDs", "Clientes", "Quant"])
#Inputs dados
df_demanda = pd.read_excel("Demanda.xlsx")
df_distancia = pd.read_excel("Distancia.xlsx")
df_estoque = pd.read_excel("Estoque.xlsx")
df_frete = pd.read_excel("Frete.xlsx")

#Calculando o valor de frete para cada cliente
df_distancia["R$/Km"] = df_distancia["Saida"].apply(lambda x: df_frete["R$/Km"].loc[df_frete["CDs"] == x].values[0])
df_distancia["Frete"] = df_distancia["Km"] * df_distancia["R$/Km"]

#Função que receberá os inputs
def AlgRussell(df_distancia, df_demanda, df_estoque, df_out):
    
    while True:
        #Calculando o mi (maior custo CD x Clientes)
        df_mi = pd.DataFrame(df_estoque["CDs"])
        df_mi["mi"] = df_mi["CDs"].apply(lambda x: df_distancia["Frete"].loc[df_distancia["Saida"] == x].max())

        #Calculando o mx (maior custo Cliente x CDs)
        df_mx = pd.DataFrame(df_demanda["Cliente"])
        df_mx["mx"] = df_mx["Cliente"].apply(lambda x: df_distancia["Frete"].loc[df_distancia["Destino"] == x].max())

        #Criando listas dos CDs e Clientes
        list_cd = list(df_estoque["CDs"])
        list_clientes = list(df_demanda["Cliente"])

        list_np = []

        #criando os inputs para criação da matriz de penalidades
        for cd in list_cd:
            list_np2 = []

            for x, line2 in pd.DataFrame(df_distancia.loc[df_distancia["Saida"] == cd]).iterrows():

                out = line2["Frete"] - df_mi["mi"].loc[df_mi["CDs"] == line2["Saida"]].values[0] - df_mx["mx"].loc[df_mx["Cliente"] == line2["Destino"]].values[0]
                list_np2.append(out)
            
            list_np.append(list_np2)

        #Criando a matriz de penalidades e alterando os valores respectivamente com as saídas
        matriz = np.array(list_np)

        #Verificando se o menor valor da matriz não se repete
        count_matriz_min = np.count_nonzero(matriz == matriz.min())

        if count_matriz_min > 1:

            #Quando menor valor se repetir, deve-se selecionar pelo menor custo do frete entre os repetidos
            list_pos_min_matriz = []
            cursor = 0
            
            while cursor + 1 <= count_matriz_min:
                pos_min_matriz = np.where(matriz == matriz.min())
                cd_min_matriz = list_cd[pos_min_matriz[0][cursor]]
                cliente_min_matriz = list_clientes[pos_min_matriz[1][cursor]]
                frete_min_matriz = df_distancia['Frete'].loc[(df_distancia['Saida'] == cd_min_matriz) & (df_distancia["Destino"] == cliente_min_matriz)].values[0]
                list_pos_min_matriz.append(frete_min_matriz)
                cursor += 1

            cursor_list_pos_min_matriz = np.argmin(list_pos_min_matriz)
            cd_min_matriz = list_cd[pos_min_matriz[0][cursor_list_pos_min_matriz]]
            cliente_min_matriz = list_clientes[pos_min_matriz[1][cursor_list_pos_min_matriz]]
            
        else:
            
            #Consultando a posição do menor valor dentro da matriz
            pos_min_matriz = np.where(matriz == matriz.min())
            cd_min_matriz = list_cd[pos_min_matriz[0][0]]
            cliente_min_matriz = list_clientes[pos_min_matriz[1][0]]

        demanda_cliente_min_matriz = df_demanda["Quant"].loc[df_demanda["Cliente"] == cliente_min_matriz].values[0]
        estoque_cd_min_matriz = df_estoque["Quant"].loc[df_estoque["CDs"] == cd_min_matriz].values[0]

        
        if demanda_cliente_min_matriz >= estoque_cd_min_matriz:
            alt_quant = estoque_cd_min_matriz
            alt_cliente = demanda_cliente_min_matriz - estoque_cd_min_matriz
            alt_cd = 0
        else:
            alt_quant = demanda_cliente_min_matriz
            alt_cliente = 0
            alt_cd = estoque_cd_min_matriz - demanda_cliente_min_matriz
        

        #Criando as saídas
        df_out.loc[len(df_out)] = [cd_min_matriz, cliente_min_matriz, alt_quant]

        df_demanda.loc[df_demanda["Cliente"] == cliente_min_matriz, "Quant"] = alt_cliente
        df_estoque.loc[df_estoque["CDs"] == cd_min_matriz, "Quant"] = alt_cd

        df_demanda = df_demanda[df_demanda["Quant"] > 0]
        df_estoque = df_estoque[df_estoque["Quant"] > 0]
        df_distancia = df_distancia[(df_distancia["Saida"].isin(df_estoque["CDs"])) & (df_distancia["Destino"].isin(df_demanda["Cliente"]))]

        if df_demanda.empty or df_estoque.empty:
            break
        else: 
            continue

    return df_out


#Executando a função
result_russell = AlgRussell(df_distancia, df_demanda, df_estoque, out)
result_russell.to_excel("out_russell.xlsx", index= False)
