import json

from tkinter import Tk, StringVar, Canvas
from tkinter import ttk

# Classes e funções auxiliares
class App(Tk):
    def __init__(self, caminho_config, *args, **kwargs):
        super().__init__()

        self.config = json.load(open(caminho_config))

        # TODO: tornar tela scrollable
        self.title(self.config['titulo'])
        row = 0
        botao_testar_todas = ttk.Button(self, text='Testar Todas')
        botao_testar_todas.pack(anchor='e', padx=20, pady=20)
        row += 1
        frame_questoes = ttk.Frame(self)
        frame_questoes.pack(padx=20, pady=20)
        for dados in self.config['questoes']:
            desc = dados['descricao']
            script = dados['script']
            params = dados['testes']
            qw = QuestaoWidget(frame_questoes, descricao=desc, script=script, parametros=params)
            qw.pack()
        

class QuestaoWidget(ttk.Frame):
    comando = 'python %s %s' # Ex.: python q1.py 1 2 3

    def __init__(self, parent=None, descricao='QuestaoWidget', script: str = 'q.py', parametros=[]):
        super().__init__(parent)
        self.script = script
        self.descricao = descricao
        self.parametros = parametros
        # Inicia a montagem da interface
        row = 0
        self._montar_primeira_linha(row)
        row += 1
        self._montar_cabecalhos(row)
        row += 1
        self._montar_teste_personalizado(row)
        row += 1
        self._montar_testes(row)
    
    def _gerar_comando(self, *args):
        '''Sincroniza o label dos parâmetros do teste personalizado com a entry.'''
        novo = self.custom_params.get()
        if novo:
            self.label_custom_params.configure(text = self.comando % (self.script, novo))
    
    def _montar_primeira_linha(self, row):
        self.label = ttk.Label(self, text=self.descricao)
        self.label.grid(column=0, row=row, columnspan=2, sticky='w')
        self.botao_testar = ttk.Button(self, text='Testar Questão')
        self.botao_testar.grid(column=2, row=row)

    def _montar_cabecalhos(self, row):
        self.label_parametros = ttk.Label(self, text='Parâmetros')
        self.label_parametros.grid(column=0, row=row)
        self.label_comando = ttk.Label(self, text='Comando')
        self.label_comando.grid(column=1, row=row)
    
    def _montar_teste_personalizado(self, row):
        self.custom_params = StringVar()
        self.custom_params.trace_add('write', self._gerar_comando)
        ttk.Entry(self, textvariable=self.custom_params).grid(column=0, row=row)
        self.label_custom_params = ttk.Label(self)
        self.label_custom_params.grid(column=1, row=row)
        ttk.Button(self, text='Testar').grid(column=2, row=row)

    def _montar_testes(self, row):
        for p in self.parametros:
            ttk.Entry(self, text=p, state='disabled').grid(column=0, row=row)
            ttk.Label(self, text=self.comando % (self.script, p)).grid(column=1, row=row)
            ttk.Button(self, text='Testar').grid(column=2, row=row)
            row += 1


# Programa principal

if __name__ == '__main__':
    App('config.json').mainloop()
