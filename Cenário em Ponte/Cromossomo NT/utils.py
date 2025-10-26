import pandas as pd
import numpy as np
import os
import math

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

def ler_componentes_excel(caminho_excel):
    df = pd.read_excel(caminho_excel)
    return [Componente(row["confiabilidade"], row["custo"], row["peso"]) for _, row in df.iterrows()]

def ler_individuos_excel(caminho_excel, componentes, custo_max, peso_max):
    df = pd.read_excel(caminho_excel)
    individuos = []
    for _, row in df.iterrows():
        tipos = eval(row["solucao_tipos"])
        quantidades = eval(row["solucao_quantidades"])
        solucao = np.vstack([tipos, quantidades])
        individuo = Individuo(solucao, componentes, custo_max, peso_max)
        individuos.append(individuo)
    return individuos