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
        # Converte as correções em objetos Correcao
        self.correcoes = []
        for args_script, func_expect, args_expect in correcoes:
            self.correcoes += [
                Correcao(comando, script, args_script, func_expect, args_expect)]


class Correcao:
    '''Uma correcao de uma questão.'''

    def __init__(self, comando: str, script: str, input_: str, func_expect, args_expect: list):
        '''Construtor.
        
        Parâmetros:
        - `comando` é o comando do terminal para executar o script da resposta.
        - `script` é o script da resposta.
        - `input_` é a entrada do teclado. O atributo `args` é calculado a partir dela, substituindo \n por espaços.
        - `func_expect` é a função que verifica a saída do script.
        - `args_expect` são os argumentos da função que verifica a saída do script.'''
        self.comando = comando
        self.script = script
        self.input = input_.encode()
        self.args = input_.replace('\n', ' ')
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
                input=self.input,
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

def testar_regex(resultado: str, regex: str) -> tuple[bool, str]:
    '''Verifica se `regex` casa em `resultado`.'''
    import re
    resultado = resultado.strip("\n\r\t ")
    padrao = re.compile(regex)
    if padrao.search(resultado) is None:
        erro = f'Esperava encontrar o padrão "{regex}".'
        return False, erro
    return True, ''


# INTERFACE GRÁFICA

# Constantes
# Paddings tamanho P, M e G
PADDING = 5
LARGURA_WIDGET_QUESTAO = 680

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
    *ATENÇÃO:* para colocar widgets dentro deste, passe o `.conteudo` deste como `parent` do widget filho.'''
    def __init__(self, parent, width, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        # Na raiz, é necessário um Canvas
        canvas = tk.Canvas(self, width=width)
        scrollbar = ttk.Scrollbar(self, command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(anchor='center', side="left", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Dentro do canvas, é necessário um Frame
        conteudo = ttk.Frame(canvas)
        posx = parent.winfo_width() / 2
        canvas.create_window((posx, 0), width=width, window=conteudo, anchor="nw")
        # Configura o Canvas para atualizar a scrollbar quando o tamanho muda
        conteudo.bind("<Configure>", self._on_resize)
        # Habilita o mouse wheel
        canvas.bind_all("<Button-4>", self._on_mousewheel_up)
        canvas.bind_all("<Button-5>", self._on_mousewheel_down)
        # Guarda as referências no self
        self.canvas = canvas
        self.conteudo = conteudo
        self.parent = parent

    def _on_mousewheel_up(self, event):
        '''Sobe a view do `canvas`.'''
        self.canvas.yview_scroll(-1, "units")

    def _on_mousewheel_down(self, event):
        '''Desce a view do `canvas`.'''
        self.canvas.yview_scroll(1, "units")
    
    def _on_resize(self, event):
        '''Redimensiona o `canvas`.'''
        # Atualiza os widgets para pegar o tamanho atual
        self.conteudo.update()
        # bbox é uma tupla (x, y, largura, altura) que engloba todo o conteúdo do canvas
        bbox = self.canvas.bbox('all')
        # Existe algum problema que ela pega além do tamanho do que é visível,
        # então consertamos isso copiando os demais valores e recalculando a altura
        altura = self.conteudo.winfo_height()
        nova_bbox = *bbox[:3], altura
        self.canvas.configure(
            scrollregion = nova_bbox,
            height = altura,
        )


class Corretor(tk.Tk):
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
        botao_corrigir_todas = ttk.Button(frame_topo, text='▶️ Corrigir Todas',
            command=self._corrigir_todas)
        botao_corrigir_todas.pack(padx=PADDING*4, pady=PADDING*4)
        self.frame_questoes = ScrolledFrame(frame_principal, width=LARGURA_WIDGET_QUESTAO)
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
    contador_corretas: int = 0

    def __init__(self, parent, questao: Questao):
        '''Construtor.
        Parâmetros:
        - `parent` é o widget pai que conterá este.
        - `questao` é a questão correspondente.'''
        super().__init__(parent)
        self.frame_questoes: ScrolledFrame = parent
        self.questao: Questao = questao
        self.widgets_correcoes: list[CorrecaoWidget] = []
        # Personalização
        self.configure(borderwidth=2, relief=tk.GROOVE)
        # Montagem
        self._montar_primeira_linha()
        self._montar_correcoes()
    
    def _montar_primeira_linha(self):
        '''Monta a primeira linha deste widget, que contém a descrição da questão e o botão para corrigir.'''
        self.label = ttk.Label(self, text=self.questao.descricao)
        self.label.grid(row=0, columnspan=2, sticky='w',
            padx=(PADDING*2, 0), pady=(PADDING*2, 0))
        self.botao_corrigir = ttk.Button(self, text='▶️ Corrigir Questão',
            command=self._corrigir_questao)
        self.botao_corrigir.grid(row=0, sticky='e', 
            padx=(0, PADDING*2), pady=PADDING*2)

    def _montar_correcoes(self):
        '''Monta o widget de cada correção.'''
        for i, p in enumerate(self.questao.correcoes):
            tw = CorrecaoWidget(self, p)
            tw.grid(padx=PADDING*2, pady=(0, PADDING), row=i+1)
            self.widgets_correcoes += [tw]
    
    def _corrigir_questao(self):
        '''Executa todas as correcoes da questão.'''
        for tw in self.widgets_correcoes:
            tw._corrigir()
    
    def atualizar(self):
        '''Atualiza este widget.'''
        # Conta quantas correções deram certo
        self.contador_corretas = 0
        for c in self.widgets_correcoes:
            if c.resultado == 'Correta':
                self.contador_corretas += 1
        self.label.configure(text=self.questao.descricao + \
            f' ({self.contador_corretas}/{len(self.widgets_correcoes)})')


class CorrecaoWidget(ttk.Frame):
    '''Widget da Correcao.'''
    resultado = 'Não executada'

    def __init__(self, parent, correcao: Correcao):
        '''Construtor.
        Parâmetros:
        - `parent` é o widget pai que conterá este.
        - `correcao` é a correcao correspondente.'''
        super().__init__(parent)
        self.widget_questao: QuestaoWidget = parent
        self.correcao: Correcao = correcao
        # Montagem
        # A correção é montada como grid. A variável `row` serve para controlar as linhas.
        self._montar_primeira_linha()
        self._montar_entrada()
        self._montar_resultado()

    def _corrigir(self):
        '''Executa a correcao e atualiza a interface com o resultado.'''
        # Correção
        codigo, saida, erro = self.correcao.corrigir()
        # Atualização da interface
        text = self.text_resultado
        # A variável res guarda o resultado da correção
        res = f'Código: {codigo}'
        if saida:
            saida = saida[:-1]  # Remove a linha extra que sempre vem
            res += f'\nSaída:\n{saida}'
        if erro:
            res += f'\nErro:\n{erro}'
        text.configure(state=tk.NORMAL)  # Habilita a caixa de texto para edição
        text.delete(0.0, 'end')  # Limpa o texto
        text.insert('end', res)  # Insere o resultado
        altura = min(len(res.split('\n')), 20)  # Ajusta a altura
        text.configure(height=altura,
                       state=tk.DISABLED)  # Desabilita a edição
        # Atualiza o label do resultado
        # Mesmo o código sendo 0, a saída precisa ser a esperada, então é necessário que erro seja None
        self.resultado = 'Incorreta' if erro else 'Correta'
        self.label_resultado.configure(text=self.resultado)
        # Atualiza o widget da questão
        self.widget_questao.atualizar()
        # Redesenha a interface
        self.update()
        self.update_idletasks()
    
    def _montar_primeira_linha(self):
        self.label_comando = ttk.Label(self, text=f'Comando: {self.correcao.comando_completo}')
        self.label_comando.grid(column=0, sticky='w',
            padx=(PADDING*2, 0), pady=(0, PADDING))
        self.botao_corrigir = ttk.Button(self, text='▶️', width=2,
            command=self._corrigir)
        self.botao_corrigir.grid(column=1, row=0, sticky='e', pady=(0, PADDING))

    def _montar_entrada(self):
        row = 2
        ttk.Label(self, text=f'Entrada:').grid(column=0, row=row, sticky='w',
            padx=(PADDING*2, 0), pady=(0, PADDING))
        row += 1
        text_entrada = tk.Text(self, wrap=tk.WORD, width=80, height=1)
        text_entrada.grid(column=0, row=row, sticky='w', columnspan=2,
            padx=(PADDING*2, 0), pady=(0, PADDING))
        text_entrada.delete(0.0, 'end')  # Limpa o texto
        entrada = self.correcao.input.decode()
        text_entrada.insert('end', entrada)  # Insere a entrada
        altura = len(entrada.split('\n'))  # Ajusta a altura
        text_entrada.configure(
            height=altura,
            state=tk.DISABLED)  # Desabilita a edição
        self.text_entrada = text_entrada
    
    def _montar_resultado(self):
        row = 4
        ttk.Label(self, text=f'Resultado:').grid(column=0, row=row, sticky='w',
            padx=(PADDING*2, 0), pady=(0, PADDING))
        self.label_resultado = ttk.Label(self, text=f'')
        self.label_resultado.grid(column=1, row=row, sticky='e',
            padx=(PADDING*2, 0), pady=(0, PADDING))
        row += 1
        self.text_resultado = tk.Text(self, wrap=tk.WORD, 
                                    width=80, height=1, state=tk.DISABLED)
        self.text_resultado.grid(column=0, row=row, sticky='w', columnspan=2,
            padx=(PADDING*2, 0), pady=(0, PADDING))

# PROGRAMA PRINCIPAL

if __name__ == '__main__':
    app = Corretor('config.json')
    style = ttk.Style(app)
    temas = style.theme_names()
    style.theme_use(temas[0])
    app.mainloop()


