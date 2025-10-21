import matplotlib.pyplot as plt
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class GeradorGraficos:
    def __init__(self, caminho_salvamento, cor):
        self.caminho_salvamento = caminho_salvamento
        self.cor = cor

    def gera_grafico(self, nome_arquivo, range_X, values, valor_final, geracao, title, xlabel, ylabel, texto_adicional=None, show_plot=True):
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