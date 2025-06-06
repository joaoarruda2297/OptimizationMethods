import numpy as np
import sys
from contextlib import redirect_stdout

class GeradorIndividuos:
    def __init__(self, num_tipos_componentes, num_individuos, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema, peso_max, custo_max, componentes):
        self.num_tipos_componentes = num_tipos_componentes
        self.num_individuos = num_individuos
        self.num_variaveis = num_variaveis
        self.num_max_componentes_subsistema = num_max_componentes_subsistema
        self.num_min_componentes_subsistema = num_min_componentes_subsistema
        self.peso_max = peso_max
        self.custo_max = custo_max
        self.componentes = componentes

    def somatoria_custos(self, individuo):
        custo_total = 0
        for subsistema in individuo:
            for componente in subsistema:
                if componente != -1:
                    custo_total += self.componentes[1][componente]
        return custo_total

    def somatoria_pesos(self, individuo):
        peso_total = 0
        for subsistema in individuo:
            for componente in subsistema:
                if componente != -1:
                    peso_total += self.componentes[2][componente]
        return peso_total

    def somatoria_componentes(self, individuo):
        for subsistema in individuo:
            if np.sum(subsistema) == -10:
                return True
        return False

    def gera_individuo(self):
        individuo = np.random.randint(-10, self.num_tipos_componentes, (self.num_variaveis, self.num_max_componentes_subsistema))
        for i in range(len(individuo)):
            for j in range(len(individuo[i])):
                if individuo[i][j] < 0:
                    individuo[i][j] = -1

        while self.somatoria_custos(individuo) > self.peso_max or self.somatoria_pesos(individuo) > self.custo_max or self.somatoria_componentes(individuo):
            individuo = np.random.randint(-10, self.num_tipos_componentes, (self.num_variaveis, self.num_max_componentes_subsistema))
            for i in range(len(individuo)):
                for j in range(len(individuo[i])):
                    if individuo[i][j] < 0:
                        individuo[i][j] = -1

        return individuo
        
    def cria_individuos(self):
        pop_inicial = []

        for i in range(self.num_individuos):
            pop_inicial.append(self.gera_individuo())

        return pop_inicial

def main(num_tipos_componentes, num_individuos, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema, peso_max, custo_max, componentes):
    generator = GeradorIndividuos(num_tipos_componentes, num_individuos, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema, peso_max, custo_max, componentes)
    individuos = generator.cria_individuos()
    return individuos

if __name__ == "__main__":
    with open('individuos.txt', 'w') as f:
        with redirect_stdout(f):
            main()