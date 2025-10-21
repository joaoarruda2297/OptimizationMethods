import os
from .GeradorComponentes import main as GeradorComponentes
from .GeradorIndividuos import main as GeradorIndividuos

import pandas as pd

def exporta_individuos_para_excel(individuos, caminho_excel):
    data = []
    for ind in individuos:
        row = {
            "solucao_tipos": ind.solucao[0].tolist(),
            "solucao_quantidades": ind.solucao[1].tolist(),
            "funcao_objetivo": float(ind.valor_funcao_objetivo),
            "confiabilidade_total": float(ind.confiabilidade_total),
            "peso": float(ind.peso),
            "custo": float(ind.custo),
        }
        data.append(row)
    df = pd.DataFrame(data)
    df.to_excel(caminho_excel, index=False)

def exporta_componentes_para_excel(componentes, caminho_excel):
    data = {
        "confiabilidade": [c.confiabilidade for c in componentes],
        "custo": [c.custo for c in componentes],
        "peso": [c.peso for c in componentes],
    }
    df = pd.DataFrame(data)
    df.to_excel(caminho_excel, index=False)

def main(num_populacoes,confiabilidade_maxima, confiabilidade_minima, num_tipos_componentes, num_individuos, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema, peso_max, custo_max, lim_inf_custo, lim_sup_custo, lim_inf_peso, lim_sup_peso):
    componentes = GeradorComponentes(num_tipos_componentes, confiabilidade_maxima, confiabilidade_minima,  lim_inf_custo, lim_sup_custo, lim_inf_peso, lim_sup_peso)
    populacoes = GeradorIndividuos(num_populacoes, num_tipos_componentes, num_individuos, num_variaveis, num_max_componentes_subsistema, num_min_componentes_subsistema, peso_max, custo_max, componentes)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    excel_dir = os.path.join(base_dir, 'Excel')
    os.makedirs(excel_dir, exist_ok=True)

    exporta_componentes_para_excel(componentes, excel_dir + "/componentes.xlsx")
    for i, individuos in enumerate(populacoes):
        exporta_individuos_para_excel(individuos, excel_dir + f"/individuos_{i+1}.xlsx")

    return componentes, populacoes
