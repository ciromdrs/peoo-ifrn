import json, subprocess, tkinter as tk

from tkinter import ttk


# CORREÇÃO DE QUESTÕES

# Constantes
TIMEOUT = 2

# Classes

class Questao:
    '''Uma questão para corrigir.'''

    def __init__(self, descricao: str, comando: str, script: str, correcoes: list):
        '''Construtor.

        Parâmetros:
        - `descricao` é uma descrição da questão.
        - `comando` é o comando do terminal para executar o script da resposta.
        - `script` é o script da resposta.
        - `correcoes` são os argumentos e verificações da saída do script para corrigir a questão.
        '''
        self.descricao = descricao
        self.script = script
        self.correcoes = correcoes
        # Converte as correcoes em objetos Correcao
        self.correcoes = []
        for args_script, func_expect, args_expect in correcoes:
            self.correcoes += [
                Correcao(comando, script, args_script, func_expect, args_expect)]


class Correcao:
    '''Uma correcao de uma questão.'''

    def __init__(self, comando: str, script: str, args: str, func_expect, args_expect: list):
        '''Construtor.
        
        Parâmetros:
        - `comando` é o comando do terminal para executar o script da resposta.
        - `script` é o script da resposta.
        - `args` são os argumentos do script.
        - `func_expect` é a função que verifica a saída do script.
        - `args_expect` são os argumentos da função que verifica a saída do script.'''
        self.comando = comando
        self.script = script
        self.args = args
        self.func_expect = func_expect
        self.args_expect = args_expect

    @property
    def comando_completo(self) -> str:
        '''Retorna o comando para executar o script, incluindo o comando do terminal, script e argumentos.'''
        c = f'{self.comando} {self.script}'
        if self.args:
            c += f' {self.args}'
        return c

    def corrigir(self) -> tuple[int, str, str]:
        '''Executa a correcao e retorna o código de saída, a saída e o erro.'''
        codigo = -1
        resposta = 'Não executado\n'
        erro = 'Não executado\n'
        try:
            processo = subprocess.run(
                [self.comando, self.script, self.args],
                capture_output=True,
                timeout=TIMEOUT)
            codigo = processo.returncode
            resposta = processo.stdout.decode()
            erro = processo.stderr.decode()
        except subprocess.TimeoutExpired as e:
            codigo = 1
            resposta = e.stdout.decode() if e.stdout else '\n'
            erro = f'Timeout de {TIMEOUT}s expirado.'
        # TODO: Revisar os códigos de erro no Windows e Linux
        if codigo == 0: # O script funcionou
            # Verifica a resposta
            _, erro = eval(self.func_expect)(resposta, self.args_expect)
        elif codigo == 2: # File not found
            erro = f'Arquivo {self.script} não encontrado.'
        return codigo, resposta, erro


# Funções de correcao

def testar_igual(resultado: str, esperado: str) -> tuple[bool, str]:
    '''Verifica se o `resultado` é igual ao `esperado`.'''
    resultado = resultado.strip("\n\r\t ")
    esperado = esperado.strip("\n\r\t ")
    if resultado != esperado:
        erro = f"Esperava '{esperado}', recebeu '{resultado}'"
        return False, erro
    return True, ''


# INTERFACE GRÁFICA

# Constantes
# Paddings tamanho P, M e G
PADDING = 5
LARGURA_WIDGET_QUESTAO = 694

class ScrolledText(tk.Text):
    """ScrolledText do tk.scrolledtext reimplementado com ttk.
    (Copiado de https://github.com/python/cpython/blob/3.12/Lib/tkinter/scrolledtext.py)"""
    def __init__(self, parent=None, **kw):
        self.frame = ttk.Frame(parent)
        self.vbar = ttk.Scrollbar(self.frame)
        self.vbar.pack(side=tk.RIGHT, fill=tk.Y)

        kw.update({'yscrollcommand': self.vbar.set})
        tk.Text.__init__(self, self.frame, **kw)
        self.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.vbar['command'] = self.yview

        # Copy geometry methods of self.frame without overriding Text
        # methods -- hack!
        text_meths = vars(tk.Text).keys()
        methods = vars(tk.Pack).keys() | vars(tk.Grid).keys() | vars(tk.Place).keys()
        methods = methods.difference(text_meths)

        for m in methods:
            if m[0] != '_' and m != 'config' and m != 'configure':
                setattr(self, m, getattr(self.frame, m))

    def __str__(self):
        return str(self.frame)


class ScrolledFrame(ttk.Frame):
    '''Frame com scrollbar.
    *ATENÇÃO:* para colocar widgets dentro deste, passe o `.conteudo` como `parent` do widget filho.'''
    def __init__(self, parent, height: int = 940, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # Na raiz, é necessário um Canvas e a Scrollbar
        canvas = tk.Canvas(self, height=height, width=LARGURA_WIDGET_QUESTAO)
        scrollbar = ttk.Scrollbar(self, command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(anchor='center',side="left", expand=True)
        scrollbar.pack(side="right", fill="y")
        # Dentro do canvas, é necessário um Frame
        conteudo = ttk.Frame(canvas)
        posx = parent.winfo_width() / 2
        canvas.create_window((posx, 0), window=conteudo, anchor="nw")
        # Configura o Canvas para atualizar a scrollbar quando o tamanho muda
        conteudo.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        # Habilita o mouse wheel
        canvas.bind_all("<Button-4>", self._on_mousewheel_up)
        canvas.bind_all("<Button-5>", self._on_mousewheel_down)

        self.canvas = canvas
        self.conteudo = conteudo

    def _on_mousewheel_up(self, event):
        '''Sobe a view do `self.canvas`.'''
        self.canvas.yview_scroll(-1, "units")

    def _on_mousewheel_down(self, event):
        '''Desce a view do `self.canvas`.'''
        self.canvas.yview_scroll(1, "units")


class App(tk.Tk):
    '''Janela principal do corretor.'''

    def __init__(self, caminho_config: str):
        '''Construtor.
        `caminho_config` é o caminho para o arquivo json de configuração da correção.'''
        super().__init__()
        # Lê o arquivo de configuração
        self.config = json.load(open(caminho_config))
        # Atribui o título da janela
        self.title(f"Corretor Automático - {self.config['titulo']}")
        # Configura o tamanho da janela
        self.geometry("1024x600")
        # Montagem da interface
        # O frame principal contém todos os elementos da tela
        # Isso facilita o redimensionamento da janela sem alterar seu conteúdo
        frame_principal = ttk.Frame(self)
        frame_principal.pack(expand=True, fill=tk.BOTH)
        frame_topo = ttk.Frame(frame_principal, borderwidth=2, relief=tk.GROOVE)
        frame_topo.pack(fill=tk.BOTH, pady=(0,PADDING))
        botao_corrigir_todas = ttk.Button(frame_topo, text='Corrigir Todas',
            command=self._corrigir_todas)
        botao_corrigir_todas.pack(padx=PADDING*4, pady=PADDING*4)
        self.frame_questoes = ScrolledFrame(frame_principal)
        self.frame_questoes.pack(fill=tk.BOTH)
        self._montar_questoes()
    
    def _montar_questoes(self):
        '''Monta os widgets das questões'''
        self.widgets_questoes: list[QuestaoWidget] = []
        for dados in self.config['questoes']:
            desc = dados['descricao']
            comando = dados['comando']
            script = dados['script']
            correcoes = dados['correcoes']
            questao = Questao(descricao=desc, comando=comando, script=script,
                correcoes=correcoes)
            qw = QuestaoWidget(self.frame_questoes.conteudo, questao)
            qw.pack(pady=(0,PADDING))
            self.widgets_questoes += [qw]

    def _corrigir_todas(self):
        '''Testa todas as questões.'''
        for qw in self.widgets_questoes:
            qw._corrigir_questao()
        

class QuestaoWidget(ttk.Frame):
    '''Widget de Questões.'''

    def __init__(self, parent, questao: Questao):
        '''Construtor.
        Parâmetros:
        - `parent` é o widget pai que conterá este.
        - `questao` é a questão correspondente.'''
        super().__init__(parent)
        self.questao: Questao = questao
        self.widgets_correcoes: list[CorrecaoWidget] = []
        # Personalização
        self.configure(borderwidth=2, relief=tk.GROOVE)
        # Montagem
        row = 0
        self._montar_primeira_linha(row)
        row += 1
        self._montar_correcoes()
    
    def _montar_primeira_linha(self, row):
        '''Monta a primeira linha deste widget, que contém a descrição da questão e o botão para corrigir.'''
        self.label = ttk.Label(self, text=self.questao.descricao)
        self.label.grid(column=0, row=row, columnspan=2, sticky='w',
            padx=(PADDING*2, 0), pady=(PADDING*2, 0))
        self.botao_corrigir = ttk.Button(self, text='Corrigir Questão',
            command=self._corrigir_questao)
        self.botao_corrigir.grid(row=row, sticky='e', 
            padx=(0, PADDING*2), pady=PADDING*2)

    def _montar_correcoes(self):
        '''Monta o widget de cada correção.'''
        for p in self.questao.correcoes:
            tw = CorrecaoWidget(self, p)
            tw.grid(padx=PADDING*2, pady=(0, PADDING))
            self.widgets_correcoes += [tw]
    
    def _corrigir_questao(self):
        '''Executa todas as correcoes da questão.'''
        for tw in self.widgets_correcoes:
            tw._corrigir()


class CorrecaoWidget(ttk.Frame):
    '''Widget da Correcao.'''

    def __init__(self, parent, correcao: Correcao):
        '''Construtor.
        Parâmetros:
        - `parent` é o widget pai que conterá este.
        - `correcao` é a correcao correspondente.'''
        super().__init__(parent)
        self.correcao: Correcao = correcao
        # Montagem
        # A correção é montada como grid. A variável `row` serve para controlar as linhas.
        row = 0
        self.label_comando = ttk.Label(self, text=f'Comando: {correcao.comando_completo}')
        self.label_comando.grid(column=0, row=row, sticky='w',
            padx=(PADDING*2, 0), pady=(0, PADDING))
        self.botao_corrigir = ttk.Button(self, text='Corrigir', command=self._corrigir)
        self.botao_corrigir.grid(column=1, row=row, sticky='e',
            pady=(0, PADDING))
        row += 1
        label_resultado = ttk.Label(self, text=f'Resultado:')
        label_resultado.grid(column=0, row=row, sticky='w',
            padx=(PADDING*2, 0), pady=(0, PADDING))
        row += 1
        self.text_resultado = ScrolledText(self, wrap=tk.WORD, 
                                    width=80, height=8, state=tk.DISABLED)
        self.text_resultado.grid(column=0, row=row, sticky='w', columnspan=2,
            padx=(PADDING*2, 0), pady=(0, PADDING))

    def _corrigir(self):
        '''Executa a correcao e atualiza a interface com o resultado.'''
        text = self.text_resultado
        # Habilita a caixa de texto para edição
        text.configure(state=tk.NORMAL)
        # Limpa o texto
        text.delete(1.0, 'end')
        codigo, saida, erro = self.correcao.corrigir()
        if saida == '': saida = '\n'
        # Preenche com o resultado da correcao
        text.insert('end', f'Código: {codigo}')
        text.insert('end', f'\nSaída: {saida}')
        if erro:
            text.insert('end', f'Erro: {erro}')
        # Desabilita a edição
        text.configure(state=tk.DISABLED)
        # Atualiza a interface
        root = self.winfo_toplevel()
        root.update()
        root.update_idletasks()

# PROGRAMA PRINCIPAL

if __name__ == '__main__':
    app = App('config.json')
    style = ttk.Style(app)
    temas = style.theme_names()
    style.theme_use(temas[0])
    app.mainloop()


