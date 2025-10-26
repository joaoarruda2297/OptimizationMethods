import matplotlib.pyplot as plt
import sys
import os
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

    def gera_grafico_comparativo(self, nome_arquivo, dicionario_metodos, title, xlabel, ylabel, xlim=None, show_plot=True):
        show_plot = False
        for metodo, data in dicionario_metodos.items():
            plt.plot(data['x'], data['y'], label=data['label'], color=data['color'])
        # Configurações do gráfico
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(title)
        plt.legend()
        plt.grid(True)
        if xlim is not None:
            plt.xlim(xlim[0], xlim[1])
        plt.savefig(self.caminho_salvamento + nome_arquivo)
        if show_plot:
            plt.show()
        else:
            plt.close()

    def gera_grafico_comparativo_parametros(self, nome_arquivo, dicionario_parametros, title, xlabel, ylabel, xlim=None, show_plot=True):
        show_plot = False
        # Verifica se há mais parâmetros que cores
        if len(dicionario_parametros) > len(self.cores):
            print(f"Aviso: Mais parâmetros ({len(dicionario_parametros)}) que cores disponíveis ({len(self.cores)})")

        for i, (parametro, data) in enumerate(dicionario_parametros.items()):
            plt.plot(data['x'], data['y'], label=data['label'], color=self.cores[i % len(self.cores)])
        # Configurações do gráfico
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(title)
        plt.legend()
        plt.grid(True)
        if xlim is not None:
            plt.xlim(xlim[0], xlim[1])
        plt.savefig(self.caminho_salvamento + nome_arquivo)
        if show_plot:
            plt.show()
        else:
            plt.close()