import numpy as np

class GeradorComponentes:
    def __init__(self, num_tipos_componentes, confiabilidade_maxima, confiabilidade_minima,lim_inf_custo,lim_sup_custo,lim_inf_peso,lim_sup_peso):
        self.num_tipos_componentes = num_tipos_componentes
        self.confiabilidade_maxima = confiabilidade_maxima
        self.confiabilidade_minima = confiabilidade_minima
        self.lim_inf_custo = lim_inf_custo
        self.lim_sup_custo = lim_sup_custo
        self.lim_inf_peso = lim_inf_peso
        self.lim_sup_peso = lim_sup_peso

    def cria_componentes(self):
        linha1 = np.round(np.random.uniform(self.confiabilidade_minima, self.confiabilidade_maxima, self.num_tipos_componentes), 8)  # confiabilidade com max 8 casas decimais
        linha2 = np.round(np.random.uniform(self.lim_inf_custo, self.lim_sup_custo + 0.1, self.num_tipos_componentes), 2)#custo com duas casas decimais
        linha3 = np.round(np.random.uniform(self.lim_inf_peso, self.lim_sup_peso + 0.1, self.num_tipos_componentes), 2)#peso com duas casas decimais
        
        # Combina as linhas em uma matriz
        matriz = np.vstack([linha1, linha2, linha3])
        return matriz

def main(num_tipos_componentes, confiabilidade_maxima, confiabilidade_minima,lim_inf_custo,lim_sup_custo,lim_inf_peso,lim_sup_peso):
    generator = GeradorComponentes(num_tipos_componentes, confiabilidade_maxima, confiabilidade_minima, lim_inf_custo,lim_sup_custo,lim_inf_peso,lim_sup_peso)
    componentes = generator.cria_componentes()
    #ordena os componentes por uma chave = confiabilidade - (custo - lim_inf_custo) - (peso - lim_inf_peso)
    componentes = componentes[:, np.argsort(componentes[0] - (componentes[1] - lim_inf_custo) - (componentes[2] - lim_inf_peso))]
    return componentes