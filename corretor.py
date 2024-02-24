import json, os

from tkinter import Tk
from tkinter import ttk


# CONSTANTES
# Paddings tamanho P, M e G
PADDING_P = 5
PADDING_M = 10
PADDING_G = 20

# INTERFACE GRÁFICA

class App(Tk):
    def __init__(self, caminho_config, *args, **kwargs):
        super().__init__()

        self.config = json.load(open(caminho_config))

        self.title(self.config['titulo'])
        # TODO: tornar tela scrollable
        self.geometry("1024x600")
        row = 0
        botao_testar_todas = ttk.Button(self, text='Testar Todas')
        botao_testar_todas.pack(anchor='e', padx=PADDING_G, pady=PADDING_G)
        row += 1
        frame_questoes = ttk.Frame(self)
        frame_questoes.pack(padx=PADDING_G, pady=PADDING_G)
        for dados in self.config['questoes']:
            desc = dados['descricao']
            script = dados['script']
            testes = dados['testes']
            qw = QuestaoWidget(frame_questoes, descricao=desc, script=script, testes=testes)
            qw.pack(pady=(PADDING_M,0))
        

class QuestaoWidget(ttk.Frame):
    comando = 'python %s %s' # Ex.: python q1.py 1 2 3

    def __init__(self, parent=None, descricao='QuestaoWidget', script: str = 'q.py', testes=[]):
        super().__init__(parent)
        self.script = script
        self.descricao = descricao
        self.testes = testes
        # Personalização
        self.configure(borderwidth=2, relief='groove')
        # Montagem
        row = 0
        self._montar_primeira_linha(row)
        row += 1
        self._montar_cabecalhos(row)
        row += 1
        # self._montar_executar(row)
        row += 1
        self._montar_testes(row)
    
    def _montar_primeira_linha(self, row):
        self.label = ttk.Label(self, text=self.descricao)
        self.label.grid(column=0, row=row, columnspan=2, sticky='w', padx=(PADDING_M, 0), pady=(PADDING_M, 0))
        self.botao_testar = ttk.Button(self, text='Testar Questão')
        self.botao_testar.grid(column=2, row=row, sticky='e', padx=(0, PADDING_M), pady=(PADDING_M, 0))

    def _montar_cabecalhos(self, row):
        self.label_comando = ttk.Label(self, text='Comando')
        self.label_comando.grid(column=0, row=row, padx=(PADDING_M, 0), pady=(PADDING_M, PADDING_P))

    def _montar_testes(self, row):
        for p in self.testes:
            l = ttk.Label(self, text=self.comando % (self.script, p))
            l.grid(column=0, row=row, sticky='w', padx=(PADDING_M, 0), pady=(0, PADDING_P))
            b = ttk.Button(self, text='Testar')
            b.grid(column=2, row=row, sticky='e', padx=(0, PADDING_M), pady=(0, PADDING_P))
            row += 1


# Programa principal

if __name__ == '__main__':
    App('config.json').mainloop()
