from decimal import Decimal
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
from utils import limpar_diretorio, junta_excels

def combinar_parametros(parametros1, parametros2):
    combinacoes = []
    for p1 in parametros1:
        for p2 in parametros2:
            combinacoes.append((p1, p2))
    return combinacoes

def analisa_resultados_parametros_multiplos(resultados_finais, index, nome_variavel_one, nome_variavel_two, alg_nome, variavel_one_abreviada):
    gerador_graficos = GeradorGraficos(caminho_salvamento="./Resultados/Graficos/Graficos Parametros/")
    # Organiza os resultados por taxa de mutação
    resultados_por_variavel_one = {}
    for ALG_variavel_one_result in resultados_finais:
        for resultados in ALG_variavel_one_result:
            melhor_valor, solucoes_avaliacoes, variavel_one, variavel_two = resultados
            if variavel_one not in resultados_por_variavel_one:
                resultados_por_variavel_one[variavel_one] = {}
            
            resultados_por_variavel_one[variavel_one][variavel_two] = {
                'x': range(1, len(solucoes_avaliacoes) + 1),
                'y': solucoes_avaliacoes,
                'label': f'{nome_variavel_two}: {variavel_two}',
            }
    
    # Gera um gráfico para cada taxa de mutação
    for ALG_variavel_one in resultados_por_variavel_one:
        teste=f'Comparativo_{alg_nome}_{variavel_one_abreviada}_{ALG_variavel_one}_Pop_{index}.png'
        print("Nome arquivo:", teste)
        gerador_graficos.gera_grafico_comparativo_parametros(
            nome_arquivo=f'Comparativo_{alg_nome}_{variavel_one_abreviada}_{ALG_variavel_one}_Pop_{index}.png',
            dicionario_parametros=resultados_por_variavel_one[ALG_variavel_one],
            title=f'{nome_variavel_one} {ALG_variavel_one} - População {index}',
            xlabel='Número de Avaliações',
            ylabel='Função Objetivo'
        )
        print(f"Gráfico para {variavel_one} {ALG_variavel_one} gerado com sucesso para população {index}.")

    # Criar matriz de resultados para o Excel
    resultados_matriz = {}
    for ALG_variavel_one_result in resultados_finais:
        for resultados in ALG_variavel_one_result:
            melhor_valor, solucoes_avaliacoes, variavel_one, variavel_two = resultados
            # Reverte o log natural (ln) para o valor original
            valor_original = math.exp(melhor_valor)  # e^x, onde x é o ln(confiabilidade)
            if variavel_one not in resultados_matriz:
                resultados_matriz[variavel_one] = {}
            resultados_matriz[variavel_one][variavel_two] = valor_original  # Usa o valor original, não o log
    
    # Criar DataFrame do pandas
    df = pd.DataFrame(resultados_matriz).T  # Transpõe a matriz para ter mutação nas linhas e crossover nas colunas
    
    # Configurar formato com 6 casas decimais para todas as células
    df = df.round(6)  # Arredonda para 6 casas decimais
    
    # Criar diretório se não existir
    excel_path = f'./Resultados/Txt/Resultados Parametros/{alg_nome}/resultados_parametros_pop_{index}.xlsx'
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

def analisa_resultados_parametros_unico(resultados_finais, index, nome_variavel, alg_nome, variavel_abreviada, num_max_avaliacoes):
    gerador_graficos = GeradorGraficos(caminho_salvamento="./Resultados/Graficos/Graficos Parametros/")
    
    # Organiza os resultados em um formato adequado para o gráfico
    dicionario_parametros = {}
    valores_parametro = []
    melhores_valores = []
    
    for ALG_result in resultados_finais:
        for resultados in ALG_result:
            melhor_valor, solucoes_avaliacoes, variavel = resultados
            valores_parametro.append(variavel)
            dicionario_parametros[variavel] = {
                'x': range(1, len(solucoes_avaliacoes) + 1),
                'y': solucoes_avaliacoes,
                'label': f'{nome_variavel}: {variavel}',
            }
            melhor_valor = float(max(solucoes_avaliacoes[:num_max_avaliacoes]))
            melhores_valores.append(melhor_valor)
    
    # Gera o gráfico comparativo
    gerador_graficos.gera_grafico_comparativo_parametros(
        nome_arquivo=f'Comparativo_{alg_nome}_{variavel_abreviada}_Pop_{index}.png',
        dicionario_parametros=dicionario_parametros,
        title=f'Comparativo {nome_variavel} - População {index}',
        xlabel='Número de Avaliações',
        ylabel='Função Objetivo'
    )
    print(f"Gráfico comparativo de {nome_variavel} gerado com sucesso para população {index}.")
    
    # Criar DataFrame do pandas para Excel
    df = pd.DataFrame({
        nome_variavel: valores_parametro,
        'Melhor Valor': melhores_valores
    })
    
    # Configurar formato com 6 casas decimais
    df['Melhor Valor'] = df['Melhor Valor'].round(6)
    
    # Criar diretório se não existir
    excel_path = f'./Resultados/Txt/Resultados Parametros/{alg_nome}/resultados_parametros_pop_{index}.xlsx'
    os.makedirs(os.path.dirname(excel_path), exist_ok=True)
    
    # Salvar como Excel com formato específico
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=f'População {index}', index=False)
        # Configura o formato das células para 6 casas decimais
        worksheet = writer.sheets[f'População {index}']
        for row in range(len(df.index) + 1):  # +1 para incluir o cabeçalho
            cell = worksheet.cell(row + 2, 2)  # Coluna 2 (Melhor Valor)
            if isinstance(cell.value, (float, int)):
                cell.number_format = '0.000000'

def analisa_resultados_parametros_multiplos_desconexos(resultados_finais, index, nome_variavel_one, nome_variavel_two, alg_nome, num_max_avaliacoes):
    gerador_graficos = GeradorGraficos(caminho_salvamento="./Resultados/Graficos/Graficos Parametros/")
    # Organiza os resultados para o gráfico
    dicionario_parametros = {}
    combinacoes = []
    melhores_valores = []

    for ALG_result in resultados_finais:
        for resultados in ALG_result:
            melhor_valor, solucoes_avaliacoes, variavel_one, variavel_two = resultados
            label = f'{nome_variavel_one}: {variavel_one}, {nome_variavel_two}: {variavel_two}'
            dicionario_parametros[label] = {
                'x': range(1, len(solucoes_avaliacoes) + 1),
                'y': solucoes_avaliacoes,
                'label': label,
            }

            melhor_valor = float(max(solucoes_avaliacoes[:num_max_avaliacoes]))
            combinacoes.append(f'{variavel_one}, {variavel_two}')
            melhores_valores.append(melhor_valor)

    # Gera o gráfico único com todas as combinações
    gerador_graficos.gera_grafico_comparativo_parametros_truncado(
        nome_arquivo=f'Comparativo_{alg_nome}_Pop_{index}.png',
        dicionario_parametros=dicionario_parametros,
        title=f'Comparativo Parâmetros {alg_nome} - População {index}',
        xlabel='Número de Avaliações',
        ylabel='Função Objetivo',
        valor_truncamento=num_max_avaliacoes
    )
    print(f"Gráfico comparativo de parâmetros desconexos gerado com sucesso para população {index}.")
    # Cria DataFrame para Excel
    df = pd.DataFrame({
        'Combinação de Parâmetros': combinacoes,
        'Confiabilidade': melhores_valores
    })
    df['Confiabilidade'] = df['Confiabilidade'].round(6)

    excel_path = f'./Resultados/Txt/Resultados Parametros/{alg_nome}/resultados_parametros_pop_{index}.xlsx'
    os.makedirs(os.path.dirname(excel_path), exist_ok=True)

    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=f'População {index}', index=False)
        worksheet = writer.sheets[f'População {index}']
        for row in range(len(df.index) + 1):
            cell = worksheet.cell(row + 2, 2)  # Coluna 2 (Confiabilidade)
            if isinstance(cell.value, (float, int)):
                cell.number_format = '0.000000'

def ComparacaoParametros(populacoes, componentes, peso_max, custo_max, num_geracoes, num_max_avaliacoes, num_tipos_componentes, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema):
    estudo_parametro = True  # Indica que estamos em modo de estudo de parâmetro
    gerador_graficos = GeradorGraficos(caminho_salvamento="./Resultados/Graficos/Graficos Parametros/")

    '''#Parametros de estudo para GA
    GA_taxa_mutacao = [0.01, 0.05, 0.08, 0.1]
    GA_taxa_crossover = [0.05, 0.08, 0.11, 0.14, 0.17, 0.2]
    GA_parametros = combinar_parametros(GA_taxa_mutacao, GA_taxa_crossover)

    #Parametros de estudo para PSO
    PSO_C1 = [1.5, 1.8, 2.1, 2.3, 2.5]
    PSO_C2 = [1.5, 1.8, 2.1, 2.3, 2.5]
    PSO_parametros = combinar_parametros(PSO_C1, PSO_C2)

    #Parametros de Estudo para DE
    DE_passo = [0.4, 0.6, 0.8, 1]
    DE_cr = [0.1, 0.3, 0.5, 0.7, 0.9]
    DE_parametros = combinar_parametros(DE_passo, DE_cr)

    #Parametros de estudo para ACO
    ACO_evaporacao = [0.1, 0.2, 0.3, 0.4, 0.5]

    #Parametros de estudo para ABC
    # NAO EXISTE

    #Parametros de estudo para HS
    HS_HMCR = [0.7, 0.77, 0.85, 0.92, 0.95]
    HS_PAR = [0.1, 0.2, 0.3, 0.4, 0.5]
    HS_parametros = combinar_parametros(HS_PAR, HS_HMCR)'''

    GA_parametros = [(0.001, 0.90), (0.01, 0.80), (0.05, 0.70), (0.02, 0.85), (0.03, 0.75), (0.008, 0.65), (0.04, 0.95), (0.015, 0.60), (0.025, 0.88)]

    DE_parametros = [(0.20, 0.50), (0.50, 0.80), (0.90, 0.40), (0.70, 0.60), (0.30, 0.90), (0.60, 0.45), (0.80, 0.70), (0.40, 0.55), (0.85, 0.65), (0.25, 0.75)]

    PSO_parametros = [(2.00, 2.00), (1.50, 2.50), (2.05, 1.90), (2.20, 1.80), (1.80, 2.20), (2.10, 2.10), (1.60, 2.40), (2.30, 1.70), (1.90, 2.05), (2.05, 2.05)]

    ACO_evaporacao = [0.10, 0.30, 0.05, 0.20, 0.40, 0.15, 0.25, 0.08]

    HS_parametros = [(0.30, 0.90), (0.40, 0.75), (0.20, 0.85), (0.35, 0.95), (0.25, 0.80), (0.45, 0.88), (0.15, 0.82), (0.28, 0.92), (0.50, 0.78)]


    #limpando diretorios de estudo
    print("Limpando diretórios de estudo de resultados anteriores...")
    diretorios = ['./Resultados/Txt/Resultados Parametros/GA/','./Resultados/Txt/Resultados Parametros/PSO/','./Resultados/Txt/Resultados Parametros/DE/','./Resultados/Txt/Resultados Parametros/ACO/','./Resultados/Txt/Resultados Parametros/ABC/','./Resultados/Txt/Resultados Parametros/HS/', './Resultados/Graficos/Graficos Parametros/']
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
                    solucoes_GA, melhor_valor_GA, melhor_individuo_GA, geracao_GA, numero_avaliacoes_GA, solucoes_avaliacoes_GA, tempos_melhor_solucao_GA, melhor_tempo_GA = GA(index, componentes, individuos, peso_max, custo_max, num_geracoes, num_max_avaliacoes, num_tipos_componentes, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema, estudo_parametro, taxa_mutacao=taxa_mutacao, taxa_crossover=taxa_crossover)
                    GA_resultados.append((melhor_valor_GA, solucoes_avaliacoes_GA, taxa_mutacao, taxa_crossover))
                finally:
                    sys.stdout = original_stdout
            GA_resultados_finais.append(GA_resultados)
            print("GA executado com sucesso para população {}.".format(index))

        PSO_resultados_finais = []
        # Executa PSO e captura os resultados
        for j, (c1, c2) in enumerate(PSO_parametros):
            PSO_resultados = []
            print("Executando PSO para população {} - C1: {} - C2: {}".format(index, c1, c2))
            with open(f'./Resultados/Txt/Resultados Parametros/PSO/output{index}-Combinacao{j}.txt', 'w', encoding='utf-8') as f:
                sys.stdout = f
                try:
                    solucoes_PSO, melhor_valor_PSO, melhor_individuo_PSO, geracao_PSO, numero_avaliacoes_PSO, solucoes_avaliacoes_PSO, tempos_melhor_solucao_PSO, melhor_tempo_PSO = PSO(index, componentes, individuos, peso_max, custo_max, num_geracoes, num_max_avaliacoes, num_tipos_componentes, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema, estudo_parametro, c1=c1, c2=c2)
                    PSO_resultados.append((melhor_valor_PSO, solucoes_avaliacoes_PSO, c1, c2))
                finally:
                    sys.stdout = original_stdout
            PSO_resultados_finais.append(PSO_resultados)
            print("PSO executado com sucesso para população {}.".format(index))

        DE_resultados_finais = []
        # Executa DE e captura os resultados
        for j, (passo, cr) in enumerate(DE_parametros):
            DE_resultados = []
            print("Executando DE para população {} - Passo: {} - CR: {}".format(index, passo, cr))
            with open(f'./Resultados/Txt/Resultados Parametros/DE/output{index}-Combinacao{j}.txt', 'w', encoding='utf-8') as f:
                sys.stdout = f
                try:
                    solucoes_DE, melhor_valor_DE, melhor_individuo_DE, geracao_DE, numero_avaliacoes_DE, solucoes_avaliacoes_DE, tempos_melhor_solucao_DE, melhor_tempo_DE = DE(index, componentes, num_tipos_componentes, individuos, peso_max, custo_max, num_geracoes, num_max_avaliacoes, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema, estudo_parametro, passo=passo, cr=cr)
                    DE_resultados.append((melhor_valor_DE, solucoes_avaliacoes_DE, passo, cr))
                finally:
                    sys.stdout = original_stdout
            DE_resultados_finais.append(DE_resultados)
            print("DE executado com sucesso para população {}.".format(index))

        ACO_resultados_finais = []
        # Executa ACO e captura os resultados
        for j, evaporacao in enumerate(ACO_evaporacao):
            ACO_resultados = []
            print("Executando ACO para população {} - Evaporação: {}".format(index, evaporacao))
            with open(f'./Resultados/Txt/Resultados Parametros/ACO/output{index}-Evaporacao{j}.txt', 'w', encoding='utf-8') as f:
                sys.stdout = f
                try:
                    solucoes_ACO, melhor_valor_ACO, melhor_individuo_ACO, geracao_ACO, numero_avaliacoes_ACO, solucoes_avaliacoes_ACO, tempos_melhor_solucao_ACO, melhor_tempo_ACO = AC(index, componentes, individuos, peso_max, custo_max, num_geracoes, num_max_avaliacoes, num_tipos_componentes, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema, estudo_parametro, evaporacao=evaporacao)
                    ACO_resultados.append((melhor_valor_ACO, solucoes_avaliacoes_ACO, evaporacao))
                finally:
                    sys.stdout = original_stdout
            ACO_resultados_finais.append(ACO_resultados)
            print("ACO executado com sucesso para população {}.".format(index))

        HS_resultados_finais = []
        # Executa HS e captura os resultados
        for j, (par, hmcr) in enumerate(HS_parametros):
            HS_resultados = []
            print("Executando HS para população {} - PAR: {} - HMCR: {}".format(index, par, hmcr))
            with open(f'./Resultados/Txt/Resultados Parametros/HS/output{index}-Combinacao{j}.txt', 'w', encoding='utf-8') as f:
                sys.stdout = f
                try:
                    solucoes_HS, melhor_valor_HS, melhor_individuo_HS, geracao_HS, numero_avaliacoes_HS, solucoes_avaliacoes_HS, tempos_melhor_solucao_HS, melhor_tempo_HS = HS(index, componentes, individuos, peso_max, custo_max, num_geracoes, num_max_avaliacoes, num_tipos_componentes, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema, 0, estudo_parametro, hmcr=hmcr, par=par)
                    HS_resultados.append((melhor_valor_HS, solucoes_avaliacoes_HS, par, hmcr))
                finally:
                    sys.stdout = original_stdout
            HS_resultados_finais.append(HS_resultados)
            print("HS executado com sucesso para população {}.".format(index))
        
        analisa_resultados_parametros_multiplos_desconexos(GA_resultados_finais, index, "TM", "TC", "GA", num_max_avaliacoes)
        analisa_resultados_parametros_multiplos_desconexos(PSO_resultados_finais, index, "C1", "C2", "PSO", num_max_avaliacoes)
        analisa_resultados_parametros_multiplos_desconexos(DE_resultados_finais, index, "Passo", "CR", "DE", num_max_avaliacoes)
        analisa_resultados_parametros_multiplos_desconexos(HS_resultados_finais, index, "PAR", "HMCR", "HS", num_max_avaliacoes)
        analisa_resultados_parametros_unico(ACO_resultados_finais, index, "TE", "ACO", "evap", num_max_avaliacoes)

    junta_excels("./Resultados/Txt/Resultados Parametros/GA", "Resultados_Completos_GA.xlsx")
    junta_excels("./Resultados/Txt/Resultados Parametros/PSO", "Resultados_Completos_PSO.xlsx")
    junta_excels("./Resultados/Txt/Resultados Parametros/DE", "Resultados_Completos_DE.xlsx")
    junta_excels("./Resultados/Txt/Resultados Parametros/ACO", "Resultados_Completos_ACO.xlsx")
    junta_excels("./Resultados/Txt/Resultados Parametros/HS", "Resultados_Completos_HS.xlsx")



    