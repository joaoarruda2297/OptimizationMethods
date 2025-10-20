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
from Geradores.GeradorIndividuos import Individuo as IndividuoGA
    
class HarmonySearchAlgorithm:
    def __init__(self, componentes, individuos, peso_max, custo_max, num_geracoes, num_tipos_componentes, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema):
        #variáveis para execução do algoritmo de busca por harmonia
        self.num_individuos = len(individuos) #quantidade de individuos
        self.num_variaveis = num_variaveis
        self.num_geracoes = num_geracoes
        self.HCMR = 0.8 #Harmony Memory Consideration Rate entre 0.7 e 0.95
        self.PAR = 0.3 #Pitch Adjustment Rate entre 0.1 e 0.5
        self.bw = 0.8 #pitch bandwidth (por variável) (escala do problema)

        self.num_tipos_componentes = num_tipos_componentes

        self.componentes = componentes
        self.peso_max = peso_max
        self.custo_max = custo_max

        self.num_max_componentes_subsistema = num_max_componentes_subsistema
        self.num_min_componentes_subsistema = num_min_componentes_subsistema

        self.individuos = []
        for i in range(self.num_individuos):
            self.individuos.append(deepcopy(individuos[i]))
        self.individuos = sorted(self.individuos, key=lambda x: x.valor_funcao_objetivo, reverse=True)

    def cria_harmonia(self, pior_individuo_pop, populacao):
        pior_individuo = deepcopy(pior_individuo_pop)
        linha = 0
        while(linha < 2): #duas linhas
            for i in range(self.num_variaveis):
                rand_hcmr = random.random()
                rand_par = random.random()
                if(rand_hcmr < self.HCMR): #Exploração
                    random_index = random.randint(0, self.num_individuos - 2) # -2 para não pegar o pior individuo
                    individuo_random = deepcopy(populacao[random_index])
                    valor_individuo_random = individuo_random.solucao[linha][i]
                    novo_valor = valor_individuo_random
                    if(rand_par < self.PAR): #Intensificaçao
                        novo_valor = valor_individuo_random + round(self.bw * (2*random.random()-1)) #aleatoriedade
                        #limitando o valor ao intervalo válido
                        if(linha == 1): #linha quantidade
                            if(novo_valor < self.num_min_componentes_subsistema):
                                novo_valor = self.num_min_componentes_subsistema
                            elif(novo_valor > self.num_max_componentes_subsistema):
                                novo_valor = self.num_max_componentes_subsistema
                        else:
                            if(novo_valor < 0):
                                novo_valor = 0
                            elif(novo_valor > self.num_tipos_componentes -1):
                                novo_valor = self.num_tipos_componentes -1
                else:
                    #gera valor aletatório
                    if(linha == 1): #linha quantidade
                        novo_valor = random.randint(self.num_min_componentes_subsistema, self.num_max_componentes_subsistema)
                    else:
                        novo_valor = random.randint(0, self.num_tipos_componentes -1)
                pior_individuo.solucao[linha][i] = novo_valor
            linha += 1
        pior_individuo.solucao = pior_individuo.solucao #reforçando a atribuição para recalcular os valores de desempenho
        return pior_individuo

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

    def truncate(self, number, decimals=0):
        factor = 10 ** decimals
        return math.trunc(number * factor) / factor

def main(componentes, individuos, peso_max, custo_max, num_geracoes, num_tipos_componentes, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema, porcentagem_criacao):
    alg = HarmonySearchAlgorithm(componentes, individuos, peso_max, custo_max, num_geracoes, num_tipos_componentes, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema)

    print("POPULAÇÃO INICIAL:")
    for l in range(len(alg.individuos)):
        print("Individuo {}:".format(l+1))
        print(alg.individuos[l])
        print(" ")
    print(" ")

    if(porcentagem_criacao > 0):
        numero_recalc = len(alg.individuos)*porcentagem_criacao
    else:
        numero_recalc = 1

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
            geracao = 1
            melhor_tempo = time.time() - start_time
    solucoes_log.append(melhor_solucao_log)
    solucoes.append(melhor_individuo.valor_funcao_objetivo)
    solucoes_avaliacoes.append(melhor_individuo.valor_funcao_objetivo)
    tempos_melhor_solucao.append(time.time() - start_time)

    for i in range(alg.num_geracoes):
        print("GERACAO {}".format(i+1))

        for _ in range(int(numero_recalc)):
            pior_individuo_geracao = alg.individuos[-1]

            novo_individuo = alg.cria_harmonia(pior_individuo_geracao, alg.individuos)
            print("-----------------------------------------")
            print("Novo individuo gerado:")
            print(novo_individuo)
            print("-----------------------------------------")
            if(novo_individuo.valor_funcao_objetivo > pior_individuo_geracao.valor_funcao_objetivo):
                alg.individuos[-1] = novo_individuo

            alg.individuos = sorted(alg.individuos, key=lambda x: x.valor_funcao_objetivo, reverse=True)

            numero_avaliacoes += 1
            if(porcentagem_criacao > 0):
                solucoes_avaliacoes.append(alg.individuos[0].valor_funcao_objetivo)
            print("Número de avaliações até o momento:", numero_avaliacoes)
        
        # Limitando a população ao número máximo de indivíduos
        #populacao = alg.verifica_duplicados(populacao)
        #alg.individuos = populacao[:alg.num_individuos]

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
        tempos_melhor_solucao.append(time.time() - start_time)
        #devo adicionar a melhor solução atual ao vetor de soluções por avaliações
        if(porcentagem_criacao == 0):
            solucoes_avaliacoes.append(melhor_individuo.valor_funcao_objetivo)

    populacao = alg.individuos
    print("O algoritmo genetico obteve em", alg.num_geracoes, "geracoes o resultado para a funcao objetivo de", alg.individuos[0].valor_funcao_objetivo)
    print("Com os seguintes valores para cada variavel de decisao:")
    for z in range(alg.num_variaveis):
        print("T{}: {}".format(z+1, populacao[0].solucao[0][z]))
        print("Q{}: {}".format(z+1, populacao[0].solucao[1][z]))
    print("\n")

    # Plotando o gráfico
    #plt.axhline(y=0, color='red', linestyle='-', linewidth=0.4)  # Linha vermelha mais fina e plotada primeiro
    if(porcentagem_criacao == 0):
        plt.plot(range(0, alg.num_geracoes+1), solucoes, color='brown')  # Linha marrom/rosa plotada depois
    else:
        plt.plot(range(0, alg.num_geracoes+1), solucoes, color='#FF69B4')  # Linha marrom/rosa plotada depois
    # Configurações do gráfico
    plt.xlabel('Geração')
    plt.ylabel('Valor da Função Objetivo')

    if(porcentagem_criacao == 0):
        plt.title('Evolução da Melhor Solução ao Longo das Gerações (HS)')
    else:
        plt.title('Evolução da Melhor Solução ao Longo das Gerações (HS - Melhorado)')
    plt.grid(True)
    # Texto adicional no gráfico
    valor_final = alg.truncate(alg.individuos[0].confiabilidade_total, 4)
    texto = "Valor final: " + str(valor_final) + "\nAlcançado na geração: " + str(geracao)
    plt.figtext(0.87, 0.029, texto, wrap=True, horizontalalignment='center', fontsize=8)
    # Ajustes finais e salvamento
    plt.tight_layout()

    if(porcentagem_criacao == 0):
        plt.savefig('./HS/img/SolutionEvolutionHS.png')
    else:
        plt.savefig('./HS/img/SolutionEvolutionHSMelhorado.png')
    plt.show()

    # Plotando o gráfico em log
    if(porcentagem_criacao == 0):
        plt.plot(range(0, alg.num_geracoes+1), solucoes_log, color='brown')  # Linha marrom/rosa plotada depois
    else:
        plt.plot(range(0, alg.num_geracoes+1), solucoes_log, color='#FF69B4')  # Linha marrom/rosa plotada depois
    # Configurações do gráfico
    plt.xlabel('Geração')
    plt.ylabel('log(Função Objetivo)')

    if(porcentagem_criacao == 0):
        plt.title('Evolução da Melhor Solução ao Longo das Gerações (HS - Log)')
    else:
        plt.title('Evolução da Melhor Solução ao Longo das Gerações (HS - Log Melhorado)')
    plt.grid(True)
    # Texto adicional no gráfico
    valor_final_log = alg.truncate(melhor_solucao_log, 4)
    texto = "Valor final: " + str(valor_final_log) + "\nAlcançado na geração: " + str(geracao)
    plt.figtext(0.87, 0.029, texto, wrap=True, horizontalalignment='center', fontsize=8)
    # Ajustes finais e salvamento
    plt.tight_layout()
    if(porcentagem_criacao == 0):
        plt.savefig('./HS/img/SolutionEvolutionHSLog.png')
    else:
        plt.savefig('./HS/img/SolutionEvolutionHSMelhoradoLog.png')
    plt.show()

    # Plotando o gráfico com o número de avaliações
    #plt.figure(figsize=(20, 7))  # largura=20, altura=10 polegadas
    if(porcentagem_criacao == 0):
        plt.plot(range(0, numero_avaliacoes+1), solucoes_avaliacoes, color='brown')  # Linha marrom/rosa plotada depois
    else:
        plt.plot(range(0, numero_avaliacoes+1), solucoes_avaliacoes, color='#FF69B4')  # Linha marrom/rosa plotada depois
    # Configurações do gráfico
    plt.xlabel('Número de Avaliações')
    plt.ylabel('Valor da Função Objetivo')
    if(porcentagem_criacao == 0):
        plt.title('Evolução da Melhor Solução ao Longo das Avaliações (HS)')
    else:
        plt.title('Evolução da Melhor Solução ao Longo das Avaliações (HS - Melhorado)')
    plt.grid(True)
    # Texto adicional no gráfico
    valor_final = alg.truncate(alg.individuos[0].confiabilidade_total, 4)
    texto = "Valor final: " + str(valor_final) + "\nAlcançado na geração: " + str(geracao) + "\nNúmero de avaliações: " + str(numero_avaliacoes)
    plt.figtext(0.8, 0.05, texto, wrap=True, horizontalalignment='center', fontsize=8)
    # Ajustes finais e salvamento
    plt.subplots_adjust(bottom=0.2)
    if(porcentagem_criacao == 0):
        plt.savefig('./HS/img/SolutionEvolutionHSAvaliacoes.png')
    else:
        plt.savefig('./HS/img/SolutionEvolutionHSMelhoradoAvaliacoes.png')
    plt.show()

    # Plotando o gráfico com o tempo para alcançar a melhor solução
    if(porcentagem_criacao == 0):
        plt.plot(tempos_melhor_solucao, solucoes, color='brown')  # Linha marrom/rosa plotada depois
    else:
        plt.plot(tempos_melhor_solucao, solucoes, color='#FF69B4')  # Linha marrom/rosa plotada depois
    # Configurações do gráfico
    plt.xlabel('Geração')
    plt.ylabel('Tempo (s)')
    if(porcentagem_criacao == 0):
        plt.title('Evolução do Tempo para Alcançar a Melhor Solução (HS)')
    else:
        plt.title('Evolução do Tempo para Alcançar a Melhor Solução (HS - Melhorado)')
    plt.grid(True)
    # Texto adicional no gráfico
    valor_final = alg.truncate(alg.individuos[0].confiabilidade_total, 4)
    texto = "Valor final: " + str(valor_final) + "\nAlcançado no tempo: " + str(melhor_tempo)
    plt.figtext(0.87, 0.029, texto, wrap=True, horizontalalignment='center', fontsize=8)
    # Ajustes finais e salvamento
    plt.tight_layout()
    if(porcentagem_criacao == 0):
        plt.savefig('./HS/img/SolutionEvolutionHSTempo.png')
    else:
        plt.savefig('./HS/img/SolutionEvolutionHSMelhoradoTempo.png')
    plt.show()

    return solucoes_log, valor_final_log, melhor_individuo, geracao, numero_avaliacoes, solucoes_avaliacoes, tempos_melhor_solucao, melhor_tempo


if __name__ == "__main__":
    with open('output.txt', 'w') as f:
        with redirect_stdout(f):
            main()

    