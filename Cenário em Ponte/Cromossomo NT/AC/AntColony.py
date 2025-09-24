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
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Geradores.GeradorIndividuos import Individuo

class SolucaoMapa:
    def __init__(self, tipo_componente, quantidade_componente, ferormonio):
        self.tipo_componente = tipo_componente
        self.quantidade_componente = quantidade_componente
        self.ferormonio = ferormonio
        self.probabilidade = 0

class AntColonyOptimization:
    def __init__(self, componentes, individuos, peso_max, custo_max, num_geracoes, num_tipos_componentes, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema):
        self.num_formigas = len(individuos)
        self.num_variaveis = num_variaveis
        self.num_geracoes = num_geracoes
        self.num_tipos_componentes = num_tipos_componentes
        self.componentes = componentes
        self.peso_max = peso_max
        self.custo_max = custo_max
        self.num_max_componentes_subsistema = num_max_componentes_subsistema
        self.num_min_componentes_subsistema = num_min_componentes_subsistema
        self.evaporation_rate = 0.2

        self.individuos = []
        for i in range(self.num_formigas):
            self.individuos.append(individuos[i])
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

def main(componentes, individuos, peso_max, custo_max, num_geracoes, num_tipos_componentes, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema):
    aco = AntColonyOptimization(componentes, individuos, peso_max, custo_max, num_geracoes, num_tipos_componentes, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema)

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
                geracao = i + 1
        solucoes_log.append(melhor_solucao_log)
        solucoes.append(melhor_individuo.valor_funcao_objetivo)
        solucoes_avaliacoes.extend([melhor_individuo.valor_funcao_objetivo] * len(novas_solucoes))

    aco.individuos = sorted(aco.individuos, key=lambda x: x.valor_funcao_objetivo, reverse=True)
    melhor_individuo = aco.individuos[0]

    print("O algoritmo ACO obteve em", aco.num_geracoes, "geracoes o resultado para a funcao objetivo de", aco.individuos[0].valor_funcao_objetivo)
    print("Com os seguintes valores para cada variavel de decisao:")
    for z in range(aco.num_variaveis):
        print(f"T{z+1}: {aco.individuos[0].solucao[0][z]}")
        print(f"Q{z+1}: {aco.individuos[0].solucao[1][z]}")
    print("\n")

    plt.plot(range(0, aco.num_geracoes+1), solucoes, color='blue')
    plt.xlabel('Geração')
    plt.ylabel('Valor da Função Objetivo')
    plt.title('Evolução da Melhor Solução ao Longo das Gerações (ACO)')
    plt.grid(True)
    valor_final = aco.truncate(aco.individuos[0].confiabilidade_total, 4)
    texto = f"Valor final: {valor_final}\nAlcançado na geração: {geracao}"
    plt.figtext(0.87, 0.029, texto, wrap=True, horizontalalignment='center', fontsize=8)
    plt.tight_layout()
    plt.savefig('./AC/img/SolutionEvolutionACO.png')
    plt.show()

    plt.plot(range(0, aco.num_geracoes+1), solucoes_log, color='blue')
    plt.xlabel('Geração')
    plt.ylabel('log(confiabilidade)')
    plt.title('Evolução da Melhor Solução ao Longo das Gerações (ACO)')
    plt.grid(True)
    valor_final_log = aco.truncate(melhor_solucao_log, 4)
    texto = f"Valor final: {valor_final_log}\nAlcançado na geração: {geracao}"
    plt.figtext(0.87, 0.029, texto, wrap=True, horizontalalignment='center', fontsize=8)
    plt.tight_layout()
    plt.savefig('./AC/img/SolutionEvolutionACOLog.png')
    plt.show()

    # Plotando o gráfico com o número de avaliações
    plt.plot(range(0, numero_avaliacoes+1), solucoes_avaliacoes, color='blue')  # Linha azul plotada depois
    # Configurações do gráfico
    plt.xlabel('Número de Avaliações')
    plt.ylabel('Valor da Função Objetivo')
    plt.title('Evolução da Melhor Solução ao Longo das Avaliações (ACO)')
    plt.grid(True)
    # Texto adicional no gráfico
    valor_final = aco.truncate(aco.individuos[0].confiabilidade_total, 4)
    texto = "Valor final: " + str(valor_final) + "\nAlcançado na geração: " + str(geracao) + "\nNúmero de avaliações: " + str(numero_avaliacoes)
    plt.figtext(0.8, 0.05, texto, wrap=True, horizontalalignment='center', fontsize=8)
    # Ajustes finais e salvamento
    plt.subplots_adjust(bottom=0.2)
    plt.savefig('./AC/img/SolutionEvolutionACAvaliacoes.png')
    plt.show()

    return solucoes_log, valor_final_log, aco.individuos[0], geracao, numero_avaliacoes, solucoes_avaliacoes

if __name__ == "__main__":
    with open('output.txt', 'w') as f:
        with redirect_stdout(f):
            main()
