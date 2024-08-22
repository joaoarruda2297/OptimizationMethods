import sys
from contextlib import redirect_stdout
import matplotlib.pyplot as plt

from DE.DiffEvolution import main as DE
from GA.Genetic import main as GA
from PSO.ParticleSwarm import main as PSO
from GeradorComponentes import main as Gerador

def main():
    # Variáveis para geração de componentes
    confiabilidade_minima = 0.5
    confiabilidade_maxima = 0.7
    num_tipos_componentes = 10
    lim_sup_peso = 15
    lim_inf_peso = 1
    lim_sup_custo = 25
    lim_inf_custo = 1

    # Variáveis para execução do algoritmo
    num_geracoes = 80
    peso_max = 120
    custo_max = 80

    componentes = Gerador(
        num_tipos_componentes,
        confiabilidade_maxima,
        confiabilidade_minima,
        lim_inf_custo,
        lim_sup_custo,
        lim_inf_peso,
        lim_sup_peso
    )

    for i in range(componentes.shape[1]):
        print("Componente {}:".format(i))
        print("Confiabilidade: {}".format(componentes[0][i]))
        print("Custo: {}".format(componentes[1][i]))
        print("Peso: {}\n".format(componentes[2][i]))

    # Executa PSO e captura os resultados
    with open('./PSO/output.txt', 'w') as f:
        sys.stdout = f
        try:
            solucoes_PSO, melhor_valor_PSO = PSO(componentes, peso_max, custo_max, num_geracoes)
        finally:
            sys.stdout = sys.__stdout__

    # Executa DE e captura os resultados
    with open('./DE/output.txt', 'w') as f:
        sys.stdout = f
        try:
            solucoes_DE, melhor_valor_DE = DE(componentes, peso_max, custo_max, num_geracoes)
        finally:
            sys.stdout = sys.__stdout__

    # Executa GA e captura os resultados
    with open('./GA/output.txt', 'w') as f:
        sys.stdout = f
        try:
            solucoes_GA, melhor_valor_GA = GA(componentes, peso_max, custo_max, num_geracoes)
        finally:
            sys.stdout = sys.__stdout__

    # Gerando o gráfico comparativo
    plt.axhline(y=0, color='red', linestyle='-', linewidth=0.4)
    plt.plot(range(1, len(solucoes_PSO) + 1), solucoes_PSO, label='PSO ({})'.format(melhor_valor_PSO), color='purple')
    plt.plot(range(1, len(solucoes_DE) + 1), solucoes_DE, label='DE ({})'.format(melhor_valor_DE), color='green')
    plt.plot(range(1, len(solucoes_GA) + 1), solucoes_GA, label='GA ({})'.format(melhor_valor_GA), color='orange')

    plt.xlabel('Geração')
    plt.ylabel('Valor da Função Objetivo')
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
