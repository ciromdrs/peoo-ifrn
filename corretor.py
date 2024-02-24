import json

from tkinter import Tk
from tkinter import ttk

# Classes e funções auxiliares
class App(Tk):
    def __init__(self, caminho_config, *args, **kwargs):
        super().__init__()

        self.config = json.load(open(caminho_config))

        self.title(self.config['titulo'])
        # TODO: tornar tela scrollable
        self.geometry("1024x600")
        row = 0
        botao_testar_todas = ttk.Button(self, text='Testar Todas')
        botao_testar_todas.pack(anchor='e', padx=20, pady=20)
        row += 1
        frame_questoes = ttk.Frame(self)
        frame_questoes.pack(padx=20, pady=20)
        for dados in self.config['questoes']:
            desc = dados['descricao']
            script = dados['script']
            testes = dados['testes']
            qw = QuestaoWidget(frame_questoes, descricao=desc, script=script, testes=testes)
            qw.pack(pady=(10,0))
        

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
        self.label.grid(column=0, row=row, columnspan=2, sticky='w')
        self.botao_testar = ttk.Button(self, text='Testar Questão')
        self.botao_testar.grid(column=2, row=row)

    def _montar_cabecalhos(self, row):
        self.label_comando = ttk.Label(self, text='Comando')
        self.label_comando.grid(column=0, row=row)

    def _montar_testes(self, row):
        for p in self.testes:
            ttk.Label(self, text=self.comando % (self.script, p)).grid(column=0, row=row)
            ttk.Button(self, text='Testar').grid(column=2, row=row)
            row += 1


# Programa principal

if __name__ == '__main__':
    App('config.json').mainloop()
