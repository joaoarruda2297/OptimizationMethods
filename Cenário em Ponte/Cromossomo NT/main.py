import math
import sys
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os

from Metodos.DE.DiffEvolution import main as DE
from Metodos.GA.Genetic import main as GA
from Metodos.PSO.ParticleSwarm import main as PSO
from Metodos.AC.AntColony import main as AC
from Metodos.ABC.BeeColony import main as ABC
from Metodos.HS.HarmonySearch import main as HS
from Geradores.GeradorComponentes import main as GeradorComponentes
from Geradores.GeradorIndividuos import main as GeradorIndividuos
from Geradores.GeradorComponentes import Componente
from Geradores.GeradorIndividuos import Individuo
from Geradores.main import main as GeradoresMain

def limpar_diretorio(caminho):
    """Limpa todos os arquivos de um diretório específico"""
    if os.path.exists(caminho):
        for arquivo in os.listdir(caminho):
            caminho_arquivo = os.path.join(caminho, arquivo)
            try:
                if os.path.isfile(caminho_arquivo):
                    os.unlink(caminho_arquivo)
            except Exception as e:
                print(f'Erro ao deletar {caminho_arquivo}: {e}')

def ler_componentes_excel(caminho_excel):
    df = pd.read_excel(caminho_excel)
    return [Componente(row["confiabilidade"], row["custo"], row["peso"]) for _, row in df.iterrows()]

def ler_individuos_excel(caminho_excel, componentes, custo_max, peso_max):
    df = pd.read_excel(caminho_excel)
    individuos = []
    for _, row in df.iterrows():
        tipos = eval(row["solucao_tipos"])
        quantidades = eval(row["solucao_quantidades"])
        solucao = np.vstack([tipos, quantidades])
        individuo = Individuo(solucao, componentes, custo_max, peso_max)
        individuos.append(individuo)
    return individuos

def main():
    def truncate(number, decimals=0):
        factor = 10 ** decimals
        return math.trunc(number * factor) / factor

    #QUALQUER TROCA DE VARIAVEL É OBRIGATORIA A RECRIAÇÃO DE INDIVIDUOS E COMPONENTES
    # Variáveis para geração de componentes e individuos
    confiabilidade_minima = 0.8
    confiabilidade_maxima = 0.9
    lim_sup_peso = 24
    lim_inf_peso = 12
    lim_sup_custo = 18
    lim_inf_custo = 9
    num_tipos_componentes = 10
    num_populacoes = 3
    num_individuos = 50
    num_variaveis = 5
    num_max_componentes_subsistema = 3
    num_min_componentes_subsistema = 1

    # Variáveis para execução do algoritmo
    num_geracoes = 200
    peso_max = 100
    custo_max = 80

    # A LÓGICA DE CRIAÇÃO DE INDIVÍDUOS FOI ALTERADA PARA QUE GERE 3 POPULAÇÕES VALIDAS DIFERENTES, LOGO SERÁ NUM_INVIDUOS * 3
    print("Deseja gerar indivíduos e componentes novamente? (S/N)")
    resposta = input().strip().upper()
    if resposta == "S":
        print("Gerando novos componentes e indivíduos...")
        limpar_diretorio("./Geradores/Excel")
        componentes, populacoes = GeradoresMain(
            num_populacoes,
            confiabilidade_maxima,
            confiabilidade_minima,
            num_tipos_componentes,
            num_individuos,
            num_variaveis,
            num_max_componentes_subsistema,
            num_min_componentes_subsistema,
            peso_max,
            custo_max,
            lim_inf_custo,
            lim_sup_custo,
            lim_inf_peso,
            lim_sup_peso
        )
        print("Componentes e indivíduos gerados com sucesso.")
    else:
        print("Lendo componentes e indivíduos dos arquivos Excel...")
        componentes = ler_componentes_excel("Geradores/Excel/componentes.xlsx")
        individuos = ler_individuos_excel("Geradores/Excel/individuos.xlsx", componentes, custo_max, peso_max)
        print("Componentes e indivíduos lidos com sucesso.")

    #Limpa diretórios de imagem e output antes de gerar novos resultados
    print("Limpando diretórios de imagens e outputs...")
    diretorios = ['./Metodos/GA/img', './Metodos/PSO/img', './Metodos/DE/img', './Metodos/AC/img', './Metodos/ABC/img', './Metodos/HS/img', './Metodos/GA/output', './Metodos/PSO/output', './Metodos/DE/output', './Metodos/AC/output', './Metodos/ABC/output', './Metodos/HS/output', './Graficos']
    for diretorio in diretorios:
        limpar_diretorio(diretorio)
    print("Diretórios limpos com sucesso.")

    for i, individuos in enumerate(populacoes):
        index = i + 1
        # Executa GA e captura os resultados
        with open(f'./Metodos/GA/output/output{index}.txt', 'w') as f:
            sys.stdout = f
            try:
                solucoes_GA, melhor_valor_GA, melhor_individuo_GA, geracao_GA, numero_avaliacoes_GA, solucoes_avaliacoes_GA, tempos_melhor_solucao_GA, melhor_tempo_GA = GA(index, componentes, individuos, peso_max, custo_max, num_geracoes, num_tipos_componentes, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema)
            finally:
                sys.stdout = sys.__stdout__

        # Executa PSO e captura os resultados
        with open(f'./Metodos/PSO/output/output{index}.txt', 'w') as f:
            sys.stdout = f
            try:
                solucoes_PSO, melhor_valor_PSO, melhor_individuo_PSO, geracao_PSO, numero_avaliacoes_PSO, solucoes_avaliacoes_PSO, tempos_melhor_solucao_PSO, melhor_tempo_PSO = PSO(index, componentes, individuos, peso_max, custo_max, num_geracoes, num_tipos_componentes, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema)
            finally:
                sys.stdout = sys.__stdout__

        # Executa DE e captura os resultados
        with open(f'./Metodos/DE/output/output{index}.txt', 'w') as f:
            sys.stdout = f
            try:
                solucoes_DE, melhor_valor_DE, melhor_individuo_DE, geracao_DE, numero_avaliacoes_DE, solucoes_avaliacoes_DE, tempos_melhor_solucao_DE, melhor_tempo_DE = DE(index, componentes,num_tipos_componentes, individuos, peso_max, custo_max, num_geracoes, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema)
            finally:
                sys.stdout = sys.__stdout__

        # Executa AntColony e captura os resultados
        with open(f'./Metodos/AC/output/output{index}.txt', 'w') as f:
            sys.stdout = f
            try:
                solucoes_AC, melhor_valor_AC, melhor_individuo_AC, geracao_AC, numero_avaliacoes_AC, solucoes_avaliacoes_AC, tempos_melhor_solucao_AC, melhor_tempo_AC = AC(index, componentes, individuos, peso_max, custo_max, num_geracoes, num_tipos_componentes, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema)
            finally:
                sys.stdout = sys.__stdout__
        
        # Executa Artificial Bee Colony e captura os resultados
        with open(f'./Metodos/ABC/output/output{index}.txt', 'w') as f:
            sys.stdout = f
            try:
                solucoes_ABC, melhor_valor_ABC, melhor_individuo_ABC, geracao_ABC, numero_avaliacoes_ABC, solucoes_avaliacoes_ABC, tempos_melhor_solucao_ABC, melhor_tempo_ABC = ABC(index, componentes, individuos, peso_max, custo_max, num_geracoes, num_tipos_componentes, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema)
            finally:
                sys.stdout = sys.__stdout__

        # Executa HS e captura os resultados
        with open(f'./Metodos/HS/output/output{index}.txt', 'w') as f:
            sys.stdout = f
            try:
                solucoes_HS, melhor_valor_HS, melhor_individuo_HS, geracao_HS, numero_avaliacoes_HS, solucoes_avaliacoes_HS, tempos_melhor_solucao_HS, melhor_tempo_HS = HS(index, componentes, individuos, peso_max, custo_max, num_geracoes, num_tipos_componentes, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema, porcentagem_criacao=0)
            finally:
                sys.stdout = sys.__stdout__

        # Executa HS melhorado e captura os resultados
        with open(f'./Metodos/HS/output/outputMelhorado{index}.txt', 'w') as f:
            sys.stdout = f
            try:
                solucoes_HS_melhorado, melhor_valor_HS_melhorado, melhor_individuo_HS_melhorado, geracao_HS_melhorado, numero_avaliacoes_HS_melhorado, solucoes_avaliacoes_HS_melhorado, tempos_melhor_solucao_HS_melhorado, melhor_tempo_HS_melhorado = HS(index, componentes, individuos, peso_max, custo_max, num_geracoes, num_tipos_componentes, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema, porcentagem_criacao=0.1)
            finally:
                sys.stdout = sys.__stdout__

        # Gerando o gráfico comparativo
        plt.plot(range(1, len(solucoes_PSO) + 1), solucoes_PSO, label='PSO ({})'.format(melhor_valor_PSO), color='purple')
        plt.plot(range(1, len(solucoes_DE) + 1), solucoes_DE, label='DE ({})'.format(melhor_valor_DE), color='green')
        plt.plot(range(1, len(solucoes_GA) + 1), solucoes_GA, label='GA ({})'.format(melhor_valor_GA), color='orange')
        plt.plot(range(1, len(solucoes_AC) + 1), solucoes_AC, label='ACO ({})'.format(melhor_valor_AC), color='blue')
        plt.plot(range(1, len(solucoes_ABC) + 1), solucoes_ABC, label='ABC ({})'.format(melhor_valor_ABC), color='red')
        plt.plot(range(1, len(solucoes_HS) + 1), solucoes_HS, label='HS ({})'.format(melhor_valor_HS), color='brown')
        plt.plot(range(1, len(solucoes_HS_melhorado) + 1), solucoes_HS_melhorado, label='HS Melhorado ({})'.format(melhor_valor_HS_melhorado), color='#FF69B4')

        plt.xlabel('Geração')
        plt.ylabel('log(Função Objetivo)')
        plt.title('Comparação dos Algoritmos')
        plt.legend()
        plt.grid(True)

        penalidade_GA = truncate(melhor_individuo_GA.valor_funcao_objetivo - melhor_individuo_GA.confiabilidade_total, 8)
        textoGA = "GA\nAlcançado na geração: " + str(geracao_GA) + "\nFunção Objetivo: " + str(truncate(melhor_individuo_GA.valor_funcao_objetivo, 8)) + "\nConfiabilidade: " + str(truncate(melhor_individuo_GA.confiabilidade_total, 8)) + "\nPenalidade: " + str(penalidade_GA) + "\nCusto: " + str(melhor_individuo_GA.custo) + "\nPeso: " + str(melhor_individuo_GA.peso)
        plt.figtext(0.08, 0.029, textoGA, wrap=True, horizontalalignment='center', fontsize=8)

        penalidade_PSO = truncate(melhor_individuo_PSO.valor_funcao_objetivo - melhor_individuo_PSO.confiabilidade_total, 8)
        textoPSO = "PSO\nAlcançado na geração: " + str(geracao_PSO) + "\nFunção Objetivo: " + str(truncate(melhor_individuo_PSO.valor_funcao_objetivo, 8)) + "\nConfiabilidade: " + str(truncate(melhor_individuo_PSO.confiabilidade_total, 8)) + "\nPenalidade: " + str(penalidade_PSO) + "\nCusto: " + str(melhor_individuo_PSO.custo) + "\nPeso: " + str(melhor_individuo_PSO.peso)
        plt.figtext(0.25, 0.029, textoPSO, wrap=True, horizontalalignment='center', fontsize=8)

        penalidade_DE = truncate(melhor_individuo_DE.valor_funcao_objetivo - melhor_individuo_DE.confiabilidade_total, 8)
        textoDE = "DE\nAlcançado na geração: " + str(geracao_DE) + "\nFunção Objetivo: " + str(truncate(melhor_individuo_DE.valor_funcao_objetivo, 8)) + "\nConfiabilidade: " + str(truncate(melhor_individuo_DE.confiabilidade_total, 8)) + "\nPenalidade: " + str(penalidade_DE) + "\nCusto: " + str(melhor_individuo_DE.custo) + "\nPeso: " + str(melhor_individuo_DE.peso)
        plt.figtext(0.80, 0.029, textoDE, wrap=True, horizontalalignment='center', fontsize=8)

        penalidade_AC = truncate(melhor_individuo_AC.valor_funcao_objetivo - melhor_individuo_AC.confiabilidade_total, 8)
        textoAC = "ACO\nAlcançado na geração: " + str(geracao_AC) + "\nFunção Objetivo: " + str(truncate(melhor_individuo_AC.valor_funcao_objetivo, 8)) + "\nConfiabilidade: " + str(truncate(melhor_individuo_AC.confiabilidade_total, 8)) + "\nPenalidade: " + str(penalidade_AC) + "\nCusto: " + str(melhor_individuo_AC.custo) + "\nPeso: " + str(melhor_individuo_AC.peso)
        plt.figtext(0.67, 0.029, textoAC, wrap=True, horizontalalignment='center', fontsize=8)

        penalidade_ABC = truncate(melhor_individuo_ABC.valor_funcao_objetivo - melhor_individuo_ABC.confiabilidade_total, 8)
        textoABC = "ABC\nAlcançado na geração: " + str(geracao_ABC) + "\nFunção Objetivo: " + str(truncate(melhor_individuo_ABC.valor_funcao_objetivo, 8)) + "\nConfiabilidade: " + str(truncate(melhor_individuo_ABC.confiabilidade_total, 8)) + "\nPenalidade: " + str(penalidade_ABC) + "\nCusto: " + str(melhor_individuo_ABC.custo) + "\nPeso: " + str(melhor_individuo_ABC.peso)
        plt.figtext(0.91, 0.029, textoABC, wrap=True, horizontalalignment='center', fontsize=8)

        penalidade_HS = truncate(melhor_individuo_HS.valor_funcao_objetivo - melhor_individuo_HS.confiabilidade_total, 8)
        textoHS = "HS\nAlcançado na geração: " + str(geracao_HS) + "\nFunção Objetivo: " + str(truncate(melhor_individuo_HS.valor_funcao_objetivo, 8)) + "\nConfiabilidade: " + str(truncate(melhor_individuo_HS.confiabilidade_total, 8)) + "\nPenalidade: " + str(penalidade_HS) + "\nCusto: " + str(melhor_individuo_HS.custo) + "\nPeso: " + str(melhor_individuo_HS.peso)
        plt.figtext(0.40, 0.029, textoHS, wrap=True, horizontalalignment='center', fontsize=8)

        penalidade_HS_melhorado = truncate(melhor_individuo_HS_melhorado.valor_funcao_objetivo - melhor_individuo_HS_melhorado.confiabilidade_total, 8)
        textoHS_melhorado = "HS Melhorado\nAlcançado na geração: " + str(geracao_HS_melhorado) + "\nFunção Objetivo: " + str(truncate(melhor_individuo_HS_melhorado.valor_funcao_objetivo, 8)) + "\nConfiabilidade: " + str(truncate(melhor_individuo_HS_melhorado.confiabilidade_total, 8)) + "\nPenalidade: " + str(penalidade_HS_melhorado) + "\nCusto: " + str(melhor_individuo_HS_melhorado.custo) + "\nPeso: " + str(melhor_individuo_HS_melhorado.peso)
        plt.figtext(0.54, 0.029, textoHS_melhorado, wrap=True, horizontalalignment='center', fontsize=8)

        # Ajustes finais e salvamento
        plt.subplots_adjust(bottom=0.2)
        plt.savefig(f'./Graficos/comparativeMethods{index}.png')
        plt.show()

        #Gerando o gráfico comparativo por numero de avaliacoes
        plt.plot(range(1, len(solucoes_avaliacoes_PSO) + 1), solucoes_avaliacoes_PSO, label='PSO ({})'.format(melhor_valor_PSO), color='purple')
        plt.plot(range(1, len(solucoes_avaliacoes_DE) + 1), solucoes_avaliacoes_DE, label='DE ({})'.format(melhor_valor_DE), color='green')
        plt.plot(range(1, len(solucoes_avaliacoes_GA) + 1), solucoes_avaliacoes_GA, label='GA ({})'.format(melhor_valor_GA), color='orange')
        plt.plot(range(1, len(solucoes_avaliacoes_AC) + 1), solucoes_avaliacoes_AC, label='ACO ({})'.format(melhor_valor_AC), color='blue')
        plt.plot(range(1, len(solucoes_avaliacoes_ABC) + 1), solucoes_avaliacoes_ABC, label='ABC ({})'.format(melhor_valor_ABC), color='red')
        plt.plot(range(1, len(solucoes_avaliacoes_HS) + 1), solucoes_avaliacoes_HS, label='HS ({})'.format(melhor_valor_HS), color='brown')
        plt.plot(range(1, len(solucoes_avaliacoes_HS_melhorado) + 1), solucoes_avaliacoes_HS_melhorado, label='HS Melhorado ({})'.format(melhor_valor_HS_melhorado), color='#FF69B4')

        plt.xlabel('Número de Avaliações')
        plt.ylabel('log(Função Objetivo)')
        plt.title('Comparação dos Algoritmos por Número de Avaliações')
        plt.legend()
        plt.grid(True)
        plt.subplots_adjust(bottom=0.2)
        plt.savefig(f'./comparativeMethodsAvaliacoes{index}.png')
        plt.show()

        # Gerando o gráfico comparativo por tempo até a melhor solução
        plt.plot(tempos_melhor_solucao_PSO, solucoes_PSO, label='PSO ({})'.format(melhor_valor_PSO), color='purple')
        plt.plot(tempos_melhor_solucao_DE, solucoes_DE, label='DE ({})'.format(melhor_valor_DE), color='green')
        plt.plot(tempos_melhor_solucao_GA, solucoes_GA, label='GA ({})'.format(melhor_valor_GA), color='orange')
        plt.plot(tempos_melhor_solucao_AC, solucoes_AC, label='ACO ({})'.format(melhor_valor_AC), color='blue')
        plt.plot(tempos_melhor_solucao_ABC, solucoes_ABC, label='ABC ({})'.format(melhor_valor_ABC), color='red')
        plt.plot(tempos_melhor_solucao_HS, solucoes_HS, label='HS ({})'.format(melhor_valor_HS), color='brown')
        plt.plot(tempos_melhor_solucao_HS_melhorado, solucoes_HS_melhorado, label='HS Melhorado ({})'.format(melhor_valor_HS_melhorado), color='#FF69B4')

        plt.xlabel('Tempo até a Melhor Solução (s)')
        plt.ylabel('log(Função Objetivo)')
        plt.title('Comparação dos Algoritmos por Tempo até a Melhor Solução')
        plt.legend()
        plt.grid(True)
        plt.subplots_adjust(bottom=0.2)
        plt.savefig(f'./comparativeMethodsTempo{index}.png')
        plt.show()

        plt.figure()
        for tempo, solucao, cor, label in [
            (tempos_melhor_solucao_PSO, solucoes_PSO, 'purple', f'PSO ({melhor_valor_PSO})'),
            (tempos_melhor_solucao_DE, solucoes_DE, 'green', f'DE ({melhor_valor_DE})'),
            (tempos_melhor_solucao_GA, solucoes_GA, 'orange', f'GA ({melhor_valor_GA})'),
            (tempos_melhor_solucao_AC, solucoes_AC, 'blue', f'ACO ({melhor_valor_AC})'),
            (tempos_melhor_solucao_ABC, solucoes_ABC, 'red', f'ABC ({melhor_valor_ABC})'),
            (tempos_melhor_solucao_HS, solucoes_HS, 'brown', f'HS ({melhor_valor_HS})'),
            (tempos_melhor_solucao_HS_melhorado, solucoes_HS_melhorado, '#FF69B4', f'HS Melhorado ({melhor_valor_HS_melhorado})')
        ]:
            # Filtrar pontos até 1 segundo
            pontos_filtrados = [(t, s) for t, s in zip(tempo, solucao) if t <= 1.0]
            if pontos_filtrados:
                if(tempo[-1] != 1.0):
                    pontos_filtrados.append((1.0, solucao[-1]))
                tempos, sols = zip(*pontos_filtrados)
                plt.plot(tempos, sols, label=label, color=cor)

        plt.xlabel('Tempo até a Melhor Solução (s)')
        plt.ylabel('log(Função Objetivo)')
        plt.title('Comparação dos Algoritmos por Tempo (truncado em 1s)')
        plt.legend()
        plt.grid(True)
        plt.xlim(-0.04, 1.04)
        plt.subplots_adjust(bottom=0.2)
        plt.savefig(f'./comparativeMethodsTempoTruncado{index}.png')
        plt.show()

if __name__ == "__main__":
    main()