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

    def __init__(self, parent, descricao: str, script: str, testes: list):
        super().__init__(parent)
        self.questao = Questao(descricao, script, testes)
        # Personalização
        self.configure(borderwidth=2, relief='groove')
        # Montagem
        row = 0
        self._montar_primeira_linha(row)
        row += 1
        self._montar_cabecalhos(row)
        row += 1
        self._montar_testes(row)
    
    def _montar_primeira_linha(self, row):
        self.label = ttk.Label(self, text=self.questao.descricao)
        self.label.grid(column=0, row=row, columnspan=2, sticky='w',
            padx=(PADDING_M, 0), pady=(PADDING_M, 0))
        self.botao_testar = ttk.Button(self, text='Testar Questão')
        self.botao_testar.grid(column=2, row=row, sticky='e',
            padx=(0, PADDING_M), pady=(PADDING_M, 0))

    def _montar_cabecalhos(self, row):
        self.label_comando = ttk.Label(self, text='Comando')
        self.label_comando.grid(column=0, row=row,
            padx=(PADDING_M, 0), pady=(PADDING_M, PADDING_P))

    def _montar_testes(self, row):
        for p in self.questao.testes:
            l = ttk.Label(self,
                text=self.comando % (self.questao.script, p.args))
            l.grid(column=0, row=row, sticky='w',
                padx=(PADDING_M, 0), pady=(0, PADDING_P))
            b = ttk.Button(self, text='Testar')
            b.grid(column=2, row=row, sticky='e',
                padx=(0, PADDING_M), pady=(0, PADDING_P))
            row += 1


# FUNÇÕES DE CORREÇÃO DE QUESTÕES

class Questao:
    def __init__(self, descricao: str, script: str, testes: list):
        self.descricao = descricao
        self.script = script
        self.testes = testes

        # Converte os testes em objetos Teste
        self.testes = []
        for args_script, func_expect, args_expect in testes:
            self.testes += [
                Teste(script, args_script, func_expect, args_expect)]

    def corrigir(self):
        # Executa os testes, conta acertos e exibe erros
        global respostas_certas, respostas_erradas
        for t in self.testes:
            erro = t.testar()
            if erro:
                respostas_erradas += 1
                print(f'{self.descricao} errada:')
                print('-', erro)
                return
        print(f'{self.descricao} certa.')
        respostas_certas += 1


class Teste():
    def __init__(self, script: str, args: str, func_expect, args_expect: list):
        self.script = f'{dir}/{script}' if dir != '.' else script
        self.args = args
        self.func_expect = func_expect
        self.args_expect = args_expect

    @property
    def comando(self):
        return f'php {self.script} {self.args}'

    def testar(self):
        processo = os.popen(self.comando)
        resposta = processo.read()
        codigo = processo.close()
        codigo = 0 if codigo == None else codigo

        if codigo == 0: # O script funcionou
            # Verifica a resposta
            ok, erro = self.func_expect(resposta, *self.args_expect)
            if not ok:
                return self._formatar_erro(erro)
            return None
        elif codigo == 256: # File not found
            return self._formatar_erro(f'Arquivo {self.script} não encontrado.')
        else:
            return self._formatar_erro(f"Erro {codigo}: {resposta}")

    def _formatar_erro(self, erro):
        return f'Comando: {self.comando}\n  {erro}'


def testar_igual(resultado: str, esperado: str,
    modificadores = [lambda x: x.strip("\n\r\t ")]) -> tuple[bool, str]:
    for m in modificadores + [lambda x: ignorar_cabecalhos(x)]:
        resultado = m(resultado)
        esperado = m(esperado)
    if resultado != esperado:
        erro = f"Esperava '{esperado}', recebeu '{resultado}'"
        return False, erro
    return True, ''


def ignorar_cabecalhos(resp_http):
    linhas = resp_http.split('\n')
    saida = ''
    for l in linhas:
        add = True
        for c in [
            'Date:',
            'X-',
            'Access-Control-',
            'Connection',
            'Host',
            'Cache-']:
            if l.lower().startswith(c.lower()):
                add = False
        if add:
            saida += l + '\n'
    return saida


# PROGRAMA PRINCIPAL

if __name__ == '__main__':
    App('config.json').mainloop()
