import time
import numpy as np
import sys
import os
import math
from contextlib import redirect_stdout
from copy import deepcopy
import matplotlib.pyplot as plt
from decimal import Decimal, getcontext
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Geradores.GeradorIndividuos import IndividuoPSO
from Geradores.GeradorGraficos import GeradorGraficos

class ParticleSwarmOptimization:
    def __init__(self, componentes, individuos, peso_max, custo_max, num_geracoes, num_tipos_componentes, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema):
        self.num_particulas = len(individuos)
        self.num_variaveis = 5 #5 subsistemas
        self.num_geracoes = num_geracoes
        self.exploracao_global = 1.49 #C2
        self.auto_exploracao = 1.49 #C1
        self.taxa_inercia = 1 #w
        self.damp_inercia = 0.99

        self.num_tipos_componentes = num_tipos_componentes
        self.componentes = componentes
        self.peso_max = peso_max
        self.custo_max = custo_max

        self.num_max_componentes_subsistema = num_max_componentes_subsistema
        self.num_min_componentes_subsistema = num_min_componentes_subsistema

        self.individuos = []
        for i in range(len(individuos)):
            self.individuos.append(IndividuoPSO(deepcopy(individuos[i].solucao), componentes, None, peso_max, custo_max, num_variaveis))
        self.individuos = sorted(self.individuos, key=lambda x: x.valor_funcao_objetivo, reverse=True)
    
    def atualiza_velocidade(self, individuo, globalBest):
        r1 = np.random.rand()
        r2 = np.random.rand()

        inercia = deepcopy(individuo.velocidade)*self.taxa_inercia
        auto_exploracao = self.auto_exploracao*r1*(deepcopy(individuo.melhor_posicao.solucao) - deepcopy(individuo.solucao))
        exploracao_global = self.exploracao_global*r2*(deepcopy(globalBest.solucao) - deepcopy(individuo.solucao))

        velocidade_final = np.array(
            inercia + auto_exploracao + exploracao_global
        )

        #tratativa de espelho para ver quais dimensões irão fugir da solução viável
        #de forma simples, se a posicao atual da partícula já estiver numa borda e a velocidade ainda aponta para fora, invertemos a velocidade

        for i in range(len(velocidade_final[0])):
            #primeira linha, que se refere aos tipos de componentes
            if velocidade_final[0][i] < 0 and deepcopy(individuo.solucao[0][i]) == 0:
                velocidade_final[0][i] *= -1
            if velocidade_final[0][i] > 0 and deepcopy(individuo.solucao[1][i]) == self.num_tipos_componentes - 1:
                velocidade_final[0][i] *= -1

            #segunda linha, que se refere às quantidades de componentes
            if velocidade_final[1][i] < 0 and deepcopy(individuo.solucao[1][i]) == self.num_min_componentes_subsistema:
                velocidade_final[1][i] *= -1
            if velocidade_final[1][i] > 0 and deepcopy(individuo.solucao[1][i]) == self.num_max_componentes_subsistema:
                velocidade_final[1][i] *= -1

        return velocidade_final

    def atualiza_posicao(self, individuo):
        posicao_final = (
            deepcopy(individuo.solucao) + deepcopy(individuo.velocidade)
        )

        posicao_final_inteira = np.round(posicao_final,0)
        posicao_final_inteira[posicao_final_inteira == -0.0] = 0

        #olhando para todos os valores da segunda linha da posicao final, caso fique maior que 3, volta pra 3, caso menor que 1, volta para 1
        posicao_final_inteira[1][posicao_final_inteira[1] > self.num_max_componentes_subsistema] = self.num_max_componentes_subsistema
        posicao_final_inteira[1][posicao_final_inteira[1] < self.num_min_componentes_subsistema] = self.num_min_componentes_subsistema

        #tratativa casa fique negativo tambem
        posicao_final_inteira[0][posicao_final_inteira[0] < 0] = 0
        posicao_final_inteira[0][posicao_final_inteira[0] >= self.num_tipos_componentes] = self.num_tipos_componentes - 1

        return posicao_final_inteira
    
    def truncate(self, number, decimals=0):
        factor = 10 ** decimals
        return math.trunc(number * factor) / factor

def main(index, componentes, individuos, peso_max, custo_max, num_geracoes, num_tipos_componentes, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema):
    alg = ParticleSwarmOptimization(componentes, individuos, peso_max, custo_max, num_geracoes, num_tipos_componentes, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema)

    print("POPULAÇÃO INICIAL:")
    for l in range(len(alg.individuos)):
        print("Individuo {}:".format(l+1))
        print(alg.individuos[l])
        print(" ")
    print(" ")

    numero_avaliacoes = 0
    solucoes_avaliacoes = []
    solucoes = []
    solucoes_log = []
    geracao = -1

    global_best = None
    melhor_solucao = -10000
    melhor_solucao_log = -10000

    melhor_tempo = 0
    start_time = time.time()
    tempos_melhor_solucao = []

    for i in range(alg.num_geracoes):
        print("GERACAO {}".format(i+1))
        for j in range(alg.num_particulas):
            fit_pos_atual = alg.individuos[j].valor_funcao_objetivo
            fit_best_pos = alg.individuos[j].melhor_posicao.valor_funcao_objetivo

            if i == 0 and j==0:
                fit_global = -10000
            else:
                fit_global = global_best.valor_funcao_objetivo
                
            if fit_pos_atual > fit_best_pos:
                alg.individuos[j].melhor_posicao = deepcopy(alg.individuos[j])
                fit_best_pos = alg.individuos[j].melhor_posicao.valor_funcao_objetivo
            
            if fit_best_pos > fit_global:
                global_best = deepcopy(alg.individuos[j].melhor_posicao)
                fit_global = fit_best_pos

        if i == 0: 
            solucoes.append(fit_global)
            solucoes_log.append(math.log(fit_global))
            solucoes_avaliacoes.append(fit_global)
            melhor_tempo = time.time() - start_time
            tempos_melhor_solucao.append(time.time() - start_time)
        
        print("Populacao antes da execucao:")
        for l in range(len(alg.individuos)):
            print("Individuo {}:".format(l+1))
            print(alg.individuos[l])
            print(" ")
        print("-----------------------------------------")

        for k in range(alg.num_particulas):
            alg.individuos[k].velocidade = alg.atualiza_velocidade(alg.individuos[k], global_best)
            alg.individuos[k].solucao = alg.atualiza_posicao(alg.individuos[k])

        print("Populacao final da era:")
        for l in range(len(alg.individuos)):
            print("Individuo {}:".format(l+1))
            print(alg.individuos[l])
            print(" ")
        print("-----------------------------------------")
        print("-----------------------------------------")
        print("-----------------------------------------")
        print("-----------------------------------------")

        fit_global = global_best.valor_funcao_objetivo
        solucoes.append(fit_global)
        solucoes_log.append(math.log(fit_global))
        tempos_melhor_solucao.append(time.time() - start_time)
        solucoes_avaliacoes.extend([fit_global] * alg.num_particulas)
        numero_avaliacoes += alg.num_particulas

        if melhor_solucao < fit_global:
            melhor_solucao_log = math.log(fit_global)
            melhor_solucao = fit_global
            melhor_tempo = time.time() - start_time
            geracao = i + 1

        #atualizacao da inercia
        alg.taxa_inercia = alg.taxa_inercia * alg.damp_inercia
            
    print("O algoritmo PSO obteve em", alg.num_geracoes, "geracoes o resultado para a funcao objetivo de", melhor_solucao)
    print("Com os seguintes valores para cada variavel de decisao:")
    for z in range(alg.num_variaveis):
        print("T{}: {}".format(z+1, alg.individuos[0].solucao[0][z]))
        print("Q{}: {}".format(z+1, alg.individuos[0].solucao[1][z]))
    print("\n")

    gerador_graficos = GeradorGraficos('./Metodos/PSO/img/', 'purple')
    valor_final = alg.truncate(melhor_solucao, 4)
    valor_final_log = alg.truncate(melhor_solucao_log, 4)

    # Plotando o gráfico por geração
    gerador_graficos.gera_grafico(f'SolutionEvolutionPSO{index}.png', range(0, alg.num_geracoes+1), solucoes, valor_final, geracao, 'Evolução da Melhor Solução ao Longo das Gerações (PSO)', 'Geração', 'Função Objetivo', show_plot=False)

    # Plotando o gráfico em log por geração
    gerador_graficos.gera_grafico(f'SolutionEvolutionPSOLog{index}.png', range(0, alg.num_geracoes+1), solucoes_log, valor_final_log, geracao, 'Evolução da Melhor Solução ao Longo das Gerações (PSO)', 'Geração', 'log(Função Objetivo)', show_plot=False)

    # Plotando o gráfico com o número de avaliações
    gerador_graficos.gera_grafico(f'SolutionEvolutionPSOAvaliacoes{index}.png', range(0, numero_avaliacoes+1), solucoes_avaliacoes, valor_final, geracao, 'Evolução da Melhor Solução ao Longo das Avaliações (PSO)', 'Número de Avaliações', 'Função Objetivo', 'Número de Avaliações: ' + str(numero_avaliacoes))

    #Plotando o gráfico com o tempo por funcao objetivo
    gerador_graficos.gera_grafico(f'SolutionEvolutionPSOTempo{index}.png', tempos_melhor_solucao, solucoes, valor_final, geracao, 'Evolução do Tempo de Execução ao Longo das Gerações (PSO)', 'Tempo (s)', 'Função Objetivo', 'Alcançado no tempo: ' + str(alg.truncate(melhor_tempo, 4)) + 's')

    return solucoes_log, valor_final_log, global_best, geracao, numero_avaliacoes, solucoes_avaliacoes, tempos_melhor_solucao, melhor_tempo

    