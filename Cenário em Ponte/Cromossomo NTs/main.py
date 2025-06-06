import sys
from contextlib import redirect_stdout
import matplotlib.pyplot as plt

from DE.DiffEvolution import main as DE
from GA.Genetic import main as GA
from PSO.ParticleSwarm import main as PSO
from GeradorComponentes import main as GeradorComponentes
from GeradorIndividuos import main as GeradorIndividuos

def main():
    # Variáveis para geração de componentes e individuos
    confiabilidade_minima = 0.5
    confiabilidade_maxima = 0.7
    lim_sup_peso = 15
    lim_inf_peso = 1
    lim_sup_custo = 25
    lim_inf_custo = 1
    num_tipos_componentes = 10
    num_individuos = 50
    num_variaveis = 5
    num_max_componentes_subsistema = 10
    num_min_componentes_subsistema = 3

    # Variáveis para execução do algoritmo
    num_geracoes = 80
    peso_max = 1200
    custo_max = 800

    componentes = GeradorComponentes(
        num_tipos_componentes,
        confiabilidade_maxima,
        confiabilidade_minima,
        lim_inf_custo,
        lim_sup_custo,
        lim_inf_peso,
        lim_sup_peso
    )

    individuos = GeradorIndividuos(
        num_tipos_componentes,
        num_individuos,
        num_variaveis,
        num_max_componentes_subsistema,
        num_min_componentes_subsistema,
        peso_max,
        custo_max,
        componentes
    )

    for i in range(len(individuos)):
        print("Individuo {}:".format(i))
        print(individuos[i])

    print("")

    for i in range(componentes.shape[1]):
        print("Componente {}:".format(i))
        print("Confiabilidade: {}".format(componentes[0][i]))
        print("Custo: {}".format(componentes[1][i]))
        print("Peso: {}\n".format(componentes[2][i]))

    # Executa GA e captura os resultados
    with open('./GA/output.txt', 'w') as f:
        sys.stdout = f
        try:
            solucoes_GA, melhor_valor_GA = GA(componentes, individuos, peso_max, custo_max, num_geracoes)
        finally:
            sys.stdout = sys.__stdout__    

    # Executa PSO e captura os resultados
    with open('./PSO/output.txt', 'w') as f:
        sys.stdout = f
        try:
            solucoes_PSO, melhor_valor_PSO = PSO(componentes, individuos, peso_max, custo_max, num_geracoes)
        finally:
            sys.stdout = sys.__stdout__

    # Executa DE e captura os resultados
    with open('./DE/output.txt', 'w') as f:
        sys.stdout = f
        try:
            solucoes_DE, melhor_valor_DE = DE(componentes, individuos, peso_max, custo_max, num_geracoes)
        finally:
            sys.stdout = sys.__stdout__

    # Gerando o gráfico comparativo
    #plt.axhline(y=0, color='red', linestyle='-', linewidth=0.4)
    plt.plot(range(1, len(solucoes_PSO) + 1), solucoes_PSO, label='PSO ({})'.format(melhor_valor_PSO), color='purple')
    plt.plot(range(1, len(solucoes_DE) + 1), solucoes_DE, label='DE ({})'.format(melhor_valor_DE), color='green')
    plt.plot(range(1, len(solucoes_GA) + 1), solucoes_GA, label='GA ({})'.format(melhor_valor_GA), color='orange')

    plt.xlabel('Geração')
    plt.ylabel('log(confiabilidade)')
    plt.title('Comparação dos Algoritmos')
    plt.legend()
    plt.grid(True)

    # Ajustes finais e salvamento
    plt.tight_layout()
    plt.savefig('./comparativeMethods.png')
    plt.show()

if __name__ == "__main__":
    with open('components.txt', 'w') as f:
        with redirect_stdout(f):
            main()
