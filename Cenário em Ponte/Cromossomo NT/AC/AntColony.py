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
from GeradorIndividuos import Individuo

class AntColonyOptimization:
    def __init__(self, componentes, individuos, peso_max, custo_max, num_geracoes, coeficiente_custo, coeficiente_peso, num_tipos_componentes, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema):
        self.num_formigas = len(individuos)
        self.num_variaveis = num_variaveis
        self.num_geracoes = num_geracoes
        self.num_tipos_componentes = num_tipos_componentes
        self.componentes = componentes
        self.peso_max = peso_max
        self.custo_max = custo_max
        self.num_max_componentes_subsistema = num_max_componentes_subsistema
        self.num_min_componentes_subsistema = num_min_componentes_subsistema
        self.coeficiente_custo = coeficiente_custo
        self.coeficiente_peso = coeficiente_peso
        self.feromonio = np.ones((2, num_variaveis, num_tipos_componentes))
        self.evaporation_rate = 0.2
        self.alpha = 1.0  # influência do feromônio
        self.beta = 2.0   # influência da heurística

        self.individuos = []
        for i in range(self.num_formigas):
            self.individuos.append(individuos[i])
        self.individuos = sorted(self.individuos, key=lambda x: x.valor_funcao_objetivo, reverse=True)

    def heuristica(self, linha, coluna, tipo):
        # Heurística baseada na confiabilidade do componente
        return float(self.componentes[0][tipo])

    def construir_solucao(self):
        solucoes = []
        for _ in range(self.num_formigas):
            solucao = [[], []]
            for linha in range(2):
                for coluna in range(self.num_variaveis):
                    probabilidades = []
                    for tipo in range(self.num_tipos_componentes):
                        fer = self.feromonio[linha][coluna][tipo] ** self.alpha
                        heu = self.heuristica(linha, coluna, tipo) ** self.beta
                        probabilidades.append(fer * heu)
                        print("fer: ", fer)
                        print(self.feromonio[linha][coluna][tipo])
                        print("l: ", linha)
                        print("c: ", coluna)
                        print("t: ", tipo)
                        print("alpha: ", self.alpha)
                        print("beta: ", self.beta)
                        print("heu: ", heu)
                    probabilidades = np.array(probabilidades)
                    probabilidades /= probabilidades.sum()
                    escolhido = np.random.choice(range(self.num_tipos_componentes), p=probabilidades)
                    solucao[linha].append(escolhido)
                print("PROBA: ", probabilidades)
            # Quantidade de componentes (linha 1) deve respeitar limites
            for i in range(self.num_variaveis):
                if solucao[1][i] < self.num_min_componentes_subsistema:
                    solucao[1][i] = self.num_min_componentes_subsistema
                elif solucao[1][i] > self.num_max_componentes_subsistema:
                    solucao[1][i] = self.num_max_componentes_subsistema
            individuo = Individuo([np.array(solucao[0]), np.array(solucao[1])], self.componentes, self.peso_max, self.custo_max, self.coeficiente_peso, self.coeficiente_custo)
            if individuo.valor_funcao_objetivo > 0:
                solucoes.append(individuo)
        return solucoes

    def atualizar_feromonio(self, melhores):
        self.feromonio *= (1 - self.evaporation_rate)
        for ind in melhores:
            for linha in range(2):
                for coluna in range(self.num_variaveis):
                    tipo = int(ind.solucao[linha][coluna])
                    self.feromonio[linha][coluna][tipo] += float(ind.valor_funcao_objetivo)

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

def main(componentes, individuos, peso_max, custo_max, num_geracoes, coeficiente_custo, coeficiente_peso, num_tipos_componentes, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema):
    aco = AntColonyOptimization(componentes, individuos, peso_max, custo_max, num_geracoes, coeficiente_custo, coeficiente_peso, num_tipos_componentes, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema)

    print("POPULAÇÃO INICIAL:")
    for l in range(len(aco.individuos)):
        print(f"Individuo {l+1}:")
        print(aco.individuos[l])
        print(" ")
    print(" ")

    solucoes = []
    solucoes_log = []
    melhor_solucao_log = -10000
    melhor_solucao = -10000
    geracao = -1


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
        
        # Demais gerações: constrói novas soluções
        novas_solucoes = aco.construir_solucao()
        todas = aco.individuos + novas_solucoes
        todas = sorted(todas, key=lambda x: x.valor_funcao_objetivo, reverse=True)
        todas = aco.verifica_duplicados(todas)
        aco.individuos = todas[:aco.num_formigas]
        melhores = aco.individuos[:5]
        aco.atualizar_feromonio(melhores)

        print("Populacao final da era:")
        for l in range(len(aco.individuos)):
            print(f"Individuo {l+1}:")
            print(aco.individuos[l])
            print(" ")
        print("-----------------------------------------")

        # Adiciona apenas o melhor indivíduo da geração
        melhor_individuo = aco.individuos[0]
        melhor_solucao = melhor_individuo.valor_funcao_objetivo
        melhor_solucao_log = math.log(melhor_solucao)
        geracao = i + 1
        solucoes_log.append(melhor_solucao_log)
        solucoes.append(melhor_solucao)

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

    return solucoes_log, valor_final_log

if __name__ == "__main__":
    with open('output.txt', 'w') as f:
        with redirect_stdout(f):
            main()
