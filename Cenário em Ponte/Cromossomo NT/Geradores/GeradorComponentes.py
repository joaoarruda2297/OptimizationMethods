from contextlib import redirect_stdout
import os
import numpy as np

class Componente:
    def __init__(self, confiabilidade, custo, peso):
        self.confiabilidade = confiabilidade
        self.custo = custo
        self.peso = peso

    def __str__(self):
        return (
            "{\n"
            f"  \"confiabilidade\": {self.confiabilidade}\n"
            f"  \"peso\": {self.peso},\n"
            f"  \"custo\": {self.custo}\n"
            "}"
        )

class GeradorComponentes:
    def __init__(self, num_tipos_componentes, confiabilidade_maxima, confiabilidade_minima,lim_inf_custo,lim_sup_custo,lim_inf_peso,lim_sup_peso):
        self.num_tipos_componentes = num_tipos_componentes
        self.confiabilidade_maxima = confiabilidade_maxima
        self.confiabilidade_minima = confiabilidade_minima
        self.lim_inf_custo = lim_inf_custo
        self.lim_sup_custo = lim_sup_custo
        self.lim_inf_peso = lim_inf_peso
        self.lim_sup_peso = lim_sup_peso
    
    def cria_componentes_matriz(self):
        linha1 = np.round(np.random.uniform(self.confiabilidade_minima, self.confiabilidade_maxima, self.num_tipos_componentes), 8)  # confiabilidade com max 8 casas decimais
        linha2 = np.round(np.random.uniform(self.lim_inf_custo, self.lim_sup_custo + 0.1, self.num_tipos_componentes), 2)#custo com duas casas decimais
        linha3 = np.round(np.random.uniform(self.lim_inf_peso, self.lim_sup_peso + 0.1, self.num_tipos_componentes), 2)#peso com duas casas decimais
        
        # Combina as linhas em uma matriz
        matriz = np.vstack([linha1, linha2, linha3])
        return matriz
    
    def cria_componentes_estruturado(self):
        componentes = []
        for _ in range(self.num_tipos_componentes):
            confiabilidade = round(np.random.uniform(self.confiabilidade_minima, self.confiabilidade_maxima), 8)  # confiabilidade com max 8 casas decimais
            custo = round(np.random.uniform(self.lim_inf_custo, self.lim_sup_custo + 0.1), 2)  # custo com duas casas decimais
            peso = round(np.random.uniform(self.lim_inf_peso, self.lim_sup_peso + 0.1), 2)  # peso com duas casas decimais
            componente = Componente(confiabilidade, custo, peso)
            componentes.append(componente)
        return componentes

def main(num_tipos_componentes, confiabilidade_maxima, confiabilidade_minima,lim_inf_custo,lim_sup_custo,lim_inf_peso,lim_sup_peso):
    generator = GeradorComponentes(num_tipos_componentes, confiabilidade_maxima, confiabilidade_minima, lim_inf_custo,lim_sup_custo,lim_inf_peso,lim_sup_peso)
    componentes = generator.cria_componentes_estruturado()
    #ordena os componentes por confiabilidade
    componentes = sorted(componentes, key=lambda x: x.confiabilidade, reverse=True)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    txt_dir = os.path.join(base_dir, 'Txt')
    os.makedirs(txt_dir, exist_ok=True)

    with open(os.path.join(txt_dir, 'components.txt'), 'w') as f:
        print("COMPONENTES GERADOS:\n", file=f)
        for i, componente in enumerate(componentes):
            print(f"Componente {i}: {componente}", file=f)

    return componentes