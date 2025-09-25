import numpy as np
import math
import time
import sys
import random
import os
from decimal import Decimal, getcontext
from contextlib import redirect_stdout
from copy import deepcopy
import matplotlib.pyplot as plt
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Geradores.GeradorIndividuos import Individuo as IndividuoGA
    
class GeneticAlgorithm:
    def __init__(self, componentes, individuos, peso_max, custo_max, num_geracoes, num_tipos_componentes, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema):
        #variáveis para execução do algoritmo genético
        self.num_individuos = len(individuos) #quantidade de individuos
        self.num_variaveis = num_variaveis
        self.num_geracoes = num_geracoes
        self.taxa_cruzamento = 0.6 #quantidade de pais que gerarão individuos (pais/2)
        self.taxa_mutacao = 0.3 #quantidade de individuos que vão receber mutação

        self.num_tipos_componentes = num_tipos_componentes

        self.componentes = componentes
        self.peso_max = peso_max
        self.custo_max = custo_max

        self.num_max_componentes_subsistema = num_max_componentes_subsistema
        self.num_min_componentes_subsistema = num_min_componentes_subsistema

        self.individuos = []
        for i in range(self.num_individuos):
            self.individuos.append(individuos[i])
        self.individuos = sorted(self.individuos, key=lambda x: x.valor_funcao_objetivo, reverse=True)

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

        filho1 = IndividuoGA(filho1, self.componentes, self.peso_max, self.custo_max)
        filho2 = IndividuoGA(filho2, self.componentes, self.peso_max, self.custo_max)

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

        filho1 = IndividuoGA(filho1, self.componentes, self.peso_max, self.custo_max)
        filho2 = IndividuoGA(filho2, self.componentes, self.peso_max, self.custo_max)

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
                    novo_cromossomo,self.componentes,self.peso_max,self.custo_max
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

def main(componentes, individuos, peso_max, custo_max, num_geracoes, num_tipos_componentes, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema):
    alg = GeneticAlgorithm(componentes, individuos, peso_max, custo_max, num_geracoes, num_tipos_componentes, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema)

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
    melhor_solucao_log = -10000
    geracao = -1
    melhor_individuo: IndividuoGA = alg.individuos[1] #qualquer só para inicializar
    melhor_tempo = 0

    start_time = time.time()
    tempos_melhor_solucao = []
    for j in range(len(alg.individuos)):
        if(alg.individuos[j].valor_funcao_objetivo > melhor_individuo.valor_funcao_objetivo):
            log_individuo = math.log(alg.individuos[j].valor_funcao_objetivo)
            melhor_solucao_log = log_individuo
            melhor_individuo = alg.individuos[j]
            melhor_tempo = time.time() - start_time
            geracao = 1
    solucoes_log.append(melhor_solucao_log)
    solucoes.append(melhor_individuo.valor_funcao_objetivo)
    solucoes_avaliacoes.append(melhor_individuo.valor_funcao_objetivo)
    tempos_melhor_solucao.append(time.time() - start_time)

    for i in range(alg.num_geracoes):
        print("GERACAO {}".format(i+1))

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
        numero_avaliacoes += len(mutantes) + len(filhos)
        print("Número de avaliações até o momento:", numero_avaliacoes)
        
        # Limitando a população ao número máximo de indivíduos
        populacao = alg.verifica_duplicados(populacao)
        alg.individuos = populacao[:alg.num_individuos]

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

        for j in range(len(alg.individuos)):
            if(alg.individuos[j].valor_funcao_objetivo > melhor_individuo.valor_funcao_objetivo):
                log_individuo = math.log(alg.individuos[j].valor_funcao_objetivo)
                melhor_solucao_log = log_individuo
                melhor_individuo = alg.individuos[j]
                melhor_tempo = time.time() - start_time
                geracao = i + 1
        solucoes_log.append(melhor_solucao_log)
        solucoes.append(melhor_individuo.valor_funcao_objetivo)
        #devo adicionar a melhor solução atual ao vetor de soluções por avaliações
        solucoes_avaliacoes.extend([melhor_individuo.valor_funcao_objetivo] * (len(mutantes) + len(filhos)))
        tempos_melhor_solucao.append(time.time() - start_time)

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
    plt.ylabel('log(Função Objetivo)')
    plt.title('Evolução da Melhor Solução ao Longo das Gerações (GA)')
    plt.grid(True)
    # Texto adicional no gráfico
    valor_final_log = alg.truncate(melhor_solucao_log, 4)
    texto = "Valor final: " + str(valor_final_log) + "\nAlcançado na geração: " + str(geracao)
    plt.figtext(0.87, 0.029, texto, wrap=True, horizontalalignment='center', fontsize=8)
    # Ajustes finais e salvamento
    plt.tight_layout()
    plt.savefig('./GA/img/SolutionEvolutionGALog.png')
    plt.show()

    # Plotando o gráfico com o número de avaliações
    #plt.figure(figsize=(20, 7))  # largura=20, altura=10 polegadas
    plt.plot(range(0, numero_avaliacoes+1), solucoes_avaliacoes, color='orange')  # Linha laranja plotada depois
    # Configurações do gráfico
    plt.xlabel('Número de Avaliações')
    plt.ylabel('Valor da Função Objetivo')
    plt.title('Evolução da Melhor Solução ao Longo das Avaliações (GA)')
    plt.grid(True)
    # Texto adicional no gráfico
    valor_final = alg.truncate(alg.individuos[0].confiabilidade_total, 4)
    texto = "Valor final: " + str(valor_final) + "\nAlcançado na geração: " + str(geracao) + "\nNúmero de avaliações: " + str(numero_avaliacoes)
    plt.figtext(0.8, 0.05, texto, wrap=True, horizontalalignment='center', fontsize=8)
    # Ajustes finais e salvamento
    plt.subplots_adjust(bottom=0.2)
    plt.savefig('./GA/img/SolutionEvolutionGAAvaliacoes.png')
    plt.show()

    #Plotando o gráfico com o tempo por funcao objetivo
    plt.plot(tempos_melhor_solucao, solucoes, color='orange')  # Linha laranja plotada depois
    # Configurações do gráfico
    plt.xlabel('Tempo (s)')
    plt.ylabel('Valor da Função Objetivo')
    plt.title('Evolução do Tempo de Execução ao Longo das Gerações (GA)')
    plt.grid(True)
    # Texto adicional no gráfico
    valor_final = alg.truncate(alg.individuos[0].confiabilidade_total, 4)
    texto = "Valor final: " + str(valor_final) + "\nAlcançado no tempo: " + str(melhor_tempo)
    plt.figtext(0.87, 0.029, texto, wrap=True, horizontalalignment='center', fontsize=8)
    # Ajustes finais e salvamento
    plt.tight_layout()
    plt.savefig('./GA/img/SolutionEvolutionGATempo.png')
    plt.show()

    return solucoes_log, valor_final_log, melhor_individuo, geracao, numero_avaliacoes, solucoes_avaliacoes


if __name__ == "__main__":
    with open('output.txt', 'w') as f:
        with redirect_stdout(f):
            main()

    