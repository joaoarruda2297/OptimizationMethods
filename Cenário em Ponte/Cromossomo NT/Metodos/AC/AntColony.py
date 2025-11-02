from collections import defaultdict
import numpy as np
import math
import random
import os
from decimal import Decimal
from copy import deepcopy
import matplotlib.pyplot as plt
from contextlib import redirect_stdout
import sys
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Geradores.GeradorIndividuos import Individuo
from Geradores.GeradorGraficos import GeradorGraficos
from utils import truncate

class SolucaoMapa:
    def __init__(self, tipo_componente, quantidade_componente, ferormonio):
        self.tipo_componente = tipo_componente
        self.quantidade_componente = quantidade_componente
        self.ferormonio = ferormonio
        self.probabilidade = 0

class AntColonyOptimization:
    def __init__(self, componentes, individuos, peso_max, custo_max, num_geracoes, num_tipos_componentes, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema, evaporacao=None):
        self.num_formigas = len(individuos)
        self.num_variaveis = num_variaveis
        self.num_geracoes = num_geracoes
        self.num_tipos_componentes = num_tipos_componentes
        self.componentes = componentes
        self.peso_max = peso_max
        self.custo_max = custo_max
        self.num_max_componentes_subsistema = num_max_componentes_subsistema
        self.num_min_componentes_subsistema = num_min_componentes_subsistema
        self.evaporation_rate = evaporacao if evaporacao is not None else 0.5

        self.individuos = []
        for i in range(self.num_formigas):
            self.individuos.append(deepcopy(individuos[i]))
        self.individuos = sorted(self.individuos, key=lambda x: x.valor_funcao_objetivo, reverse=True)

    def heuristica(self, tipo):
        # Heurística baseada na confiabilidade do componente
        return float(self.componentes[tipo].confiabilidade)

    def construir_mapa_solucoes(self):
        mapa_solucoes = []
        for i in range(len(self.componentes)):
            for quantidade in range(self.num_max_componentes_subsistema):
                solucao_mapa = SolucaoMapa(i, quantidade + 1, 0.01)
                mapa_solucoes.append(solucao_mapa)
        return mapa_solucoes

    def construir_solucao_por_mapa(self, mapa):
        novas_solucoes = []
        for _ in range(self.num_formigas):
            nova_solucao = self.construir_solucao_unica_por_mapa(mapa)
            individuo = Individuo([np.array(nova_solucao[0]), np.array(nova_solucao[1])], self.componentes, self.peso_max, self.custo_max)
            novas_solucoes.append(individuo)
        return novas_solucoes

    def construir_solucao_unica_por_mapa(self, mapa):
        nova_solucao = [[], []]
        #vetor de probabilidades encaixada diretamente com o vetor mapa, logo index = 0 significa nó 0 do mapa = tipo 0, quantidade 1
        probabilidades = []
        probabilidade_total = float(0)
        for noh in mapa:
            probabilidade_atual = float((noh.ferormonio) * (self.heuristica(noh.tipo_componente)))
            probabilidade_total += probabilidade_atual
            probabilidades.append(probabilidade_atual)
        
        for noh in range(len(mapa)):
            if probabilidade_total == 0:
                probabilidades[noh] = 0
            else:
                probabilidades[noh] /= probabilidade_total
        
        index_escolhidos = []
        for _ in range(self.num_variaveis):
            index_escolhido = np.random.choice(range(len(probabilidades)), p=probabilidades)
            index_escolhidos.append(index_escolhido)

        for indice in index_escolhidos:
            noh = mapa[indice]
            nova_solucao[0].append(noh.tipo_componente)
            nova_solucao[1].append(noh.quantidade_componente)

        return nova_solucao

    def atualizar_feromonio(self, populacao, mapa):
        for individuo in populacao:
            for i in range(self.num_variaveis):
                tipo = individuo.solucao[0][i]
                quantidade = individuo.solucao[1][i]
                index_mapa = tipo * self.num_max_componentes_subsistema + (quantidade - 1)
                delta_feromonio = 1 / (1 + math.exp(-individuo.valor_funcao_objetivo))
                mapa[index_mapa].ferormonio = (1 - self.evaporation_rate) * mapa[index_mapa].ferormonio + delta_feromonio

    def verifica_duplicados(self, populacao):
        solucoes_unicas = set()
        populacao_filtrada = []
        for individuo in populacao:
            chave_solucao = (tuple(individuo.solucao[0]), tuple(individuo.solucao[1]))
            if chave_solucao not in solucoes_unicas:
                solucoes_unicas.add(chave_solucao)
                populacao_filtrada.append(individuo)
        return populacao_filtrada

    def truncate(self, number, decimals=0):
        factor = 10 ** decimals
        return math.trunc(number * factor) / factor

def main(index, componentes, individuos, peso_max, custo_max, num_geracoes, num_tipos_componentes, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema, estudo_parametro=False, evaporacao=None):
    aco = AntColonyOptimization(componentes, individuos, peso_max, custo_max, num_geracoes, num_tipos_componentes, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema, evaporacao)

    print("POPULAÇÃO INICIAL:")
    for l in range(len(aco.individuos)):
        print(f"Individuo {l+1}:")
        print(aco.individuos[l])
        print(" ")
    print(" ")

    numero_avaliacoes = 0
    solucoes_avaliacoes = []
    solucoes = []
    solucoes_log = []
    melhor_solucao_log = -10000
    melhor_solucao = -10000
    geracao = -1
    melhor_tempo = 0
    start_time = time.time()
    tempos_melhor_solucao = []

    mapa = aco.construir_mapa_solucoes()
    for l in range(len(mapa)):
        print("NOH:", l+ 1)
        print("Tipo:", mapa[l].tipo_componente)
        print("Quantidade:", mapa[l].quantidade_componente)
        print("Ferormonio:", mapa[l].ferormonio)
        print("")

    for i in range(aco.num_geracoes):
        print(f"GERACAO {i+1}")
        if i == 0:
            # Primeira geração: usa apenas a população inicial
            # Adiciona apenas o melhor indivíduo da geração
            melhor_individuo = aco.individuos[0]
            melhor_solucao = melhor_individuo.valor_funcao_objetivo
            melhor_solucao_log = math.log(melhor_solucao)
            geracao = i + 1
            solucoes_log.append(melhor_solucao_log)
            solucoes.append(melhor_solucao)
            solucoes_avaliacoes.append(melhor_solucao)
            melhor_tempo = time.time() - start_time
            tempos_melhor_solucao.append(time.time() - start_time)
        
        # Demais gerações: constrói novas soluções para cada formiga
        novas_solucoes = aco.construir_solucao_por_mapa(mapa)
        numero_avaliacoes += len(novas_solucoes)
        todas = aco.individuos + novas_solucoes
        todas = aco.verifica_duplicados(todas)
        todas = sorted(todas, key=lambda x: x.valor_funcao_objetivo, reverse=True)
        aco.individuos = todas[:aco.num_formigas]
        melhores = aco.individuos[:5]
        aco.atualizar_feromonio(melhores, mapa)

        print("Populacao final da era:")
        for l in range(len(aco.individuos)):
            print(f"Individuo {l+1}:")
            print(aco.individuos[l])
            print(" ")
        print("-----------------------------------------")

        for j in range(len(aco.individuos)):
            if(aco.individuos[j].valor_funcao_objetivo > melhor_individuo.valor_funcao_objetivo):
                log_individuo = math.log(aco.individuos[j].valor_funcao_objetivo)
                melhor_solucao_log = log_individuo
                melhor_individuo = aco.individuos[j]
                melhor_tempo = time.time() - start_time
                geracao = i + 1
        solucoes_log.append(melhor_solucao_log)
        solucoes.append(melhor_individuo.valor_funcao_objetivo)
        solucoes_avaliacoes.extend([melhor_individuo.valor_funcao_objetivo] * len(novas_solucoes))
        tempos_melhor_solucao.append(time.time() - start_time)

    aco.individuos = sorted(aco.individuos, key=lambda x: x.valor_funcao_objetivo, reverse=True)
    melhor_individuo = aco.individuos[0]

    print("O algoritmo ACO obteve em", aco.num_geracoes, "geracoes o resultado para a funcao objetivo de", aco.individuos[0].valor_funcao_objetivo)
    print("Com os seguintes valores para cada variavel de decisao:")
    for z in range(aco.num_variaveis):
        print(f"T{z+1}: {aco.individuos[0].solucao[0][z]}")
        print(f"Q{z+1}: {aco.individuos[0].solucao[1][z]}")
    print("\n")

    valor_final = truncate(aco.individuos[0].confiabilidade_total, 4)
    valor_final_log = truncate(melhor_solucao_log, 4)

    if not estudo_parametro:
        gerador_graficos = GeradorGraficos('./Metodos/AC/img/', 'blue')

        # Plotando o gráfico por geração
        gerador_graficos.gera_grafico(f'SolutionEvolutionACO{index}.png', range(0, aco.num_geracoes+1), solucoes, valor_final, geracao, 'Evolução da Melhor Solução ao Longo das Gerações (ACO)', 'Geração', 'Função Objetivo', show_plot=False)

        # Plotando o gráfico em log por geração
        gerador_graficos.gera_grafico(f'SolutionEvolutionACOLog{index}.png', range(0, aco.num_geracoes+1), solucoes_log, valor_final_log, geracao, 'Evolução da Melhor Solução ao Longo das Gerações (ACO)', 'Geração', 'log(Função Objetivo)', show_plot=False)

        # Plotando o gráfico com o número de avaliações
        gerador_graficos.gera_grafico(f'SolutionEvolutionACOAvaliacoes{index}.png', range(0, numero_avaliacoes+1), solucoes_avaliacoes, valor_final, geracao, 'Evolução da Melhor Solução ao Longo das Avaliações (ACO)', 'Número de Avaliações', 'Função Objetivo', 'Número de Avaliações: ' + str(numero_avaliacoes))

        #Plotando o gráfico com o tempo por funcao objetivo
        gerador_graficos.gera_grafico(f'SolutionEvolutionACOTempo{index}.png', tempos_melhor_solucao, solucoes, valor_final, geracao, 'Evolução do Tempo de Execução ao Longo das Gerações (ACO)', 'Tempo (s)', 'Função Objetivo', 'Tempo alcançado: ' + str(truncate(melhor_tempo,4)) + 's')

    return solucoes_log, valor_final_log, aco.individuos[0], geracao, numero_avaliacoes, solucoes_avaliacoes, tempos_melhor_solucao, melhor_tempo
