import numpy as np
import math
from contextlib import redirect_stdout
from copy import deepcopy
import matplotlib.pyplot as plt

class GeneticAlgorithm:
    def __init__(self):
        #variáveis para execução do algoritmo genético
        self.num_individuos = 3
        self.num_variaveis = 5 #5 subsistemas
        self.num_geracoes = 100
        self.taxa_cruzamento = 0.6 #quantidade de pais que gerarão individuos (pais/2)
        self.taxa_mutacao = 0.3 #quantidade de individuos que vão receber mutação

        #variáveis para geração de banco de dados de componentes
        self.num_tipos_componentes = 7
        self.lim_sup_peso = 10
        self.lim_inf_peso = 0
        self.lim_sup_custo = 10
        self.lim_inf_custo = 0
        self.peso_max = 20
        self.custo_max = 30

        self.num_max_componentes_subsistema = self.num_tipos_componentes
        self.num_min_componentes_subsistema = 3

        self.coeficiente_custo = 1.1
        self.coeficiente_peso = 1.05
        
        self.componentes = self.cria_componentes()
    
    def truncate(self, number, decimals=0):
        factor = 10.0 ** decimals
        return math.trunc(number * factor) / factor

    #ok
    def cria_componentes(self):
        linha1 = np.round(np.random.uniform(0.91, 0.99, self.num_tipos_componentes), 8)  # confiabilidade com max 8 casas decimais
        linha2 = np.random.randint(self.lim_inf_custo + 1, self.lim_sup_custo + 1, self.num_tipos_componentes)#custo
        linha3 = np.random.randint(self.lim_inf_peso + 1, self.lim_sup_peso + 1, self.num_tipos_componentes)#peso
        
        # Combina as linhas em uma matriz
        matriz = np.vstack([linha1, linha2, linha3])
        return matriz

    #ok
    def confiabilidade_paralelo(self, subsistema):
        confiabilidade = 1

        for i,componente in enumerate(subsistema):
            if componente != -1:
                conf_componente = self.componentes[0][componente]
                confiabilidade *= (1 - conf_componente)

        confiabilidade = self.truncate(1 - confiabilidade, 8)
        return confiabilidade

    #ok
    def confiabilidade_ponte(self, individuo):
        #considerando a confiabilidade do sistema em ponte
        r_1 = self.confiabilidade_paralelo(individuo[0])
        r_2 = self.confiabilidade_paralelo(individuo[1])
        r_3 = self.confiabilidade_paralelo(individuo[2])
        r_4 = self.confiabilidade_paralelo(individuo[3])
        r_5 = self.confiabilidade_paralelo(individuo[4])

        confiabilidade_sistema = (
            r_1*r_2 + r_3*r_4 + r_1*r_4*r_5 + r_2*r_3*r_5
            - r_1*r_2*r_3*r_4 - r_1*r_2*r_3*r_5 - r_1*r_2*r_4*r_5 - r_1*r_3*r_4*r_5 - r_2*r_3*r_4*r_5 
            + 2*r_1*r_2*r_3*r_4*r_5 
        )
        return confiabilidade_sistema

    #ok
    def somatoria_custos(self, individuo):
        custo_total = 0
        for subsistema in individuo:
            for componente in subsistema:
                if componente != -1:
                    custo_total += self.componentes[1][componente]
        print("Custo total:", custo_total)
        return custo_total

    #ok
    def somatoria_pesos(self, individuo):
        peso_total = 0
        for subsistema in individuo:
            for componente in subsistema:
                if componente != -1:
                    peso_total += self.componentes[2][componente]
        print("Peso total:", peso_total)
        return peso_total

    #ok
    def funcao_objetivo(self, individuo):
        confiabilidade = self.confiabilidade_ponte(individuo)

        soma_pesos = self.somatoria_pesos(individuo)
        soma_custos = self.somatoria_custos(individuo)

        f_custo = soma_custos - self.custo_max
        f_peso =  soma_pesos - self.peso_max

        f_obj = confiabilidade - self.coeficiente_peso*max(0, f_peso) - self.coeficiente_custo*max(0, f_custo)
        return f_obj

    #ok
    def avaliacao_populacao(self, populacao):
        pop_avaliada = [(self.funcao_objetivo(individuo), self.confiabilidade_ponte(individuo), individuo) for individuo in populacao]
        return pop_avaliada

    #ok
    def inicia_populacao(self):
        #gerando população inicial
        pop_inicial = np.random.randint(0, self.num_tipos_componentes, (self.num_individuos, self.num_variaveis, self.num_max_componentes_subsistema))

        #corrigindo quantos componentes cada subsistema irá ter
        for individuo in pop_inicial:
            for subsistema in individuo:
                num_componentes = np.random.randint(self.num_min_componentes_subsistema, self.num_max_componentes_subsistema+1)
                subsistema[num_componentes:] = -1

        pop_avaliada = self.avaliacao_populacao(pop_inicial)

        populacao = sorted(pop_avaliada, key=lambda x: x[0], reverse=True)
        return populacao


def main():
    alg = GeneticAlgorithm()
    populacao = alg.inicia_populacao()
    
    print("Componentes:")
    print(alg.componentes)

    print("\nPopulação:")
    print(populacao)
    

if __name__ == "__main__":
    with open('output.txt', 'w') as f:
        with redirect_stdout(f):
            main()

    