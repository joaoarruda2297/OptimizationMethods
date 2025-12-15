import matplotlib.pyplot as plt
import sys
import os
from utils import truncate
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class GeradorGraficos:
    def __init__(self, caminho_salvamento, cor=None):
        self.caminho_salvamento = caminho_salvamento
        self.cor = cor
        self.cores = ["#0095ff", '#ff7f0e', "#00ff00", '#d62728', 
                "#8400ff", "#346f39", "#6a365a", "#ff00f7",
                '#bcbd22', "#00e5ff"]

    def gera_grafico(self, nome_arquivo, range_X, values, valor_final, geracao, title, xlabel, ylabel, texto_adicional=None, show_plot=False):
        show_plot = False
        plt.plot(range_X, values, color=self.cor)
        # Configurações do gráfico
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(title)
        plt.grid(True)
        # Texto adicional no gráfico
        texto = ("Valor final: " + str(valor_final) + 
                "\nAlcançado na geração: " + str(geracao) + 
                (("\n" + texto_adicional) if texto_adicional != None else ""))
        if( texto_adicional != None ):
            plt.figtext(0.8, 0.05, texto, wrap=True, horizontalalignment='center', fontsize=8)
            plt.subplots_adjust(bottom=0.2)
        else:
            plt.figtext(0.87, 0.029, texto, wrap=True, horizontalalignment='center', fontsize=8)
            plt.tight_layout()
        plt.savefig(self.caminho_salvamento + nome_arquivo)
        if show_plot:
            plt.show()
        else:
            plt.close()

    def gera_grafico_comparativo_truncado(self, nome_arquivo, dicionario_metodos, title, xlabel, ylabel, valor_truncamento, xlim=None, show_plot=True):
        dicionario_metodos_filtrado = {}
        for metodo, dados in dicionario_metodos.items():
            # Filtrar pontos até 1 segundo
            pontos_filtrados = [(t, s) for t, s in zip(dados['x'], dados['y']) if t <= valor_truncamento]
            if pontos_filtrados:
                if(dados['x'][-1] != valor_truncamento):
                    pontos_filtrados.append((valor_truncamento, pontos_filtrados[-1][1]))
                aval, sols = zip(*pontos_filtrados)
                # Criar nova entrada no dicionário filtrado
                novo_label = f'{metodo} ({truncate(sols[-1], 5)})'
                dicionario_metodos_filtrado[metodo] = {
                    'x': aval,
                    'y': sols,
                    'color': dados['color'],
                    'label': novo_label
                }
        self.gera_grafico_comparativo(nome_arquivo, dicionario_metodos_filtrado, title, xlabel, ylabel, xlim, show_plot)

    def gera_grafico_comparativo(self, nome_arquivo, dicionario_metodos, title, xlabel, ylabel, xlim=None, show_plot=True):
        show_plot = False
        fig, ax = plt.subplots(figsize=(12, 6))
        fig.subplots_adjust(right=0.55)  # reserva espaço à direita para a legenda
        for metodo, data in dicionario_metodos.items():
            ax.plot(data['x'], data['y'], label=data['label'], color=data['color'])
        # Configurações do gráfico
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.grid(True)
        if xlim is not None:
            ax.set_xlim(xlim[0], xlim[1])
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        fig.savefig(self.caminho_salvamento + nome_arquivo)
        if show_plot:
            plt.show()
        else:
            plt.close(fig)

    def gera_grafico_comparativo_parametros(self, nome_arquivo, dicionario_parametros, title, xlabel, ylabel, xlim=None, show_plot=True):
        show_plot = False
        fig, ax = plt.subplots(figsize=(12, 6))
        fig.subplots_adjust(right=0.55)  # reserva espaço à direita para a legenda
        # Verifica se há mais parâmetros que cores
        if len(dicionario_parametros) > len(self.cores):
            print(f"Aviso: Mais parâmetros ({len(dicionario_parametros)}) que cores disponíveis ({len(self.cores)})")

        for i, (parametro, data) in enumerate(dicionario_parametros.items()):
            ax.plot(data['x'], data['y'], label=data['label'], color=self.cores[i % len(self.cores)])
        # Configurações do gráfico
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.grid(True)
        if xlim is not None:
            ax.set_xlim(xlim[0], xlim[1])
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        fig.savefig(self.caminho_salvamento + nome_arquivo)
        if show_plot:
            plt.show()
        else:
            plt.close(fig)
    
    def gera_grafico_comparativo_parametros_truncado(self, nome_arquivo, dicionario_parametros, title, xlabel, ylabel, valor_truncamento, xlim=None, show_plot=True):
        dicionario_parametros_filtrado = {}
        for parametro, dados in dicionario_parametros.items():
            # Filtrar pontos até valor_truncamento
            pontos_filtrados = [(t, s) for t, s in zip(dados['x'], dados['y']) if t <= valor_truncamento]
            if pontos_filtrados:
                if(dados['x'][-1] != valor_truncamento):
                    pontos_filtrados.append((valor_truncamento, pontos_filtrados[-1][1]))
                aval, sols = zip(*pontos_filtrados)
                # Criar nova entrada no dicionário filtrado
                novo_label = f'{parametro} ({truncate(sols[-1], 5)})'
                dicionario_parametros_filtrado[parametro] = {
                    'x': aval,
                    'y': sols,
                    'label': novo_label
                }
        self.gera_grafico_comparativo_parametros(nome_arquivo, dicionario_parametros_filtrado, title, xlabel, ylabel, xlim, show_plot)