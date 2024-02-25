import json, subprocess, tkinter as tk

from tkinter import ttk, scrolledtext


# FUNÇÕES DE CORREÇÃO DE QUESTÕES

class Questao:
    def __init__(self, descricao: str, comando: str, script: str, testes: list):
        self.descricao = descricao
        self.script = script
        self.testes = testes

        # Converte os testes em objetos Teste
        self.testes = []
        for args_script, func_expect, args_expect in testes:
            self.testes += [
                Teste(comando, script, args_script, func_expect, args_expect)]

    def corrigir(self):
        # Executa os testes, conta acertos e exibe erros
        for t in self.testes:
            codigo, saida, erro = t.testar()
            if erro:
                return erro
        return


class Teste():
    def __init__(self, comando: str, script: str, args: str, func_expect, args_expect: list):
        self.comando = comando
        self.script = script
        self.args = args
        self.func_expect = func_expect
        self.args_expect = args_expect

    @property
    def comando_completo(self):
        c = f'{self.comando} {self.script}'
        if self.args:
            c += f' {self.args}'
        return c

    def testar(self) -> tuple[int, str, str]:
        processo = subprocess.run([self.comando, self.script, self.args], capture_output=True)
        codigo = processo.returncode
        resposta = processo.stdout.decode()
        erro = processo.stderr.decode()
        # TODO: Revisar os códigos de erro no Windows e Linux
        if codigo == 0: # O script funcionou
            # Verifica a resposta
            _, erro = eval(self.func_expect)(resposta, self.args_expect)
        elif codigo == 256: # File not found # 512 também é no Linux
            erro = f'Arquivo {self.script} não encontrado.'
        else:
            erro = f"Erro {codigo}:\n{erro}"
        return codigo, resposta, erro


# Funções de teste

def testar_igual(resultado: str, esperado: str,
    modificadores = [lambda x: x.strip("\n\r\t ")]) -> tuple[bool, str]:
    for m in modificadores:
        resultado = m(resultado)
        esperado = m(esperado)
    if resultado != esperado:
        erro = f"Esperava '{esperado}', recebeu '{resultado}'"
        return False, erro
    return True, ''


# INTERFACE GRÁFICA

# Constantes
# Paddings tamanho P, M e G
PADDING_P = 5
PADDING_M = 10
PADDING_G = 20

class App(tk.Tk):
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
        self.widgets_questoes: list[QuestaoWidget] = []
        for dados in self.config['questoes']:
            desc = dados['descricao']
            comando = dados['comando']
            script = dados['script']
            testes = dados['testes']
            qw = QuestaoWidget(frame_questoes, descricao=desc,
                comando=comando, script=script, testes=testes)
            qw.pack(pady=PADDING_M)
            self.widgets_questoes += [qw]
        

class QuestaoWidget(ttk.Frame):
    comando = 'python %s %s' # Ex.: python q1.py 1 2 3

    def __init__(self, parent, descricao: str, comando: str, script: str, testes: list):
        super().__init__(parent)
        self.questao = Questao(descricao, comando, script, testes)
        self.widgets_testes = []
        # Personalização
        self.configure(borderwidth=2, relief=tk.GROOVE)
        # Montagem
        row = 0
        self._montar_primeira_linha(row)
        row += 1
        self._montar_testes()
    
    def _montar_primeira_linha(self, row):
        self.label = ttk.Label(self, text=self.questao.descricao)
        self.label.grid(column=0, row=row, columnspan=2, sticky='w',
            padx=(PADDING_M, 0), pady=(PADDING_M, 0))
        self.botao_testar = ttk.Button(self, text='Testar Questão')
        self.botao_testar.grid(row=row, sticky='e', 
            padx=(0, PADDING_M), pady=PADDING_M)

    def _montar_testes(self):
        for p in self.questao.testes:
            tw = TesteWidget(self, p)
            tw.grid(padx=(0, PADDING_M), pady=(0, PADDING_P))
            self.widgets_testes += [tw]


class TesteWidget(ttk.Frame):
    def __init__(self, parent, teste: Teste):
        super().__init__(parent)
        self.teste = teste
        # Montagem
        row = 0
        self.label_comando = ttk.Label(self, text=f'Comando: {teste.comando_completo}')
        self.label_comando.grid(column=0, row=row, sticky='w',
            padx=(PADDING_M, 0), pady=(0, PADDING_P))
        self.botao_testar = ttk.Button(self, text='Testar', command=self._testar)
        self.botao_testar.grid(column=1, row=row, sticky='e',
            pady=(0, PADDING_P))
        row += 1
        label_resultado = ttk.Label(self, text=f'Resultado:')
        label_resultado.grid(column=0, row=row, sticky='w',
            padx=(PADDING_M, 0), pady=(0, PADDING_P))
        row += 1
        self.text_resultado = scrolledtext.ScrolledText(self, wrap=tk.WORD, 
                                    width=80, height=8, state=tk.DISABLED)
        self.text_resultado.grid(column=0, row=row, sticky='w', columnspan=2,
            padx=(PADDING_M, 0), pady=(0, PADDING_P))

    def _testar(self):
        text = self.text_resultado
        text.configure(state=tk.NORMAL)
        text.delete(1.0, 'end')
        codigo, saida, erro = self.teste.testar()
        text.insert('end', f'Código: {codigo}')
        text.insert('end', f'\nSaída: {saida}')
        if erro:
            text.insert('end', f'Erro: {erro}')
        text.configure(state=tk.DISABLED)

# PROGRAMA PRINCIPAL

if __name__ == '__main__':
    App('config.json').mainloop()
