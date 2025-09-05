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
from GeradorIndividuos import IndividuoABC
    
class BeeColonyAlgorithm:
    def __init__(self, componentes, individuos, peso_max, custo_max, num_geracoes, coeficiente_custo, coeficiente_peso, num_tipos_componentes, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema):
        #variáveis para execução do algoritmo de colônia de abelhas
        self.num_individuos = len(individuos) #quantidade de individuos
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

        # variaveis para controle do algoritmo
        self.estagnacao_max = 10

        self.individuos = []
        for i in range(len(individuos)):
            self.individuos.append(IndividuoABC(individuos[i].solucao, componentes, peso_max, custo_max, coeficiente_peso, coeficiente_custo))
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

        respeita_limite = False
        while(not respeita_limite):
            phi = random.uniform(-1,1)
            valor_final_nova_solucao = valor_nova_solucao + phi*(valor_nova_solucao - valor_solucao_diferente)
            if(linha == 0): #linha tipos
                if(valor_final_nova_solucao >= 0 and valor_final_nova_solucao < self.num_tipos_componentes):
                    respeita_limite = True
            else: #linha quantidades
                if(valor_final_nova_solucao >= self.num_min_componentes_subsistema and valor_final_nova_solucao <= self.num_max_componentes_subsistema):
                    respeita_limite = True

        #arredondando o valor final da nova solução
        valor_final_nova_solucao_inteira = int(round(valor_final_nova_solucao))
        #corrigindo possíveis erros de arredondamento
        if(linha == 0 and valor_final_nova_solucao_inteira == self.num_tipos_componentes):
            valor_final_nova_solucao_inteira -= 1
        if(linha == 1 and valor_final_nova_solucao_inteira > self.num_max_componentes_subsistema):
            valor_final_nova_solucao_inteira = self.num_max_componentes_subsistema
        if(linha == 1 and valor_final_nova_solucao_inteira < self.num_min_componentes_subsistema):
            valor_final_nova_solucao_inteira = self.num_min_componentes_subsistema
                
        nova_solucao[linha][coluna] = valor_final_nova_solucao_inteira
        
        #cria novo indivíduo com a nova solução
        novo_individuo = IndividuoABC(nova_solucao, self.componentes, self.peso_max,
                            self.custo_max, self.coeficiente_peso, self.coeficiente_custo)

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

        for i in range(len(populacao)):
            probabilidade = populacao[i].valor_funcao_objetivo / total_aptidao
            if(probabilidade > probabilidade_minima):
                self.atualiza_solucao(populacao, i)

    def abelhas_observadoras(self, populacao):
        for i in range(len(populacao)):
            if(populacao[i].estagnacao >= self.estagnacao_max):
                populacao[i] = self.gera_nova_abelha()
                
    
    def gera_nova_abelha(self):
        while True:
            linha_tipos = np.random.randint(0, self.num_tipos_componentes, self.num_variaveis)
            linha_quantidades = np.random.randint(self.num_min_componentes_subsistema,self.num_max_componentes_subsistema + 1,self.num_variaveis)
            solucao = np.vstack((linha_tipos, linha_quantidades))

            # Cria o indivíduo
            individuo = IndividuoABC(solucao, self.componentes, self.peso_max,
                                self.custo_max, self.coeficiente_peso, self.coeficiente_custo)

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

    def truncate(self, number, decimals=0):
        factor = 10 ** decimals
        return math.trunc(number * factor) / factor

def main(componentes, individuos, peso_max, custo_max, num_geracoes, coeficiente_custo, coeficiente_peso, num_tipos_componentes, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema):
    alg = BeeColonyAlgorithm(componentes, individuos, peso_max, custo_max, num_geracoes, coeficiente_custo, coeficiente_peso, num_tipos_componentes, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema)

    print("POPULAÇÃO INICIAL:")
    for l in range(len(alg.individuos)):
        print("Individuo {}:".format(l+1))
        print(alg.individuos[l])
        print(" ")
    print(" ")

    melhores_abelhas = []
    solucoes = []
    solucoes_log = []
    melhor_solucao_log = -10000
    geracao = -1
    melhor_individuo: IndividuoABC = alg.individuos[1] #qualquer só para inicializar

    for j in range(len(alg.individuos)):
        if(alg.individuos[j].valor_funcao_objetivo > melhor_individuo.valor_funcao_objetivo):
            log_individuo = math.log(alg.individuos[j].valor_funcao_objetivo)
            melhor_solucao_log = log_individuo
            melhor_individuo = alg.individuos[j]
            geracao = 1
    solucoes_log.append(melhor_solucao_log)
    solucoes.append(melhor_individuo.valor_funcao_objetivo)
    melhores_abelhas.append(melhor_individuo)

    for i in range(alg.num_geracoes):
        print("GERACAO {}".format(i+1))
        #Fase das abelhas empregadas
        alg.abelhas_empregadas(alg.individuos)

        #Fase das abelhas exploradoras
        alg.abelhas_exploradoras(alg.individuos)

        #memoriza melhor solucao do momento
        for j in range(len(alg.individuos)):
            if(alg.individuos[j].valor_funcao_objetivo > melhor_individuo.valor_funcao_objetivo):
                log_individuo = math.log(alg.individuos[j].valor_funcao_objetivo)
                melhor_solucao_log = log_individuo
                melhor_individuo = alg.individuos[j]
                geracao = i + 1
        solucoes_log.append(melhor_solucao_log)
        solucoes.append(melhor_individuo.valor_funcao_objetivo)
        melhores_abelhas.append(melhor_individuo)

        #Fase das abelhas observadoras
        alg.abelhas_observadoras(alg.individuos)

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
    print("O algoritmo de colônia de abelhas obteve em", alg.num_geracoes, "geracoes o resultado para a funcao objetivo de", alg.individuos[0].valor_funcao_objetivo)
    print("Com os seguintes valores para cada variavel de decisão:")
    for z in range(alg.num_variaveis):
        print("T{}: {}".format(z+1, melhor_individuo.solucao[0][z]))
        print("Q{}: {}".format(z+1, melhor_individuo.solucao[1][z]))
    print("\n")

    # Plotando o gráfico
    #plt.axhline(y=0, color='red', linestyle='-', linewidth=0.4)  # Linha vermelha mais fina e plotada primeiro
    plt.plot(range(0, alg.num_geracoes+1), solucoes, color='red')  # Linha vinho plotada depois
    # Configurações do gráfico
    plt.xlabel('Geração')
    plt.ylabel('Valor da Função Objetivo')
    plt.title('Evolução da Melhor Solução ao Longo das Gerações (ABC)')
    plt.grid(True)
    # Texto adicional no gráfico
    valor_final = alg.truncate(alg.individuos[0].confiabilidade_total, 4)
    texto = "Valor final: " + str(valor_final) + "\nAlcançado na geração: " + str(geracao)
    plt.figtext(0.87, 0.029, texto, wrap=True, horizontalalignment='center', fontsize=8)
    # Ajustes finais e salvamento
    plt.tight_layout()
    plt.savefig('./ABC/img/SolutionEvolutionABC.png')
    plt.show()

    # Plotando o gráfico em log
    plt.plot(range(0, alg.num_geracoes+1), solucoes_log, color='red')  # Linha laranja plotada depois
    # Configurações do gráfico
    plt.xlabel('Geração')
    plt.ylabel('log(Função Objetivo)')
    plt.title('Evolução da Melhor Solução ao Longo das Gerações (ABC)')
    plt.grid(True)
    # Texto adicional no gráfico
    valor_final_log = alg.truncate(melhor_solucao_log, 4)
    texto = "Valor final: " + str(valor_final_log) + "\nAlcançado na geração: " + str(geracao)
    plt.figtext(0.87, 0.029, texto, wrap=True, horizontalalignment='center', fontsize=8)
    # Ajustes finais e salvamento
    plt.tight_layout()
    plt.savefig('./ABC/img/SolutionEvolutionABCLog.png')
    plt.show()


    return solucoes_log, valor_final_log, melhor_individuo, geracao


if __name__ == "__main__":
    with open('output.txt', 'w') as f:
        with redirect_stdout(f):
            main()

    