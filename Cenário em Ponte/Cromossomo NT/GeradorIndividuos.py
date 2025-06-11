import numpy as np
from contextlib import redirect_stdout
import numpy as np
from decimal import Decimal, getcontext
from contextlib import redirect_stdout

class Individuo:
    def __init__(self, cromossomo=None, componentes=None, peso_max=0, custo_max=0, coeficiente_peso=1, coeficiente_custo=1):
        #print("Cromossomo: ", cromossomo)

        self.componentes = componentes
        self.peso_max = peso_max
        self.custo_max = custo_max
        self.cromossomo = cromossomo
        self.coeficiente_peso = coeficiente_peso
        self.coeficiente_custo = coeficiente_custo

        if cromossomo is not None:
            self.valor_funcao_objetivo = self.funcao_objetivo(cromossomo)
            self.confiabilidade_total = self.confiabilidade_ponte(cromossomo)
        else:
            self.valor_funcao_objetivo = None
            self.confiabilidade_total = None

    def __str__(self):
        return (
            "{\n"
            f"  \"cromossomo\": {self.cromossomo[0]}\n"
            f"                {self.cromossomo[1]},\n"
            f"  \"funcao_objetivo\": {self.valor_funcao_objetivo},\n"
            f"  \"confiabilidade_total\": {self.confiabilidade_total}\n"
            "}"
        )

    def funcao_objetivo(self, individuo):
        confiabilidade = Decimal(self.confiabilidade_ponte(individuo))

        soma_pesos = self.somatoria_pesos(individuo)
        soma_custos = self.somatoria_custos(individuo)

        f_custo = soma_custos - self.custo_max
        f_peso =  soma_pesos - self.peso_max

        f_obj = confiabilidade - Decimal(self.coeficiente_peso*max(0, f_peso)) - Decimal(self.coeficiente_custo*max(0, f_custo))
        return f_obj

    def confiabilidade_paralelo(self, tipo, quantidade):
        getcontext().prec = 50
        confiabilidade = Decimal(1)

        for i in range(quantidade):
            conf_componente = Decimal(self.componentes[0][tipo])
            confiabilidade = confiabilidade*(1 - conf_componente)

        confiabilidade = 1 - confiabilidade
        return confiabilidade

    def confiabilidade_ponte(self, individuo):
        getcontext().prec = 50
        #considerando a confiabilidade do sistema em ponte
        r_1 = Decimal(self.confiabilidade_paralelo(individuo[0][0], individuo[1][0]))
        r_2 = Decimal(self.confiabilidade_paralelo(individuo[0][1], individuo[1][1]))
        r_3 = Decimal(self.confiabilidade_paralelo(individuo[0][2], individuo[1][2]))
        r_4 = Decimal(self.confiabilidade_paralelo(individuo[0][3], individuo[1][3]))
        r_5 = Decimal(self.confiabilidade_paralelo(individuo[0][4], individuo[1][4]))

        confiabilidade_sistema = Decimal(
            r_1*r_2 + r_3*r_4 + r_1*r_4*r_5 + r_2*r_3*r_5
            - r_1*r_2*r_3*r_4 - r_1*r_2*r_3*r_5 - r_1*r_2*r_4*r_5 - r_1*r_3*r_4*r_5 - r_2*r_3*r_4*r_5 
            + 2*r_1*r_2*r_3*r_4*r_5 
        )

        return confiabilidade_sistema
    
    def somatoria_custos(self, individuo):
        custo_total = 0
        for i in range(len(individuo[0])):
            custo_total += self.componentes[1][individuo[0][i]] * individuo[1][i]
        return custo_total

    def somatoria_pesos(self, individuo):
        peso_total = 0
        for i in range(len(individuo[0])):
            peso_total += self.componentes[2][individuo[0][i]] * individuo[1][i]
        return peso_total

class GeradorIndividuos:
    def __init__(self, num_tipos_componentes, num_individuos, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema, peso_max, custo_max, componentes, coeficiente_custo, coeficiente_peso):
        self.num_tipos_componentes = num_tipos_componentes
        self.num_individuos = num_individuos
        self.num_variaveis = num_variaveis
        self.num_max_componentes_subsistema = num_max_componentes_subsistema
        self.num_min_componentes_subsistema = num_min_componentes_subsistema
        self.peso_max = peso_max
        self.custo_max = custo_max
        self.componentes = componentes
        self.coeficiente_custo = coeficiente_custo
        self.coeficiente_peso = coeficiente_peso

    def gera_individuo(self):
        while True:
            # Gera tipos de componentes aleatórios [0, num_tipos_componentes)
            linha_tipos = np.random.randint(0, self.num_tipos_componentes, self.num_variaveis)

            # Gera quantidades aleatórias de componentes [min, max]
            linha_quantidades = np.random.randint(self.num_min_componentes_subsistema,self.num_max_componentes_subsistema + 1,self.num_variaveis)

            # Empilha o cromossomo
            cromossomo = np.vstack((linha_tipos, linha_quantidades))

            # Cria o indivíduo
            individuo = Individuo(cromossomo, self.componentes, self.peso_max,
                                self.custo_max, self.coeficiente_peso, self.coeficiente_custo)

            # Retorna apenas indivíduos viáveis
            if individuo.valor_funcao_objetivo >= 0:
                return individuo
        
    def cria_individuos(self):
        pop_inicial = []

        for i in range(self.num_individuos):
            pop_inicial.append(self.gera_individuo())

        return pop_inicial

def main(num_tipos_componentes, num_individuos, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema, peso_max, custo_max, componentes, coeficiente_custo, coeficiente_peso):
    generator = GeradorIndividuos(num_tipos_componentes, num_individuos, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema, peso_max, custo_max, componentes, coeficiente_custo, coeficiente_peso)
    individuos = generator.cria_individuos()
    return individuos

if __name__ == "__main__":
    with open('individuos.txt', 'w') as f:
        with redirect_stdout(f):
            main()