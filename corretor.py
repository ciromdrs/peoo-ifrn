import json, subprocess, tkinter as tk

from tkinter import ttk, scrolledtext


# CORREÇÃO DE QUESTÕES

# Constantes
TIMEOUT = 2

# Classes

class Questao:
    '''Uma questão para corrigir.'''

    def __init__(self, descricao: str, comando: str, script: str, testes: list):
        '''Construtor.

        Parâmetros:
        - `descricao` é uma descrição da questão.
        - `comando` é o comando do terminal para executar o script da resposta.
        - `script` é o script da resposta.
        - `testes` são os argumentos e verificações da saída do script para corrigir a questão.
        '''
        self.descricao = descricao
        self.script = script
        self.testes = testes
        # Converte os testes em objetos Teste
        self.testes = []
        for args_script, func_expect, args_expect in testes:
            self.testes += [
                Teste(comando, script, args_script, func_expect, args_expect)]


class Teste:
    '''Um teste de uma questão.'''

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

    def testar(self) -> tuple[int, str, str]:
        '''Executa o teste e retorna o código de saída, a saída e o erro.'''
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


# Funções de teste

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
PADDING_P = 5
PADDING_M = 10
PADDING_G = 20


class ScrolledFrame(tk.Frame):
    '''Frame com scrollabar.
    *ATENÇÃO:* para colocar widgets dentro deste, passe o `.conteudo` como `parent` do widget filho.'''
    def __init__(self, master, canvas_size: tuple[int,int] = (2000,694), *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)

        # Na raiz, é necessário um Canvas e a Scrollbar
        canvas = tk.Canvas(self, height=canvas_size[0], width=canvas_size[1])
        scrollbar = ttk.Scrollbar(self, command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        # Dentro do canvas, é necessário um Frame
        conteudo = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=conteudo, anchor="nw")
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
        self.title(self.config['titulo'])
        # Configura o tamanho da janela
        self.geometry("1024x600")
        # O frame principal contém todos os elementos da tela
        # Isso facilita o redimensionamento da janela sem alterar seu conteúdo
        frame_principal = ttk.Frame(self)
        frame_principal.pack()
        # Montagem da interface
        botao_testar_todas = ttk.Button(frame_principal, text='Testar Todas',
            command=self._testar_todas)
        botao_testar_todas.pack(anchor='e', padx=PADDING_G, pady=PADDING_G)
        self.frame_questoes = ScrolledFrame(self, borderwidth=2, relief=tk.GROOVE)
        self.frame_questoes.pack()
        self._montar_questoes()
    
    def _montar_questoes(self):
        '''Monta os widgets das questões'''
        self.widgets_questoes: list[QuestaoWidget] = []
        for dados in self.config['questoes']:
            desc = dados['descricao']
            comando = dados['comando']
            script = dados['script']
            testes = dados['testes']
            questao = Questao(descricao=desc, comando=comando, script=script,
                testes=testes)
            qw = QuestaoWidget(self.frame_questoes.conteudo, questao)
            qw.pack()
            self.widgets_questoes += [qw]

    def _testar_todas(self):
        '''Testa todas as questões.'''
        for qw in self.widgets_questoes:
            qw._testar_questao()
        

class QuestaoWidget(ttk.Frame):
    '''Widget de Questões.'''

    def __init__(self, parent, questao: Questao):
        '''Construtor.
        Parâmetros:
        - `parent` é o widget pai que conterá este.
        - `questao` é a questão correspondente.'''
        super().__init__(parent)
        self.questao: Questao = questao
        self.widgets_testes: list[TesteWidget] = []
        # Personalização
        self.configure(borderwidth=2, relief=tk.GROOVE)
        # Montagem
        row = 0
        self._montar_primeira_linha(row)
        row += 1
        self._montar_testes()
    
    def _montar_primeira_linha(self, row):
        '''Monta a primeira linha deste widget, que contém a descrição da questão e o botão para testar.'''
        self.label = ttk.Label(self, text=self.questao.descricao)
        self.label.grid(column=0, row=row, columnspan=2, sticky='w',
            padx=(PADDING_M, 0), pady=(PADDING_M, 0))
        self.botao_testar = ttk.Button(self, text='Testar Questão',
            command=self._testar_questao)
        self.botao_testar.grid(row=row, sticky='e', 
            padx=(0, PADDING_M), pady=PADDING_M)

    def _montar_testes(self):
        '''Monta o widget de cada teste.'''
        for p in self.questao.testes:
            tw = TesteWidget(self, p)
            tw.grid(padx=PADDING_M, pady=(0, PADDING_P))
            self.widgets_testes += [tw]
    
    def _testar_questao(self):
        '''Executa todos os testes da questão.'''
        for tw in self.widgets_testes:
            tw._testar()


class TesteWidget(ttk.Frame):
    '''Widget do Teste.'''

    def __init__(self, parent, teste: Teste):
        '''Construtor.
        Parâmetros:
        - `parent` é o widget pai que conterá este.
        - `teste` é o teste correspondente.'''
        super().__init__(parent)
        self.teste: Teste = teste
        # Montagem
        # O teste é montado como grid. A variável `row` serve para controlar as linhas.
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
        '''Executa o teste e atualiza a interface com o resultado.'''
        text = self.text_resultado
        # Habilita a caixa de texto para edição
        text.configure(state=tk.NORMAL)
        # Limpa o texto
        text.delete(1.0, 'end')
        codigo, saida, erro = self.teste.testar()
        if saida == '': saida = '\n'
        # Preenche com o resultado do teste
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
    App('config.json').mainloop()
