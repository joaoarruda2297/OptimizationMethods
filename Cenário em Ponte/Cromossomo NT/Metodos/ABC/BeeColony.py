import numpy as np
import math
import sys
import random
import os
import time
from decimal import Decimal, getcontext
from contextlib import redirect_stdout
from copy import deepcopy
import matplotlib.pyplot as plt
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Geradores.GeradorIndividuos import IndividuoABC
from Geradores.GeradorGraficos import GeradorGraficos
from utils import truncate
    
class BeeColonyAlgorithm:
    def __init__(self, componentes, individuos, peso_max, custo_max, num_geracoes, num_max_avaliacoes, num_tipos_componentes, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema):
        #variáveis para execução do algoritmo de colônia de abelhas
        self.num_individuos = len(individuos) #quantidade de individuos
        self.num_variaveis = num_variaveis
        self.num_geracoes = num_geracoes
        self.num_max_avaliacoes = num_max_avaliacoes
        self.num_tipos_componentes = num_tipos_componentes

        self.componentes = componentes
        self.peso_max = peso_max
        self.custo_max = custo_max

        self.num_max_componentes_subsistema = num_max_componentes_subsistema
        self.num_min_componentes_subsistema = num_min_componentes_subsistema

        # variaveis para controle do algoritmo
        self.estagnacao_max = 10

        self.individuos = []
        for i in range(len(individuos)):
            self.individuos.append(IndividuoABC(deepcopy(individuos[i].solucao), componentes, peso_max, custo_max))
        self.individuos = sorted(self.individuos, key=lambda x: x.valor_funcao_objetivo, reverse=True)

    def atualiza_solucao(self, populacao, i):
        #index aleatorio da populacao
        index_aleatorio = i
        while(index_aleatorio == i):
            index_aleatorio = random.randint(0, len(populacao)-1)

        #copiando apenas a solucao do individuo
        nova_solucao = deepcopy(populacao[i].solucao)
        solucao_diferente = deepcopy(populacao[index_aleatorio].solucao)

        #gerando index aleatório para alteração
        linha = random.randint(0, 1)
        coluna = random.randint(0, 4)

        valor_nova_solucao = nova_solucao[linha][coluna]
        valor_solucao_diferente = solucao_diferente[linha][coluna]

        phi = random.uniform(-1,1)
        valor_final_nova_solucao = valor_nova_solucao + phi*(valor_nova_solucao - valor_solucao_diferente)

        valor_final_nova_solucao_inteira = int(round(valor_final_nova_solucao))
        #corrigindo possíveis erros de extrapolação de limites
        if(linha == 0):
            if(valor_final_nova_solucao_inteira < 0):
                valor_final_nova_solucao_inteira = 0
            elif(valor_final_nova_solucao_inteira > self.num_tipos_componentes - 1):
                valor_final_nova_solucao_inteira = self.num_tipos_componentes - 1
        elif(linha == 1):
            if(valor_final_nova_solucao_inteira < self.num_min_componentes_subsistema):
                valor_final_nova_solucao_inteira = self.num_min_componentes_subsistema
            elif(valor_final_nova_solucao_inteira > self.num_max_componentes_subsistema):
                valor_final_nova_solucao_inteira = self.num_max_componentes_subsistema
                
        nova_solucao[linha][coluna] = valor_final_nova_solucao_inteira
        
        novo_individuo = IndividuoABC(nova_solucao, self.componentes, self.peso_max,
                            self.custo_max)

        #se a função objetivo do novo indivíduo for melhor, substitui o antigo
        if(novo_individuo.valor_funcao_objetivo > populacao[i].valor_funcao_objetivo):
            populacao[i] = novo_individuo
        else:
            populacao[i].estagnacao += 1

    def abelhas_empregadas(self, populacao):
        #Cada abelha empregada tenta melhorar sua própria solução alterando uma variável de decisão
        for i in range(len(populacao)):
            self.atualiza_solucao(populacao, i)
    
    def abelhas_exploradoras(self, populacao):
        #primeiro saber a soma de probabilidades
        total_aptidao = sum(abelha.valor_funcao_objetivo for abelha in populacao)
        probabilidade_minima = random.uniform(0, 1)*0.1 #multiplico por 0.1 para garantir que seja um valor pequeno
        cont_avaliacao = 0
        for i in range(len(populacao)):
            probabilidade = populacao[i].valor_funcao_objetivo / total_aptidao
            if(probabilidade > probabilidade_minima):
                self.atualiza_solucao(populacao, i)
                cont_avaliacao += 1
        return cont_avaliacao

    def abelhas_observadoras(self, populacao):
        cont_avaliacao = 0
        for i in range(len(populacao)):
            if(populacao[i].estagnacao >= self.estagnacao_max):
                populacao[i] = self.gera_nova_abelha()
                cont_avaliacao += 1
        return cont_avaliacao
                
    
    def gera_nova_abelha(self):
        while True:
            linha_tipos = np.random.randint(0, self.num_tipos_componentes, self.num_variaveis)
            linha_quantidades = np.random.randint(self.num_min_componentes_subsistema,self.num_max_componentes_subsistema + 1,self.num_variaveis)
            solucao = np.vstack((linha_tipos, linha_quantidades))

            # Cria o indivíduo
            individuo = IndividuoABC(solucao, self.componentes, self.peso_max,
                                self.custo_max)

            # Retorna apenas indivíduos viáveis
            if individuo.valor_funcao_objetivo >= 0:
                return individuo

    def verifica_duplicados(self, populacao):
        # Verifica se existem indivíduos duplicados na população com base na solução
        solucoes_unicas = set()
        populacao_filtrada = []
        
        for individuo in populacao:
            # Convertemos a solução (duas linhas) para tupla de tuplas, que é hashable
            chave_solucao = (tuple(individuo.solucao[0]), tuple(individuo.solucao[1]))
            
            if chave_solucao not in solucoes_unicas:
                solucoes_unicas.add(chave_solucao)
                populacao_filtrada.append(individuo)

        return populacao_filtrada

def main(index, componentes, individuos, peso_max, custo_max, num_geracoes, num_max_avaliacoes, num_tipos_componentes, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema):
    alg = BeeColonyAlgorithm(componentes, individuos, peso_max, custo_max, num_geracoes, num_max_avaliacoes, num_tipos_componentes, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema)

    print("POPULACAO INICIAL:")
    for l in range(len(alg.individuos)):
        print("Individuo {}:".format(l+1))
        print(alg.individuos[l])
        print(" ")
    print(" ")

    numero_avaliacoes = 0
    solucoes_avaliacoes = []
    melhores_abelhas = []
    solucoes = []
    solucoes_log = []
    melhor_solucao_log = -10000
    geracao = -1
    melhor_individuo: IndividuoABC = alg.individuos[1] #qualquer só para inicializar
    melhor_tempo = 0
    start_time = time.time()
    tempos_melhor_solucao = []

    for j in range(len(alg.individuos)):
        if(alg.individuos[j].valor_funcao_objetivo > melhor_individuo.valor_funcao_objetivo):
            log_individuo = math.log(alg.individuos[j].valor_funcao_objetivo)
            melhor_solucao_log = log_individuo
            melhor_individuo = alg.individuos[j]
            geracao = 1
            melhor_tempo = time.time() - start_time
    solucoes_log.append(melhor_solucao_log)
    solucoes.append(melhor_individuo.valor_funcao_objetivo)
    melhores_abelhas.append(melhor_individuo)
    solucoes_avaliacoes.append(melhor_individuo.valor_funcao_objetivo)
    tempos_melhor_solucao.append(time.time() - start_time)

    for i in range(alg.num_geracoes):
        if(numero_avaliacoes >= alg.num_max_avaliacoes):
            break
        print("GERACAO {}".format(i+1))
        #Fase das abelhas empregadas
        alg.abelhas_empregadas(alg.individuos)

        #Fase das abelhas exploradoras
        cont_avaliacao_exploradoras = alg.abelhas_exploradoras(alg.individuos)

        #memoriza melhor solucao do momento
        for j in range(len(alg.individuos)):
            if(alg.individuos[j].valor_funcao_objetivo > melhor_individuo.valor_funcao_objetivo):
                log_individuo = math.log(alg.individuos[j].valor_funcao_objetivo)
                melhor_solucao_log = log_individuo
                melhor_individuo = alg.individuos[j]
                melhor_tempo = time.time() - start_time
                geracao = i + 1
        solucoes_log.append(melhor_solucao_log)
        solucoes.append(melhor_individuo.valor_funcao_objetivo)
        melhores_abelhas.append(melhor_individuo)
        tempos_melhor_solucao.append(time.time() - start_time)

        #Fase das abelhas observadoras
        cont_avaliacao_observadoras = alg.abelhas_observadoras(alg.individuos)

        numero_avaliacoes += cont_avaliacao_exploradoras + cont_avaliacao_observadoras + len(alg.individuos) 
        solucoes_avaliacoes.extend([melhor_individuo.valor_funcao_objetivo] * (cont_avaliacao_exploradoras + cont_avaliacao_observadoras + len(alg.individuos)))

        print("Populacao final da era:")
        for l in range(len(alg.individuos)):
            print("Abelha {}:".format(l+1))
            print(alg.individuos[l])
            print(" ")
        print("-----------------------------------------")
        print("-----------------------------------------")
        print("-----------------------------------------")
        print("-----------------------------------------")
        print("-----------------------------------------")

    melhor_individuo = melhores_abelhas[-1]
    print("O algoritmo de colônia de abelhas obteve em", i, "geracoes o resultado para a funcao objetivo de", alg.individuos[0].valor_funcao_objetivo)
    print("Com os seguintes valores para cada variavel de decisão:")
    for z in range(alg.num_variaveis):
        print("T{}: {}".format(z+1, melhor_individuo.solucao[0][z]))
        print("Q{}: {}".format(z+1, melhor_individuo.solucao[1][z]))
    print("\n")

    gerador_graficos = GeradorGraficos('./Metodos/ABC/img/', 'red')
    valor_final = truncate(alg.individuos[0].confiabilidade_total, 4)
    valor_final_log = truncate(melhor_solucao_log, 4)

    # Plotando o gráfico por geração
    #gerador_graficos.gera_grafico(f'SolutionEvolutionABC{index}.png', range(0, alg.num_geracoes+1), solucoes, valor_final, geracao, 'Evolução da Melhor Solução ao Longo das Gerações (ABC)', 'Geração', 'Função Objetivo', show_plot=False)

    # Plotando o gráfico em log por geração
    #gerador_graficos.gera_grafico(f'SolutionEvolutionABCLog{index}.png', range(0, alg.num_geracoes+1), solucoes_log, valor_final_log, geracao, 'Evolução da Melhor Solução ao Longo das Gerações (ABC)', 'Geração', 'log(Função Objetivo)', show_plot=False)

    # Plotando o gráfico com o número de avaliações
    gerador_graficos.gera_grafico(f'SolutionEvolutionABCAvaliacoes{index}.png', range(0, numero_avaliacoes+1), solucoes_avaliacoes, valor_final, geracao, 'Evolução da Melhor Solução ao Longo das Avaliações (ABC)', 'Número de Avaliações', 'Função Objetivo', 'Número de avaliações: ' + str(numero_avaliacoes))

    # Plotando o gráfico com o tempo para alcançar a melhor solução
    gerador_graficos.gera_grafico(f'SolutionEvolutionABCTempo{index}.png', tempos_melhor_solucao, solucoes, valor_final, geracao, 'Evolução do Tempo para Alcançar a Melhor Solução (ABC)', 'Tempo (s)', 'Função Objetivo', 'Tempo alcançado: ' + str(truncate(melhor_tempo,4)) + 's')

    return solucoes_log, valor_final_log, melhor_individuo, geracao, numero_avaliacoes, solucoes_avaliacoes, tempos_melhor_solucao, melhor_tempo

    