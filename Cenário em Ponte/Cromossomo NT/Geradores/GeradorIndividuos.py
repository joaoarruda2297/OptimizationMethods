import os
import numpy as np
from contextlib import redirect_stdout
import numpy as np
from decimal import Decimal, getcontext
from contextlib import redirect_stdout
from copy import deepcopy

class Individuo:
    def __init__(self, solucao=None, componentes=None, peso_max=0, custo_max=0):
        self.componentes = componentes
        self.peso_max = peso_max
        self.custo_max = custo_max

        self._solucao = None
        self.valor_funcao_objetivo = self.funcao_objetivo(solucao) if solucao is not None else None
        self.confiabilidade_total = self.confiabilidade_ponte(solucao) if solucao is not None else None

        self.solucao = solucao

        self.peso = self.somatoria_pesos(solucao) if solucao is not None else None
        self.custo = self.somatoria_custos(solucao) if solucao is not None else None

    def __str__(self):
        return (
            "{\n"
            f"  \"solucao\": {self.solucao[0]}\n"
            f"                {self.solucao[1]},\n"
            f"  \"funcao_objetivo\": {self.valor_funcao_objetivo},\n"
            f"  \"confiabilidade_total\": {self.confiabilidade_total}\n"
            f"  \"peso\": {self.peso},\n"
            f"  \"custo\": {self.custo}\n"
            "}"
        )

    @property
    def solucao(self):
        return self._solucao

    @solucao.setter
    def solucao(self, nova_solucao):
        self._solucao = nova_solucao
        if nova_solucao is not None:
            self.peso = self.somatoria_pesos(nova_solucao)
            self.custo = self.somatoria_custos(nova_solucao)
            self.valor_funcao_objetivo = self.funcao_objetivo(nova_solucao)
            self.confiabilidade_total = self.confiabilidade_ponte(nova_solucao)
        else:
            self.valor_funcao_objetivo = None
            self.confiabilidade_total = None

    def funcao_objetivo(self, individuo):
        confiabilidade = Decimal(self.confiabilidade_ponte(individuo))

        soma_pesos = self.somatoria_pesos(individuo)
        soma_custos = self.somatoria_custos(individuo)

        f_custo = (self.custo_max - soma_custos)/self.custo_max
        f_peso = (self.peso_max - soma_pesos)/self.peso_max

        f_obj = confiabilidade + Decimal(min(0, f_peso)) + Decimal(min(0, f_custo))
        return f_obj

    def confiabilidade_paralelo(self, tipo, quantidade):
        getcontext().prec = 50
        confiabilidade = Decimal(1)
        for _ in range(int(quantidade)):
            conf_componente = Decimal(self.componentes[int(tipo)].confiabilidade)
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
            custo_total += self.componentes[int(individuo[0][i])].custo * int(individuo[1][i])
        return custo_total

    def somatoria_pesos(self, individuo):
        peso_total = 0
        for i in range(len(individuo[0])):
            peso_total += self.componentes[int(individuo[0][i])].peso * int(individuo[1][i])
        return peso_total
    
class IndividuoABC(Individuo):
    def __init__(self, solucao=None, componentes=None, peso_max=0, custo_max=0):
        super().__init__(solucao, componentes, peso_max, custo_max)
        self.estagnacao = 0

    def __str__(self):
        return (
            "{\n"
            f"  \"solucao\": {self.solucao[0]}\n"
            f"                {self.solucao[1]},\n"
            f"  \"funcao_objetivo\": {self.valor_funcao_objetivo},\n"
            f"  \"confiabilidade_total\": {self.confiabilidade_total}\n"
            f"  \"estagnacao\": {self.estagnacao},\n"
            "}"
        )

class IndividuoPSO(Individuo):
    def __init__(self, solucao=None, componentes=None, velocidade=None, peso_max=0, custo_max=0, num_variaveis=0):
        super().__init__(solucao, componentes, peso_max, custo_max)

        self.num_variaveis = num_variaveis

        self.velocidade = None
        if velocidade is None:
            self.velocidade = self.gera_velocidade()

        self.melhor_posicao = None
        if solucao is not None:
            self.melhor_posicao = deepcopy(self)

    def __str__(self):
        return (
            "{\n"
            f"  \"Posicao\": {self.solucao[0]}\n"
            f"             {self.solucao[1]},\n"
            f"  \"Velocidade\": {self.velocidade[0]}\n"
            f"                {self.velocidade[1]},\n"
            f"  \"funcao_objetivo\": {self.valor_funcao_objetivo},\n"
            f"  \"confiabilidade_total\": {self.confiabilidade_total}\n"
            "}"
        )

    def gera_velocidade(self):
        velocidade = np.zeros((2, self.num_variaveis))
        return velocidade
    
class GeradorIndividuos:
    def __init__(self, num_populacoes, num_tipos_componentes, num_individuos, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema, peso_max, custo_max, componentes):
        self.num_populacoes = num_populacoes
        self.num_tipos_componentes = num_tipos_componentes
        self.num_individuos = num_individuos
        self.num_variaveis = num_variaveis
        self.num_max_componentes_subsistema = num_max_componentes_subsistema
        self.num_min_componentes_subsistema = num_min_componentes_subsistema
        self.peso_max = peso_max
        self.custo_max = custo_max
        self.componentes = componentes

        self.contador = 0

    def gera_individuo(self):
        while True:
            self.contador += 1
            # Gera tipos de componentes aleatórios [0, num_tipos_componentes)
            linha_tipos = np.random.randint(0, self.num_tipos_componentes, self.num_variaveis)

            # Gera quantidades aleatórias de componentes [min, max]
            linha_quantidades = np.random.randint(self.num_min_componentes_subsistema,self.num_max_componentes_subsistema + 1,self.num_variaveis)

            # Empilha o cromossomo
            solucao = np.vstack((linha_tipos, linha_quantidades))

            # Cria o indivíduo
            individuo = Individuo(solucao, self.componentes, self.peso_max, self.custo_max)

            # Retorna apenas indivíduos viáveis
            if individuo.confiabilidade_total == individuo.valor_funcao_objetivo:
                return individuo
        
    def cria_individuos(self):
        pop_inicial = []

        for _ in range(self.num_individuos*self.num_populacoes):
            pop_inicial.append(self.gera_individuo())

        return pop_inicial

def main(num_populacoes, num_tipos_componentes, num_individuos, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema, peso_max, custo_max, componentes):
    generator = GeradorIndividuos(num_populacoes,num_tipos_componentes, num_individuos, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema, peso_max, custo_max, componentes)
    individuos = generator.cria_individuos()
    populacoes = np.array_split(individuos, generator.num_populacoes)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    txt_dir = os.path.join(base_dir, 'Txt')
    os.makedirs(txt_dir, exist_ok=True)

    with open(os.path.join(txt_dir, 'individuos.txt'), 'w') as f:
        print(f"Total de tentativas para gerar individuos: {generator.contador}\n", file=f)
        for p, populacao in enumerate(populacoes):
            print(f"POPULACAO {p+1}:\n", file=f)
            for i, individuo in enumerate(populacao):
                print(f"Individuo {i+1}: {individuo}", file=f)

    return populacoes