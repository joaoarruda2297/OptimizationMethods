import numpy as np
import math
import sys
import random
import os
from decimal import Decimal, getcontext
from contextlib import redirect_stdout
from copy import deepcopy
import matplotlib.pyplot as plt
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from GeradorIndividuos import Individuo as IndividuoGA
    
class GeneticAlgorithm:
    def __init__(self, componentes, individuos, peso_max, custo_max, num_geracoes, coeficiente_custo, coeficiente_peso):
        #variáveis para execução do algoritmo genético
        self.num_individuos = len(individuos) #quantidade de individuos
        self.num_variaveis = 5 #5 subsistemas
        self.num_geracoes = num_geracoes
        self.taxa_cruzamento = 0.6 #quantidade de pais que gerarão individuos (pais/2)
        self.taxa_mutacao = 0.3 #quantidade de individuos que vão receber mutação

        self.num_tipos_componentes = componentes.shape[1]

        self.componentes = componentes
        self.peso_max = peso_max
        self.custo_max = custo_max

        self.num_max_componentes_subsistema = 10
        self.num_min_componentes_subsistema = 3

        self.coeficiente_custo = coeficiente_custo
        self.coeficiente_peso = coeficiente_peso

        self.individuos = []
        for i in range(self.num_individuos):
            self.individuos.append(individuos[i])
        self.individuos = sorted(self.individuos, key=lambda x: x.valor_funcao_objetivo, reverse=True)

    def seleciona_pais(self, populacao):
        #selecionando os pais de forma simples, apenas pelos mais fortes
        num_pais = int(self.taxa_cruzamento*self.num_individuos)

        if(num_pais % 2 != 0):
            num_pais-=1

        pais = []
        for i in range(num_pais):
            pais.append(populacao[i])

        return pais
    
    def crossover_linha(self, individuo1, individuo2):
        tamanho_cromossomo = random.randint(1, self.num_variaveis) #numero de genes que serão trocados entre os pais
        posicoes = [] #posicoes variadas do genes, nao necessariamente sequenciais
        filho1 = [] 
        filho2 = []
        linha1 = random.randint(0, 1)  # Escolhe aleatoriamente a linha do cromossomo
        linha2 = 1 if linha1 == 0 else 0   

        for _ in range(tamanho_cromossomo):
            while True:
                posicao = random.randint(0, self.num_variaveis - 1)
                if posicao not in posicoes:
                    posicoes.append(posicao)
                    break
        posicoes.sort()

        for i in range(self.num_variaveis):
            if i in posicoes:
                filho1.append(individuo2.solucao[linha1][i])
                filho2.append(individuo1.solucao[linha1][i])
            else:
                filho1.append(individuo1.solucao[linha1][i])
                filho2.append(individuo2.solucao[linha1][i])

        if(linha1 == 0):
            filho1 = [np.array(filho1), individuo1.solucao[linha2].copy()]
            filho2 = [np.array(filho2), individuo2.solucao[linha2].copy()]
        else:
            filho1 = [individuo1.solucao[linha2].copy(), np.array(filho1)]
            filho2 = [individuo2.solucao[linha2].copy(), np.array(filho2)]
        
        filho1 = IndividuoGA(filho1, self.componentes, self.peso_max, self.custo_max, self.coeficiente_peso, self.coeficiente_custo)
        filho2 = IndividuoGA(filho2, self.componentes, self.peso_max, self.custo_max, self.coeficiente_peso, self.coeficiente_custo)

        return filho1, filho2

    def crossover_coluna(self, individuo1, individuo2):
        n_colunas = random.randint(1, self.num_variaveis) #numero de colunas que serão trocados entre os pais
        posicoes = [] #posicoes variadas do genes, nao necessariamente sequenciais
        filho1 = [[],[]]
        filho2 = [[],[]]

        for _ in range(n_colunas):
            while True:
                posicao = random.randint(0, self.num_variaveis - 1)
                if posicao not in posicoes:
                    posicoes.append(posicao)
                    break
        posicoes.sort()
        print("Numero de colunas: ", n_colunas)
        print("Posicoes: ", posicoes)
        for i in range(self.num_variaveis):
            if i in posicoes:
                filho1[0].append(individuo2.solucao[0][i])
                filho1[1].append(individuo2.solucao[1][i])
                filho2[0].append(individuo1.solucao[0][i])
                filho2[1].append(individuo1.solucao[1][i])
            else:
                filho1[0].append(individuo1.solucao[0][i])
                filho2[0].append(individuo2.solucao[0][i])
                filho1[1].append(individuo1.solucao[1][i])
                filho2[1].append(individuo2.solucao[1][i])

        filho1 = [np.array(filho1[0]), np.array(filho1[1])]
        filho2 = [np.array(filho2[0]), np.array(filho2[1])]

        filho1 = IndividuoGA(filho1, self.componentes, self.peso_max, self.custo_max, self.coeficiente_peso, self.coeficiente_custo)
        filho2 = IndividuoGA(filho2, self.componentes, self.peso_max, self.custo_max, self.coeficiente_peso, self.coeficiente_custo)

        return filho1, filho2
    
    def crossover(self, pais):
        filhos = []
        filho1 = IndividuoGA()
        filho2 = IndividuoGA()

        for i in range(0, len(pais) - 1, 2):
            filhos_criados = 0
            while(filhos_criados < 3):
                valor = np.random.choice([True, False])

                if(valor):
                    filho1, filho2 = self.crossover_linha(pais[i], pais[i+1])
                else:
                    filho1, filho2 = self.crossover_coluna(pais[i], pais[i+1])

                if(filho1.valor_funcao_objetivo > 0):
                    filhos.append(filho1)
                    filhos_criados += 1
                if(filho2.valor_funcao_objetivo > 0):
                    filhos.append(filho2)
                    filhos_criados += 1

        return filhos

    def seleciona_mutantes(self, populacao):
        #selecionando os mutantes de forma simples, apenas pelos mais fracos
        num_mutantes = int(self.taxa_mutacao*self.num_individuos)
        ind_para_mutacao = [deepcopy(populacao[i]) for i in range(self.num_individuos-1, self.num_individuos - num_mutantes -1, -1)]
        
        return ind_para_mutacao
    
    def mutacao(self, ind_para_mutacao):
        mutantes = []

        def gerar_mutante_valido(cromossomo_original):
            while True:
                # Faz uma cópia profunda para não modificar o original
                novo_cromossomo = [linha.copy() for linha in cromossomo_original]

                linha = random.randint(0, 1)  # 0 ou 1 (dois níveis: tipo e quantidade)
                coluna = random.randint(0, self.num_variaveis - 1)

                valor_atual = novo_cromossomo[linha][coluna]
                limite_inferior = 0 if linha == 0 else 1
                limite_superior = self.num_tipos_componentes-1 if linha == 0 else self.num_max_componentes_subsistema

                # Gera novo valor diferente
                while True:
                    valor_mutacao = random.randint(limite_inferior, limite_superior)
                    if valor_mutacao != valor_atual:
                        break

                novo_cromossomo[linha][coluna] = valor_mutacao

                novo_individuo = IndividuoGA(
                    novo_cromossomo,self.componentes,self.peso_max,self.custo_max,self.coeficiente_peso,self.coeficiente_custo
                )

                if novo_individuo.valor_funcao_objetivo > 0:
                    return novo_individuo

        for i in range(len(ind_para_mutacao)):
            cromossomo_original = ind_para_mutacao[i].solucao
            mutante_valido = gerar_mutante_valido(cromossomo_original)
            mutantes.append(mutante_valido)

        return mutantes

    def truncate(self, number, decimals=0):
        factor = 10 ** decimals
        return math.trunc(number * factor) / factor

def main(componentes, individuos, peso_max, custo_max, num_geracoes, coeficiente_custo, coeficiente_peso):
    alg = GeneticAlgorithm(componentes, individuos, peso_max, custo_max, num_geracoes, coeficiente_custo, coeficiente_peso)

    print("POPULAÇÃO INICIAL:")
    for l in range(len(alg.individuos)):
        print("Individuo {}:".format(l+1))
        print(alg.individuos[l])
        print(" ")
    print(" ")

    solucoes = []
    solucoes_log = []
    melhor_solucao_log = -10000
    melhor_solucao = -10000
    geracao = -1
    geracao_log = -1

    for i in range(alg.num_geracoes):
        print("GERACAO {}".format(i+1))

        if i == 0:
            for j in range(len(alg.individuos)):
                print("AQUI:", alg.individuos[j].confiabilidade_total)
                log_individuo = math.log(alg.individuos[j].confiabilidade_total)

                if log_individuo > melhor_solucao_log:
                    melhor_solucao_log = log_individuo
                    print("MELHOR:", melhor_solucao_log)
            solucoes_log.append(melhor_solucao_log)
            geracao_log = 0

        if alg.individuos[0].valor_funcao_objetivo > melhor_solucao and i == 0:
            melhor_solucao = alg.individuos[0].valor_funcao_objetivo
            geracao = i
            solucoes.append(alg.individuos[0].valor_funcao_objetivo)

        pais = alg.seleciona_pais(alg.individuos)
        filhos = alg.crossover(pais)

        for l in range(len(filhos)):
            print("Filho {}:".format(l+1))
            print(filhos[l])
            print(" ")
        print("-----------------------------------------")
        
        ind_para_mutacao = alg.seleciona_mutantes(alg.individuos)
        for l in range(len(ind_para_mutacao)):
            print("Pré-Mutante {}:".format(l+1))
            print(ind_para_mutacao[l])
            print(" ")
        print("-----------------------------------------")
        mutantes = alg.mutacao(ind_para_mutacao)

        for l in range(len(mutantes)):
            print("Mutante {}:".format(l+1))
            print(mutantes[l])
            print(" ")
        print("-----------------------------------------")

        print("Populacao antes da mescla:")
        for l in range(len(alg.individuos)):
            print("Individuo {}:".format(l+1))
            print(alg.individuos[l])
            print(" ")
        print("-----------------------------------------")

        populacao = alg.individuos + mutantes + filhos
        populacao = sorted(populacao, key=lambda x: x.valor_funcao_objetivo, reverse=True)

        populacao = populacao[:alg.num_individuos]

        alg.individuos = populacao
        print("Populacao final da era:")
        for l in range(len(alg.individuos)):
            print("Individuo {}:".format(l+1))
            print(alg.individuos[l])
            print(" ")
        print("-----------------------------------------")
        print("-----------------------------------------")
        print("-----------------------------------------")
        print("-----------------------------------------")
        print("-----------------------------------------")

        solucoes.append(alg.individuos[0].valor_funcao_objetivo)

        if alg.individuos[0].valor_funcao_objetivo > melhor_solucao:
            melhor_solucao = alg.individuos[0].valor_funcao_objetivo
            geracao = i
        
        for j in range(len(alg.individuos)):
            log_individuo = math.log(alg.individuos[0].confiabilidade_total)

            if log_individuo > melhor_solucao_log:
                melhor_solucao_log = log_individuo
                geracao_log = i
        solucoes_log.append(melhor_solucao_log)
        
    print("O algoritmo genetico obteve em", alg.num_geracoes, "geracoes o resultado para a funcao objetivo de", alg.individuos[0].valor_funcao_objetivo)
    print("Com os seguintes valores para cada variavel de decisao:")
    for z in range(alg.num_variaveis):
        print("T{}: {}".format(z+1, populacao[0].solucao[0][z]))
        print("Q{}: {}".format(z+1, populacao[0].solucao[1][z]))
    print("\n")

    # Plotando o gráfico
    #plt.axhline(y=0, color='red', linestyle='-', linewidth=0.4)  # Linha vermelha mais fina e plotada primeiro
    plt.plot(range(0, alg.num_geracoes+1), solucoes, color='orange')  # Linha laranja plotada depois
    # Configurações do gráfico
    plt.xlabel('Geração')
    plt.ylabel('Valor da Função Objetivo')
    plt.title('Evolução da Melhor Solução ao Longo das Gerações (GA)')
    plt.grid(True)
    # Texto adicional no gráfico
    valor_final = alg.truncate(alg.individuos[0].confiabilidade_total, 4)
    texto = "Valor final: " + str(valor_final) + "\nAlcançado na geração: " + str(geracao)
    plt.figtext(0.87, 0.029, texto, wrap=True, horizontalalignment='center', fontsize=8)
    # Ajustes finais e salvamento
    plt.tight_layout()
    plt.savefig('./GA/img/SolutionEvolutionGA.png')
    plt.show()

    # Plotando o gráfico em log
    plt.plot(range(0, alg.num_geracoes+1), solucoes_log, color='orange')  # Linha laranja plotada depois
    # Configurações do gráfico
    plt.xlabel('Geração')
    plt.ylabel('log(confiabilidade)')
    plt.title('Evolução da Melhor Solução ao Longo das Gerações (GA)')
    plt.grid(True)
    # Texto adicional no gráfico
    valor_final_log = alg.truncate(melhor_solucao_log, 4)
    texto = "Valor final: " + str(valor_final_log) + "\nAlcançado na geração: " + str(geracao_log)
    plt.figtext(0.87, 0.029, texto, wrap=True, horizontalalignment='center', fontsize=8)
    # Ajustes finais e salvamento
    plt.tight_layout()
    plt.savefig('./GA/img/SolutionEvolutionGALog.png')
    plt.show()

    return solucoes_log, valor_final_log


if __name__ == "__main__":
    with open('output.txt', 'w') as f:
        with redirect_stdout(f):
            main()

    