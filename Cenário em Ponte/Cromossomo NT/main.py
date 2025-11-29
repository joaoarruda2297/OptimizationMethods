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
from Geradores.GeradorGraficos import GeradorGraficos
from utils import limpar_diretorio, ler_componentes_excel, ler_individuos_excel
from ComparacaoParametros import ComparacaoParametros

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
    num_populacoes = 5
    num_individuos = 50
    num_variaveis = 5
    num_max_componentes_subsistema = 3
    num_min_componentes_subsistema = 1

    # Variáveis para execução do algoritmo
    num_geracoes = 200
    peso_max = 120
    custo_max = 100

    arquivosBase = [f for f in os.listdir('./Geradores/Excel') if f.endswith(".xlsx")]
    arquivosIndividuos = [f for f in os.listdir('./Geradores/Excel') if f.endswith(".xlsx") and f.startswith("individuos")]
    if len(arquivosIndividuos) == 0:
        print("Não foram encontrados arquivos base na pasta './Geradores/Excel'. Será necessário gerar componentes e indivíduos.")
        resposta = "1"
    elif len(arquivosIndividuos) != num_populacoes:
        print(f'Quantidade de arquivos base na pasta ./Geradores/Excel ({len(arquivosIndividuos)}) é diferente do utilizado como parâmetro ({num_populacoes}). Será necessário gerar componentes e indivíduos.')
        resposta = "1"
    elif len(arquivosIndividuos) == num_populacoes:
        #encontrar se em arquivos existem os individuos e se existem os componentes
        individuos_existentes = any("individuos" in f for f in arquivosBase)
        componentes_existentes = any("componentes" in f for f in arquivosBase)
        print("Foram encontrados arquivos base:")
        if individuos_existentes and componentes_existentes:
            print("- Indivíduos e Componentes")
        elif individuos_existentes:
            print("- Indivíduos")
        elif componentes_existentes:
            print("- Componentes")
        print("===============================")
        print("Deseja:")
        print("1 - Gerar novos indivíduos e componentes")
        print("2 - Utilizar os indivíduos e componentes existentes")
        resposta = input().strip().upper()
    if resposta == "1":
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
        populacoes = ler_individuos_excel("Geradores/Excel", componentes, custo_max, peso_max)
        print("Componentes e indivíduos lidos com sucesso.")

    print("Escolha:")
    print("1 - Otimizar o sistema")
    print("2 - Fazer estudo de parâmetros")
    print("3 - Ambos")
    respostaAlgoritmo = input().strip().upper()

    if(respostaAlgoritmo == "2" or respostaAlgoritmo == "3"):
        #Faz o estudo de parametros inicialmente
        print("Iniciando estudo de parâmetros...")
        ComparacaoParametros(populacoes, componentes, peso_max, custo_max, num_geracoes, num_tipos_componentes, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema)
        print("Estudo de parâmetros concluído.")

    if(respostaAlgoritmo == "1" or respostaAlgoritmo == "3"):
        #Executa a otimização dos sistemas
        print("Iniciando otimização dos sistemas...")
        #Limpa diretórios de imagem e output antes de gerar novos resultados
        print("Limpando diretórios de imagens e outputs...")
        diretorios = ['./Metodos/GA/img', './Metodos/PSO/img', './Metodos/DE/img', './Metodos/AC/img', './Metodos/ABC/img', './Metodos/HS/img', './Metodos/GA/output', './Metodos/PSO/output', './Metodos/DE/output', './Metodos/AC/output', './Metodos/ABC/output', './Metodos/HS/output', './Resultados/Graficos/Graficos Comparativos', './Resultados/Txt/Resultados Comparativos']
        for diretorio in diretorios:
            limpar_diretorio(diretorio)
        print("Diretórios limpos com sucesso.")

        for i, individuos in enumerate(populacoes):
            index = i + 1
            # Executa GA e captura os resultados
            original_stdout = sys.stdout
            print("Executando GA para população {}...".format(index))
            with open(f'./Metodos/GA/output/output{index}.txt', 'w', encoding='utf-8') as f:
                sys.stdout = f
                try:
                    solucoes_GA, melhor_valor_GA, melhor_individuo_GA, geracao_GA, numero_avaliacoes_GA, solucoes_avaliacoes_GA, tempos_melhor_solucao_GA, melhor_tempo_GA = GA(index, componentes, individuos, peso_max, custo_max, num_geracoes, num_tipos_componentes, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema)
                finally:
                    sys.stdout = original_stdout  # Restore using our saved reference
            print("GA executado com sucesso para população {}.".format(index))

            # Executa PSO e captura os resultados
            print("Executando PSO para população {}...".format(index))
            with open(f'./Metodos/PSO/output/output{index}.txt', 'w', encoding='utf-8') as f:
                sys.stdout = f
                try:
                    solucoes_PSO, melhor_valor_PSO, melhor_individuo_PSO, geracao_PSO, numero_avaliacoes_PSO, solucoes_avaliacoes_PSO, tempos_melhor_solucao_PSO, melhor_tempo_PSO = PSO(index, componentes, individuos, peso_max, custo_max, num_geracoes, num_tipos_componentes, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema)
                finally:
                    sys.stdout = original_stdout  # Restore using our saved reference
            print("PSO executado com sucesso para população {}.".format(index))

            # Executa DE e captura os resultados
            print("Executando DE para população {}...".format(index))
            with open(f'./Metodos/DE/output/output{index}.txt', 'w', encoding='utf-8') as f:
                sys.stdout = f
                try:
                    solucoes_DE, melhor_valor_DE, melhor_individuo_DE, geracao_DE, numero_avaliacoes_DE, solucoes_avaliacoes_DE, tempos_melhor_solucao_DE, melhor_tempo_DE = DE(index, componentes,num_tipos_componentes, individuos, peso_max, custo_max, num_geracoes, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema)
                finally:
                    sys.stdout = original_stdout  # Restore using our saved reference
            print("DE executado com sucesso para população {}.".format(index))

            # Executa AntColony e captura os resultados
            print("Executando AC para população {}...".format(index))
            with open(f'./Metodos/AC/output/output{index}.txt', 'w', encoding='utf-8') as f:
                sys.stdout = f
                try:
                    solucoes_AC, melhor_valor_AC, melhor_individuo_AC, geracao_AC, numero_avaliacoes_AC, solucoes_avaliacoes_AC, tempos_melhor_solucao_AC, melhor_tempo_AC = AC(index, componentes, individuos, peso_max, custo_max, num_geracoes, num_tipos_componentes, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema)
                finally:
                    sys.stdout = original_stdout  # Restore using our saved reference
            print("AC executado com sucesso para população {}.".format(index))
            
            # Executa Artificial Bee Colony e captura os resultados
            print("Executando ABC para população {}...".format(index))
            with open(f'./Metodos/ABC/output/output{index}.txt', 'w', encoding='utf-8') as f:
                sys.stdout = f
                try:
                    solucoes_ABC, melhor_valor_ABC, melhor_individuo_ABC, geracao_ABC, numero_avaliacoes_ABC, solucoes_avaliacoes_ABC, tempos_melhor_solucao_ABC, melhor_tempo_ABC = ABC(index, componentes, individuos, peso_max, custo_max, num_geracoes, num_tipos_componentes, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema)
                finally:
                    sys.stdout = original_stdout  # Restore using our saved reference
            print("ABC executado com sucesso para população {}.".format(index))

            # Executa HS e captura os resultados
            print("Executando HS para população {}...".format(index))
            with open(f'./Metodos/HS/output/output{index}.txt', 'w', encoding='utf-8') as f:
                sys.stdout = f
                try:
                    solucoes_HS, melhor_valor_HS, melhor_individuo_HS, geracao_HS, numero_avaliacoes_HS, solucoes_avaliacoes_HS, tempos_melhor_solucao_HS, melhor_tempo_HS = HS(index, componentes, individuos, peso_max, custo_max, num_geracoes, num_tipos_componentes, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema, porcentagem_criacao=0)
                finally:
                    sys.stdout = original_stdout  # Restore using our saved reference
            print("HS executado com sucesso para população {}.".format(index))

            # Executa HS melhorado e captura os resultados
            print("Executando HS Melhorado para população {}...".format(index))
            with open(f'./Metodos/HS/output/outputMelhorado{index}.txt', 'w', encoding='utf-8') as f:
                sys.stdout = f
                try:
                    solucoes_HS_melhorado, melhor_valor_HS_melhorado, melhor_individuo_HS_melhorado, geracao_HS_melhorado, numero_avaliacoes_HS_melhorado, solucoes_avaliacoes_HS_melhorado, tempos_melhor_solucao_HS_melhorado, melhor_tempo_HS_melhorado = HS(index, componentes, individuos, peso_max, custo_max, num_geracoes, num_tipos_componentes, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema, porcentagem_criacao=0.1)
                finally:
                    sys.stdout = original_stdout  # Restore using our saved reference
            print("HS Melhorado executado com sucesso para população {}.".format(index))

            # Gerando o gráficos comparativos
            gerador_graficos = GeradorGraficos(caminho_salvamento="./Resultados/Graficos/Graficos Comparativos/")

            dicionario_metodos_geracao = {
                'PSO': {'x': range(1, len(solucoes_PSO) + 1), 'y': solucoes_PSO, 'color': 'purple', 'label': 'PSO ({})'.format(melhor_valor_PSO)},
                'DE': {'x': range(1, len(solucoes_DE) + 1), 'y': solucoes_DE, 'color': 'green', 'label': 'DE ({})'.format(melhor_valor_DE)},
                'GA': {'x': range(1, len(solucoes_GA) + 1), 'y': solucoes_GA, 'color': 'orange', 'label': 'GA ({})'.format(melhor_valor_GA)},
                'ACO': {'x': range(1, len(solucoes_AC) + 1), 'y': solucoes_AC, 'color': 'blue', 'label': 'ACO ({})'.format(melhor_valor_AC)},
                'ABC': {'x': range(1, len(solucoes_ABC) + 1), 'y': solucoes_ABC, 'color': 'red', 'label': 'ABC ({})'.format(melhor_valor_ABC)},
                'HS': {'x': range(1, len(solucoes_HS) + 1), 'y': solucoes_HS, 'color': 'brown', 'label': 'HS ({})'.format(melhor_valor_HS)},
                'HSM': {'x': range(1, len(solucoes_HS_melhorado) + 1), 'y': solucoes_HS_melhorado, 'color': '#FF69B4', 'label': 'HSM ({})'.format(melhor_valor_HS_melhorado)}
            }
            gerador_graficos.gera_grafico_comparativo(f'./comparativeMethods{index}.png', dicionario_metodos_geracao, 'Comparação dos Algoritmos', 'Geração', 'log(Função Objetivo)', show_plot=False)

            penalidade_GA = truncate(melhor_individuo_GA.valor_funcao_objetivo - melhor_individuo_GA.confiabilidade_total, 8)
            textoGA = "\nAlcançado na geração: " + str(geracao_GA) + "\nFunção Objetivo: " + str(truncate(melhor_individuo_GA.valor_funcao_objetivo, 8)) + "\nConfiabilidade: " + str(truncate(melhor_individuo_GA.confiabilidade_total, 8)) + "\nPenalidade: " + str(penalidade_GA) + "\nCusto: " + str(melhor_individuo_GA.custo) + "\nPeso: " + str(melhor_individuo_GA.peso)
            penalidade_PSO = truncate(melhor_individuo_PSO.valor_funcao_objetivo - melhor_individuo_PSO.confiabilidade_total, 8)
            textoPSO = "\nAlcançado na geração: " + str(geracao_PSO) + "\nFunção Objetivo: " + str(truncate(melhor_individuo_PSO.valor_funcao_objetivo, 8)) + "\nConfiabilidade: " + str(truncate(melhor_individuo_PSO.confiabilidade_total, 8)) + "\nPenalidade: " + str(penalidade_PSO) + "\nCusto: " + str(melhor_individuo_PSO.custo) + "\nPeso: " + str(melhor_individuo_PSO.peso)
            penalidade_DE = truncate(melhor_individuo_DE.valor_funcao_objetivo - melhor_individuo_DE.confiabilidade_total, 8)
            textoDE = "\nAlcançado na geração: " + str(geracao_DE) + "\nFunção Objetivo: " + str(truncate(melhor_individuo_DE.valor_funcao_objetivo, 8)) + "\nConfiabilidade: " + str(truncate(melhor_individuo_DE.confiabilidade_total, 8)) + "\nPenalidade: " + str(penalidade_DE) + "\nCusto: " + str(melhor_individuo_DE.custo) + "\nPeso: " + str(melhor_individuo_DE.peso)
            penalidade_AC = truncate(melhor_individuo_AC.valor_funcao_objetivo - melhor_individuo_AC.confiabilidade_total, 8)
            textoAC = "\nAlcançado na geração: " + str(geracao_AC) + "\nFunção Objetivo: " + str(truncate(melhor_individuo_AC.valor_funcao_objetivo, 8)) + "\nConfiabilidade: " + str(truncate(melhor_individuo_AC.confiabilidade_total, 8)) + "\nPenalidade: " + str(penalidade_AC) + "\nCusto: " + str(melhor_individuo_AC.custo) + "\nPeso: " + str(melhor_individuo_AC.peso)
            penalidade_ABC = truncate(melhor_individuo_ABC.valor_funcao_objetivo - melhor_individuo_ABC.confiabilidade_total, 8)
            textoABC = "\nAlcançado na geração: " + str(geracao_ABC) + "\nFunção Objetivo: " + str(truncate(melhor_individuo_ABC.valor_funcao_objetivo, 8)) + "\nConfiabilidade: " + str(truncate(melhor_individuo_ABC.confiabilidade_total, 8)) + "\nPenalidade: " + str(penalidade_ABC) + "\nCusto: " + str(melhor_individuo_ABC.custo) + "\nPeso: " + str(melhor_individuo_ABC.peso)
            penalidade_HS = truncate(melhor_individuo_HS.valor_funcao_objetivo - melhor_individuo_HS.confiabilidade_total, 8)
            textoHS = "\nAlcançado na geração: " + str(geracao_HS) + "\nFunção Objetivo: " + str(truncate(melhor_individuo_HS.valor_funcao_objetivo, 8)) + "\nConfiabilidade: " + str(truncate(melhor_individuo_HS.confiabilidade_total, 8)) + "\nPenalidade: " + str(penalidade_HS) + "\nCusto: " + str(melhor_individuo_HS.custo) + "\nPeso: " + str(melhor_individuo_HS.peso)
            penalidade_HS_melhorado = truncate(melhor_individuo_HS_melhorado.valor_funcao_objetivo - melhor_individuo_HS_melhorado.confiabilidade_total, 8)
            textoHS_melhorado = "HS Melhorado\nAlcançado na geração: " + str(geracao_HS_melhorado) + "\nFunção Objetivo: " + str(truncate(melhor_individuo_HS_melhorado.valor_funcao_objetivo, 8)) + "\nConfiabilidade: " + str(truncate(melhor_individuo_HS_melhorado.confiabilidade_total, 8)) + "\nPenalidade: " + str(penalidade_HS_melhorado) + "\nCusto: " + str(melhor_individuo_HS_melhorado.custo) + "\nPeso: " + str(melhor_individuo_HS_melhorado.peso)

            with open(f'./Resultados/Txt/Resultados Comparativos/output{index}.txt', 'w', encoding='utf-8') as f:
                sys.stdout = f
                try:
                    print("===== Resultados Comparativos dos Algoritmos - População {} =====".format(index))
                    print("PSO: {}\n".format(textoPSO))
                    print("DE: {}\n".format(textoDE))
                    print("GA: {}\n".format(textoGA))
                    print("ACO: {}\n".format(textoAC))
                    print("ABC: {}\n".format(textoABC))
                    print("HS: {}\n".format(textoHS))
                    print("HS Melhorado: {}\n".format(textoHS_melhorado))
                finally:
                    sys.stdout = original_stdout  # Restore using our saved reference

            #Gerando o gráfico comparativo por numero de avaliacoes
            dicionario_metodos_avaliacoes = {
                'PSO': {'x': range(1, len(solucoes_avaliacoes_PSO) + 1), 'y': solucoes_avaliacoes_PSO, 'color': 'purple', 'label': 'PSO ({})'.format(melhor_valor_PSO)},
                'DE': {'x': range(1, len(solucoes_avaliacoes_DE) + 1), 'y': solucoes_avaliacoes_DE, 'color': 'green', 'label': 'DE ({})'.format(melhor_valor_DE)},
                'GA': {'x': range(1, len(solucoes_avaliacoes_GA) + 1), 'y': solucoes_avaliacoes_GA, 'color': 'orange', 'label': 'GA ({})'.format(melhor_valor_GA)},
                'ACO': {'x': range(1, len(solucoes_avaliacoes_AC) + 1), 'y': solucoes_avaliacoes_AC, 'color': 'blue', 'label': 'ACO ({})'.format(melhor_valor_AC)},
                'ABC': {'x': range(1, len(solucoes_avaliacoes_ABC) + 1), 'y': solucoes_avaliacoes_ABC, 'color': 'red', 'label': 'ABC ({})'.format(melhor_valor_ABC)},
                'HS': {'x': range(1, len(solucoes_avaliacoes_HS) + 1), 'y': solucoes_avaliacoes_HS, 'color': 'brown', 'label': 'HS ({})'.format(melhor_valor_HS)},
                'HS Melhorado': {'x': range(1, len(solucoes_avaliacoes_HS_melhorado) + 1), 'y': solucoes_avaliacoes_HS_melhorado, 'color': '#FF69B4', 'label': 'HSM ({})'.format(melhor_valor_HS_melhorado)}
            }

            gerador_graficos.gera_grafico_comparativo(f'./comparativeMethodsAvaliacoes{index}.png', dicionario_metodos_avaliacoes, 'Comparação dos Algoritmos por Número de Avaliações', 'Número de Avaliações', 'Função Objetivo')

            # Gerando o gráfico comparativo por tempo até a melhor solução
            dicionario_metodos_tempo = {
                'PSO': {'x': tempos_melhor_solucao_PSO, 'y': solucoes_PSO, 'color': 'purple', 'label': 'PSO ({})'.format(melhor_valor_PSO)},
                'DE': {'x': tempos_melhor_solucao_DE, 'y': solucoes_DE, 'color': 'green', 'label': 'DE ({})'.format(melhor_valor_DE)},
                'GA': {'x': tempos_melhor_solucao_GA, 'y': solucoes_GA, 'color': 'orange', 'label': 'GA ({})'.format(melhor_valor_GA)},
                'ACO': {'x': tempos_melhor_solucao_AC, 'y': solucoes_AC, 'color': 'blue', 'label': 'ACO ({})'.format(melhor_valor_AC)},
                'ABC': {'x': tempos_melhor_solucao_ABC, 'y': solucoes_ABC, 'color': 'red', 'label': 'ABC ({})'.format(melhor_valor_ABC)},
                'HS': {'x': tempos_melhor_solucao_HS, 'y': solucoes_HS, 'color': 'brown', 'label': 'HS ({})'.format(melhor_valor_HS)},
                'HS Melhorado': {'x': tempos_melhor_solucao_HS_melhorado, 'y': solucoes_HS_melhorado, 'color': '#FF69B4', 'label': 'HSM ({})'.format(melhor_valor_HS_melhorado)}
            }

            gerador_graficos.gera_grafico_comparativo(f'./comparativeMethodsTempo{index}.png', dicionario_metodos_tempo, 'Comparação dos Algoritmos por Tempo', 'Tempo até a Melhor Solução (s)', 'log(Função Objetivo)', show_plot=False)

            gerador_graficos.gera_grafico_comparativo_truncado(f'./comparativeMethodsTempoTruncado{index}.png', dicionario_metodos_tempo, 'Comparação dos Algoritmos por Tempo\n(truncado em 1s)', 'Tempo até a Melhor Solução (s)', 'log(Função Objetivo)', 1.0 ,[-0.04, 1.04])

            #Gera novo grafico comparativo de 3 metodos apenas
            dicionario_metodos_animais = {
                'PSO': {'x': range(1, len(solucoes_avaliacoes_PSO) + 1), 'y': solucoes_avaliacoes_PSO, 'color': 'purple', 'label': 'PSO ({})'.format(melhor_valor_PSO)},
                'ACO': {'x': range(1, len(solucoes_avaliacoes_AC) + 1), 'y': solucoes_avaliacoes_AC, 'color': 'blue', 'label': 'ACO ({})'.format(melhor_valor_AC)},
                'ABC': {'x': range(1, len(solucoes_avaliacoes_ABC) + 1), 'y': solucoes_avaliacoes_ABC, 'color': 'red', 'label': 'ABC ({})'.format(melhor_valor_ABC)},
            }

            gerador_graficos.gera_grafico_comparativo(f'./comparativeMethodsAvaliacoesAnimais{index}.png', dicionario_metodos_animais, 'Comparação dos Algoritmos por Avaliações', 'Número de Avaliações', 'log(Função Objetivo)')

            gerador_graficos.gera_grafico_comparativo_truncado(f'./comparativeMethodsAvaliacoesAnimaisTruncado{index}.png', dicionario_metodos_animais, 'Comparação dos Algoritmos por Avaliações\n(Truncado em 200 avaliações)', 'Número de Avaliações', 'Função Objetivo', 200)

            #Gera novo grafico comparativo de 3 metodos apenas
            dicionario_metodos_principais = {
                'DE': {'x': range(1, len(solucoes_avaliacoes_DE) + 1), 'y': solucoes_avaliacoes_DE, 'color': 'green', 'label': 'DE ({})'.format(melhor_valor_DE)},
                'GA': {'x': range(1, len(solucoes_avaliacoes_GA) + 1), 'y': solucoes_avaliacoes_GA, 'color': 'orange', 'label': 'GA ({})'.format(melhor_valor_GA)},
                'HS': {'x': range(1, len(solucoes_avaliacoes_HS) + 1), 'y': solucoes_avaliacoes_HS, 'color': 'brown', 'label': 'HS ({})'.format(melhor_valor_HS)},
                'HS Melhorado': {'x': range(1, len(solucoes_avaliacoes_HS_melhorado) + 1), 'y': solucoes_avaliacoes_HS_melhorado, 'color': '#FF69B4', 'label': 'HSM ({})'.format(melhor_valor_HS_melhorado)}
            }

            gerador_graficos.gera_grafico_comparativo(f'./comparativeMethodsAvaliacoesPrincipais{index}.png', dicionario_metodos_principais, 'Comparação dos Algoritmos por Avaliações', 'Número de Avaliações', 'log(Função Objetivo)')

            gerador_graficos.gera_grafico_comparativo_truncado(f'./comparativeMethodsAvaliacoesPrincipaisTruncado{index}.png', dicionario_metodos_principais, 'Comparação dos Algoritmos por Avaliações\n(Truncado em 200 avaliações)', 'Número de Avaliações', 'Função Objetivo', 200)

            #Grafico comparativo dos dois ultimos finais
            dicionario_metodos_finais = {
                'GA': {'x': range(1, len(solucoes_avaliacoes_GA) + 1), 'y': solucoes_avaliacoes_GA, 'color': 'orange', 'label': 'GA ({})'.format(melhor_valor_GA)},
                'ACO': {'x': range(1, len(solucoes_avaliacoes_AC) + 1), 'y': solucoes_avaliacoes_AC, 'color': 'blue', 'label': 'ACO ({})'.format(melhor_valor_AC)},
            }

            gerador_graficos.gera_grafico_comparativo_truncado(f'./comparativeMethodsAvaliacoesFinaisTruncado{index}.png', dicionario_metodos_finais, 'Comparação dos Algoritmos Finais por Avaliações\n(Truncado em 200 avaliações)', 'Número de Avaliações', 'Função Objetivo', 200)
            

if __name__ == "__main__":
    main()