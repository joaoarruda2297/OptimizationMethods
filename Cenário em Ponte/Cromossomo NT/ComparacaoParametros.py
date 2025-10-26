import sys
import pandas as pd
import os
import math

from Metodos.DE.DiffEvolution import main as DE
from Metodos.GA.Genetic import main as GA
from Metodos.PSO.ParticleSwarm import main as PSO
from Metodos.AC.AntColony import main as AC
from Metodos.ABC.BeeColony import main as ABC
from Metodos.HS.HarmonySearch import main as HS
from Geradores.GeradorGraficos import GeradorGraficos
from utils import limpar_diretorio

def combinar_parametros(parametros1, parametros2):
    combinacoes = []
    for p1 in parametros1:
        for p2 in parametros2:
            combinacoes.append((p1, p2))
    return combinacoes

def ComparacaoParametros(populacoes, componentes, peso_max, custo_max, num_geracoes, num_tipos_componentes, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema):
    estudo_parametro = True  # Indica que estamos em modo de estudo de parâmetro
    gerador_graficos = GeradorGraficos(caminho_salvamento="./Resultados/Graficos/Graficos Parametros/")
    #Parametros de estudo para GA
    GA_taxa_mutacao = [0.01, 0.05, 0.08, 0.1]
    GA_taxa_crossover = [0.05, 0.08, 0.11, 0.14, 0.17, 0.2]
    GA_parametros = combinar_parametros(GA_taxa_mutacao, GA_taxa_crossover)

    #limpando diretorios de estudo
    print("Limpando diretórios de estudo de resultados anteriores...")
    diretorios = ['./Resultados/Txt/Resultados Parametros/GA/','./Resultados/Txt/Resultados Parametros/PSO/','./Resultados/Txt/Resultados Parametros/DE/','./Resultados/Txt/Resultados Parametros/AC/','./Resultados/Txt/Resultados Parametros/ABC/','./Resultados/Txt/Resultados Parametros/HS/', './Resultados/Graficos/Graficos Parametros/']
    for diretorio in diretorios:
        limpar_diretorio(diretorio)
    print("Diretórios limpos com sucesso.")

    for i, individuos in enumerate(populacoes):
        index = i + 1
        original_stdout = sys.stdout
        GA_resultados_finais = []
        # Executa GA e captura os resultados
        for j, (taxa_mutacao, taxa_crossover) in enumerate(GA_parametros):
            GA_resultados = []
            print("Executando GA para população {} - Taxa de Mutação: {} - Taxa de Cross-Over: {}".format(index, taxa_mutacao, taxa_crossover))
            with open(f'./Resultados/Txt/Resultados Parametros/GA/output{index}-Combinacao{j}.txt', 'w', encoding='utf-8') as f:
                sys.stdout = f
                try:
                    solucoes_GA, melhor_valor_GA, melhor_individuo_GA, geracao_GA, numero_avaliacoes_GA, solucoes_avaliacoes_GA, tempos_melhor_solucao_GA, melhor_tempo_GA = GA(index, componentes, individuos, peso_max, custo_max, num_geracoes, num_tipos_componentes, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema, estudo_parametro, taxa_mutacao=taxa_mutacao, taxa_crossover=taxa_crossover)
                    GA_resultados.append((melhor_valor_GA, solucoes_avaliacoes_GA, taxa_mutacao, taxa_crossover))
                finally:
                    sys.stdout = original_stdout
            GA_resultados_finais.append(GA_resultados)
            print("GA-Taxa de Mutação executado com sucesso para população {}.".format(index))

        '''# Executa PSO e captura os resultados
        print("Executando PSO para população {}...".format(index))
        with open(f'./Metodos/PSO/output/output{index}.txt', 'w', encoding='utf-8') as f:
            sys.stdout = f
            try:
                solucoes_PSO, melhor_valor_PSO, melhor_individuo_PSO, geracao_PSO, numero_avaliacoes_PSO, solucoes_avaliacoes_PSO, tempos_melhor_solucao_PSO, melhor_tempo_PSO = PSO(index, componentes, individuos, peso_max, custo_max, num_geracoes, num_tipos_componentes, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema)
            finally:
                sys.stdout = sys.__stdout__
        print("PSO executado com sucesso para população {}.".format(index))

        # Executa DE e captura os resultados
        print("Executando DE para população {}...".format(index))
        with open(f'./Metodos/DE/output/output{index}.txt', 'w', encoding='utf-8') as f:
            sys.stdout = f
            try:
                solucoes_DE, melhor_valor_DE, melhor_individuo_DE, geracao_DE, numero_avaliacoes_DE, solucoes_avaliacoes_DE, tempos_melhor_solucao_DE, melhor_tempo_DE = DE(index, componentes,num_tipos_componentes, individuos, peso_max, custo_max, num_geracoes, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema)
            finally:
                sys.stdout = sys.__stdout__
        print("DE executado com sucesso para população {}.".format(index))

        # Executa AntColony e captura os resultados
        print("Executando AC para população {}...".format(index))
        with open(f'./Metodos/AC/output/output{index}.txt', 'w', encoding='utf-8') as f:
            sys.stdout = f
            try:
                solucoes_AC, melhor_valor_AC, melhor_individuo_AC, geracao_AC, numero_avaliacoes_AC, solucoes_avaliacoes_AC, tempos_melhor_solucao_AC, melhor_tempo_AC = AC(index, componentes, individuos, peso_max, custo_max, num_geracoes, num_tipos_componentes, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema)
            finally:
                sys.stdout = sys.__stdout__
        print("AC executado com sucesso para população {}.".format(index))
        
        # Executa Artificial Bee Colony e captura os resultados
        print("Executando ABC para população {}...".format(index))
        with open(f'./Metodos/ABC/output/output{index}.txt', 'w', encoding='utf-8') as f:
            sys.stdout = f
            try:
                solucoes_ABC, melhor_valor_ABC, melhor_individuo_ABC, geracao_ABC, numero_avaliacoes_ABC, solucoes_avaliacoes_ABC, tempos_melhor_solucao_ABC, melhor_tempo_ABC = ABC(index, componentes, individuos, peso_max, custo_max, num_geracoes, num_tipos_componentes, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema)
            finally:
                sys.stdout = sys.__stdout__
        print("ABC executado com sucesso para população {}.".format(index))

        # Executa HS e captura os resultados
        print("Executando HS para população {}...".format(index))
        with open(f'./Metodos/HS/output/output{index}.txt', 'w', encoding='utf-8') as f:
            sys.stdout = f
            try:
                solucoes_HS, melhor_valor_HS, melhor_individuo_HS, geracao_HS, numero_avaliacoes_HS, solucoes_avaliacoes_HS, tempos_melhor_solucao_HS, melhor_tempo_HS = HS(index, componentes, individuos, peso_max, custo_max, num_geracoes, num_tipos_componentes, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema, porcentagem_criacao=0)
            finally:
                sys.stdout = sys.__stdout__
        print("HS executado com sucesso para população {}.".format(index))

        # Executa HS melhorado e captura os resultados
        print("Executando HS Melhorado para população {}...".format(index))
        with open(f'./Metodos/HS/output/outputMelhorado{index}.txt', 'w', encoding='utf-8') as f:
            sys.stdout = f
            try:
                solucoes_HS_melhorado, melhor_valor_HS_melhorado, melhor_individuo_HS_melhorado, geracao_HS_melhorado, numero_avaliacoes_HS_melhorado, solucoes_avaliacoes_HS_melhorado, tempos_melhor_solucao_HS_melhorado, melhor_tempo_HS_melhorado = HS(index, componentes, individuos, peso_max, custo_max, num_geracoes, num_tipos_componentes, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema, porcentagem_criacao=0.1)
            finally:
                sys.stdout = sys.__stdout__
        print("HS Melhorado executado com sucesso para população {}.".format(index))'''

        # Organiza os resultados por taxa de mutação
        resultados_por_mutacao = {}
        for GA_taxa_mutacao_result in GA_resultados_finais:
            for resultados in GA_taxa_mutacao_result:
                melhor_valor_GA, solucoes_avaliacoes_GA, taxa_mutacao, taxa_crossover = resultados
                if taxa_mutacao not in resultados_por_mutacao:
                    resultados_por_mutacao[taxa_mutacao] = {}
                
                resultados_por_mutacao[taxa_mutacao][taxa_crossover] = {
                    'x': range(1, len(solucoes_avaliacoes_GA) + 1),
                    'y': solucoes_avaliacoes_GA,
                    'label': f'Taxa de Crossover: {taxa_crossover}',
                }
        
        # Gera um gráfico para cada taxa de mutação
        for taxa_mutacao in resultados_por_mutacao:
            gerador_graficos.gera_grafico_comparativo_parametros(
                nome_arquivo=f'Comparativo_GA_TaxaMut_{taxa_mutacao}_Pop_{index}.png',
                dicionario_parametros=resultados_por_mutacao[taxa_mutacao],
                title=f'Taxa de Mutação {taxa_mutacao} - População {index}',
                xlabel='Número de Avaliações',
                ylabel='log(Função Objetivo)'
            )
            print(f"Gráfico para Taxa de Mutação {taxa_mutacao} gerado com sucesso para população {index}.")

        # Criar matriz de resultados para o Excel
        resultados_matriz = {}
        for GA_taxa_mutacao_result in GA_resultados_finais:
            for resultados in GA_taxa_mutacao_result:
                melhor_valor_GA, solucoes_avaliacoes_GA, taxa_mutacao, taxa_crossover = resultados
                # Reverte o log natural (ln) para o valor original
                valor_original = math.exp(melhor_valor_GA)  # e^x, onde x é o ln(confiabilidade)
                if taxa_mutacao not in resultados_matriz:
                    resultados_matriz[taxa_mutacao] = {}
                resultados_matriz[taxa_mutacao][taxa_crossover] = valor_original  # Usa o valor original, não o log
        
        # Criar DataFrame do pandas
        df = pd.DataFrame(resultados_matriz).T  # Transpõe a matriz para ter mutação nas linhas e crossover nas colunas
        
        # Configurar formato com 6 casas decimais para todas as células
        df = df.round(6)  # Arredonda para 6 casas decimais
        
        # Criar diretório se não existir
        excel_path = f'./Resultados/Txt/Resultados Parametros/GA/resultados_parametros_pop_{index}.xlsx'
        os.makedirs(os.path.dirname(excel_path), exist_ok=True)
        
        # Salvar como Excel com formato específico
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=f'População {index}')
            # Configura o formato das células para 6 casas decimais
            workbook = writer.book
            worksheet = writer.sheets[f'População {index}']
            for col in range(len(df.columns) + 1):  # +1 para incluir o índice
                for row in range(len(df.index) + 1):  # +1 para incluir o cabeçalho
                    cell = worksheet.cell(row + 2, col + 2)  # +2 porque o Excel começa em 1 e temos o cabeçalho
                    if isinstance(cell.value, (float, int)):
                        cell.number_format = '0.000000'