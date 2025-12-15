import pandas as pd
import numpy as np
import os
import math
import re

from Geradores.GeradorComponentes import Componente
from Geradores.GeradorIndividuos import Individuo

def truncate(number, decimals=0):
    factor = 10 ** decimals
    return math.trunc(number * factor) / factor

def limpar_diretorio(caminho):
    """Limpa todos os arquivos de um diretório específico"""
    if os.path.exists(caminho):
        for arquivo in os.listdir(caminho):
            caminho_arquivo = os.path.join(caminho, arquivo)
            try:
                if os.path.isfile(caminho_arquivo):
                    os.unlink(caminho_arquivo)
            except Exception as e:
                print(f'Erro ao deletar {caminho_arquivo}: {e}')

def junta_excels(caminho_pasta, nome_arquivo_saida):
    arquivos = [f for f in os.listdir(caminho_pasta) if f.endswith('.xlsx')]
    arquivos.sort(key=lambda x: int(re.findall(r'pop_(\d+)', x)[0]))
    df_final = None
    for arquivo in enumerate(arquivos):
        numero = arquivo[1].replace('resultados_parametros_pop_', '').replace('.xlsx', '')
        df = pd.read_excel(os.path.join(caminho_pasta, arquivo[1]), dtype=str)  # Lê os valores como string para preservar precisão
        if df_final is None:
            col = df.columns[0]
            df_final = pd.DataFrame({'Params': df[col]})
        col = df.columns[1]
        df_final[f'pop{numero}'] = df[col]
    df_final.to_excel(os.path.join(caminho_pasta, nome_arquivo_saida), index=False)
    print(f'Junção de excel no arquivo {nome_arquivo_saida} gerado com sucesso!')

def ler_componentes_excel(caminho_excel):
    df = pd.read_excel(caminho_excel)
    return [Componente(row["confiabilidade"], row["custo"], row["peso"]) for _, row in df.iterrows()]

def ler_individuos_excel(caminho_pasta, componentes, custo_max, peso_max):
    #encontrar todos os arquivos xlsx na pasta que possuem nome iniciando com "individuos"
    arquivos = [f for f in os.listdir(caminho_pasta) if f.startswith("individuos") and f.endswith(".xlsx")]
    if len(arquivos) == 0:
        raise FileNotFoundError("Nenhum arquivo de indivíduos encontrado na pasta especificada.")
    populacoes = []
    for arquivo in arquivos:
        df = pd.read_excel(os.path.join(caminho_pasta, arquivo))
        individuos = []
        for _, row in df.iterrows():
            tipos = eval(row["solucao_tipos"])
            quantidades = eval(row["solucao_quantidades"])
            solucao = np.vstack((tipos, quantidades))
            individuo = Individuo(solucao, componentes, peso_max, custo_max)
            individuos.append(individuo)
        populacoes.append(individuos)
    return populacoes