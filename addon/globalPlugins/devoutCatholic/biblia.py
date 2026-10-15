import ui
import globalPluginHandler
import wx
import os
import json

from . import anotacoes
from .__init__ import GlobalPlugin
from .progress import ReadingProgressManager
from .busca import BuscaBiblica


BIBLIA_ATIVA = None

class Biblias:
    def __init__(self):
        global BIBLIA_ATIVA
        BIBLIA_ATIVA = self  

        self.btn_anterior = None
        self.btn_proximo = None

        self.progress_manager = ReadingProgressManager()

        self.json_files = {
            "Pastoral": "catolica - pastoral.json",
            "Ave Maria": "catolica - Ave Maria.json",
            "Jerusalém": "catolica - jerusalem.json",
            "CNBB": "catolica - CNBB.json",
        }
    
    def script_openBible(self):
        self.menuBiblia()
    
    
    
    def continuarLeitura(self, frame_para_fechar=None):
        """Continua a leitura de onde o usuário parou.

        Se uma janela (frame) de seleção estiver aberta, fecha antes de abrir a leitura.
        """
        progresso_atual = self.progress_manager.get_progress()
        if not progresso_atual:
            wx.MessageBox("Nenhum progresso de leitura encontrado.", "Aviso", wx.OK | wx.ICON_INFORMATION)
            return
        
        try:
            if frame_para_fechar is not None:
                try:
                    frame_para_fechar.Destroy()
                except Exception:
                    pass

            versao = progresso_atual["versao"]
            self.versao_selecionada = versao
            caminho_arquivo = os.path.join(os.path.dirname(__file__), "dados", "versions", self.json_files[versao])
            
            with open(caminho_arquivo, "r", encoding="utf-8-sig") as f:
                self.biblia = json.load(f)
                self.livros = [livro["name"] for livro in self.biblia]
            
            livro_nome = progresso_atual["livro"]
            for i, livro in enumerate(self.biblia):
                if livro["name"] == livro_nome:
                    self.livro_selecionado = livro
                    self.capitulo_selecionado = progresso_atual["capitulo"] - 1  
                    self.versiculo_inicial = progresso_atual["versiculo"] - 1  
                    wx.CallAfter(self.exibirCapitulo)
                    return
            
            wx.MessageBox(f"Livro '{livro_nome}' não encontrado na versão atual.", "Erro", wx.OK | wx.ICON_ERROR)
        except Exception as e:
            wx.MessageBox(f"Erro ao continuar leitura: {e}", "Erro", wx.OK | wx.ICON_ERROR)

    def selecionaVersao(self):
        """Exibe diretamente as versões católicas disponíveis."""
        frame = wx.Frame(None, title="Selecione a Versão da Bíblia", size=(350, 300))
        panel = wx.Panel(frame)

        sizer = wx.BoxSizer(wx.VERTICAL)

        for versao in self.json_files.keys():
            btn = wx.Button(panel, label=versao)
            btn.Bind(
                wx.EVT_BUTTON,
                lambda event, v=versao, f=frame: self.selecionarVersao(v, f)
            )
            sizer.Add(btn, 0, wx.EXPAND | wx.ALL, 10)

        panel.SetSizerAndFit(sizer)
        frame.Show()

    def menuBiblia(self):
        frame = wx.Frame(None, title="Bíblia", size=(450, 250))
        panel = wx.Panel(frame)

        sizer = wx.BoxSizer(wx.VERTICAL)

        progresso = self.progress_manager.get_progress()

        if progresso:
            btn_continuar = wx.Button(
                panel,
                label=f"Continuar leitura - {progresso['livro']} {progresso['capitulo']}"
            )
            sizer.Add(btn_continuar, 0, wx.EXPAND | wx.ALL, 10)
            sizer.Add(wx.StaticLine(panel), 0, wx.EXPAND | wx.ALL, 5)
            btn_continuar.Bind(wx.EVT_BUTTON, lambda e: self.continuarLeitura(frame))

        btn_selecionar = wx.Button(panel, label="Selecionar Versão")
        sizer.Add(btn_selecionar, 0, wx.EXPAND | wx.ALL, 10)
        sizer.Add(wx.StaticLine(panel), 0, wx.EXPAND | wx.ALL, 5)

        btn_buscar = wx.Button(panel, label="Buscar por Trecho")
        sizer.Add(btn_buscar, 0, wx.EXPAND | wx.ALL, 10)

        btn_menu_principal = wx.Button(panel, label="Voltar ao Menu Principal")
        sizer.Add(btn_menu_principal, 0, wx.EXPAND | wx.ALL, 10)

        panel.SetSizer(sizer)

        btn_selecionar.Bind(
    wx.EVT_BUTTON,
    lambda e, f=frame: (f.Destroy(), self.selecionaVersao())
)
        btn_buscar.Bind(
    wx.EVT_BUTTON,
    lambda e, f=frame: (f.Destroy(), self.abrirJanelaBusca(None))
)

        btn_menu_principal.Bind(
    wx.EVT_BUTTON,
    lambda e, f=frame: self.menuInicial(f)
)

        frame.Show()

    def abrirResultadoBusca(self, resultado):
        self.versao_selecionada = resultado["versao"]

        caminho = os.path.join(
            os.path.dirname(__file__),
            "dados",
            "versions",
            self.json_files[self.versao_selecionada]
        )

        with open(caminho, "r", encoding="utf-8-sig") as f:
            self.biblia = json.load(f)

        self.livro_selecionado = next(
            l for l in self.biblia if l["name"] == resultado["livro"]
        )
        self.capitulo_selecionado = resultado["capitulo"]
        self.versiculo_inicial = resultado["versiculo"]

        wx.CallAfter(self.exibirCapitulo)

    def exibirMenu(self, btn, menu):
        """Exibe o menu na posição do botão."""
        btn.PopupMenu(menu)

    def abrirJanelaBusca(self, frame_pai):
        frame = wx.Frame(frame_pai, title="Buscar Trecho Bíblico", size=(500, 450))
        panel = wx.Panel(frame)

        sizer = wx.BoxSizer(wx.VERTICAL)

        txt_busca = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER)
        txt_busca.SetHint("Digite uma palavra ou trecho bíblico")
        sizer.Add(txt_busca, 0, wx.EXPAND | wx.ALL, 10)

        sizer.Add(
            wx.StaticText(panel, label="Buscar nas versões:"),
            0,
            wx.LEFT | wx.TOP,
            10
        )

        versoes = list(self.json_files.keys())

        lista_versoes = wx.CheckListBox(
            panel,
            choices=versoes,
            style=wx.LB_SINGLE
        )

        for i in range(len(versoes)):
            lista_versoes.Check(i)

        def on_check(event):
            index = event.GetInt()
            nome = lista_versoes.GetString(index)

            if lista_versoes.IsChecked(index):
                ui.message("marcado")
            else:
                ui.message("desmarcado")

        lista_versoes.Bind(wx.EVT_CHECKLISTBOX, on_check)

        btn_buscar = wx.Button(panel, label="Buscar")
        btn_voltar = wx.Button(panel, label="Voltar ao Menu Bíblia")

        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer.Add(btn_voltar, 0, wx.RIGHT, 10)
        btn_sizer.Add(btn_buscar, 0)

        sizer.Add(btn_sizer, 0, wx.ALIGN_CENTER | wx.ALL, 10)

        panel.SetSizer(sizer)

        def executarBusca():
            termo = txt_busca.GetValue().strip()

            if not termo:
                ui.message("Digite algo para buscar.")
                return

            indices = lista_versoes.GetCheckedItems()
            if not indices:
                ui.message("Selecione ao menos uma versão para buscar.")
                return

            versoes_selecionadas = [versoes[i] for i in indices]

            BuscaBiblica(
                frame,  
                termo,
                self.json_files,
                versoes_selecionadas,
                self.abrirResultadoBusca,
                self.menuBiblia
            )

        txt_busca.Bind(wx.EVT_TEXT_ENTER, lambda e: executarBusca())
        btn_buscar.Bind(wx.EVT_BUTTON, lambda e: executarBusca())
        btn_voltar.Bind(wx.EVT_BUTTON, lambda e: (frame.Destroy(), self.menuBiblia()))

        frame.Show()
        txt_busca.SetFocus()

    def selecionarVersao(self, versao, frame):
        """Processa a versão selecionada e continua o fluxo."""
        self.versao_selecionada = versao
        frame.Destroy()  
        wx.CallAfter(self.listar_livros_e_exibir_menu)

    def listar_livros_e_exibir_menu(self):
        """Carrega o arquivo JSON da versão selecionada e exibe a lista de livros."""
        caminho_arquivo = os.path.join(os.path.dirname(__file__), "dados", "versions", self.json_files[self.versao_selecionada])

        try:
            with open(caminho_arquivo, "r", encoding="utf-8-sig") as f:
                self.biblia = json.load(f)
                self.livros = [livro["name"] for livro in self.biblia]

            wx.CallAfter(self.selecionaLivro)
        except Exception as e:
            wx.MessageBox(f"Erro ao carregar a versão da Bíblia: {e}", "Erro")

    def selecionaLivro(self):
        """Exibe um diálogo para o usuário selecionar um livro."""
        with wx.SingleChoiceDialog(None, "Selecione um livro:", "Livros da Bíblia", self.livros) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                escolha = dlg.GetSelection()
                self.livro_selecionado = self.biblia[escolha]
                wx.CallAfter(self.selecionaCapitulo)
            else:
                ui.message("Nenhum livro foi selecionado.")

    def selecionaCapitulo(self):
        """Exibe um diálogo para o usuário selecionar um capítulo do livro escolhido."""
        total_capitulos = len(self.livro_selecionado["chapters"])

        dialogo = wx.Dialog(None, title=f"Capítulos de {self.livro_selecionado['name']}", size=(300, 200))
        panel = wx.Panel(dialogo)

        spin_capitulo = wx.SpinCtrl(panel, value="1", min=1, max=total_capitulos, size=(80, 30))

        btn_ok = wx.Button(panel, label="OK")
        btn_ok.SetDefault()  

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(wx.StaticText(panel, label="Selecione um Capítulo:"), 0, wx.EXPAND | wx.ALL, 10)
        sizer.Add(spin_capitulo, 0, wx.EXPAND | wx.ALL, 10)
        sizer.Add(btn_ok, 0, wx.ALIGN_CENTER | wx.ALL, 10)

        panel.SetSizerAndFit(sizer)

        def onConfirm(event):
            dialogo.EndModal(wx.ID_OK)

        btn_ok.Bind(wx.EVT_BUTTON, onConfirm)

        def onKeyPress(event):
            if event.GetKeyCode() == wx.WXK_RETURN:  
                dialogo.EndModal(wx.ID_OK)
            else:
                event.Skip()  

        spin_capitulo.Bind(wx.EVT_KEY_DOWN, onKeyPress)

        if dialogo.ShowModal() == wx.ID_OK:
            self.capitulo_selecionado = spin_capitulo.GetValue() - 1  
            wx.CallAfter(self.selecionaVersiculo)
        else:
            ui.message("Nenhum capítulo foi selecionado.")

    def selecionaVersiculo(self):
        """Exibe um diálogo para o usuário selecionar o versículo inicial do capítulo escolhido."""
        capitulo = self.livro_selecionado["chapters"][self.capitulo_selecionado]
        total_versiculos = len(capitulo)

        dialogo = wx.Dialog(None, title=f"Versículos do Capítulo {self.capitulo_selecionado + 1}", size=(300, 200))
        panel = wx.Panel(dialogo)

        spin_versiculo = wx.SpinCtrl(panel, value="1", min=1, max=total_versiculos, size=(80, 30))

        btn_ok = wx.Button(panel, label="OK")
        btn_ok.SetDefault()  

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(wx.StaticText(panel, label="Selecione o Versículo:"), 0, wx.EXPAND | wx.ALL, 10)
        sizer.Add(spin_versiculo, 0, wx.EXPAND | wx.ALL, 10)
        sizer.Add(btn_ok, 0, wx.ALIGN_CENTER | wx.ALL, 10)

        panel.SetSizerAndFit(sizer)

        def onConfirm(event):
            dialogo.EndModal(wx.ID_OK)

        btn_ok.Bind(wx.EVT_BUTTON, onConfirm)

        def onKeyPress(event):
            if event.GetKeyCode() == wx.WXK_RETURN:  
                dialogo.EndModal(wx.ID_OK)
            else:
                event.Skip()  

        spin_versiculo.Bind(wx.EVT_KEY_DOWN, onKeyPress)

        if dialogo.ShowModal() == wx.ID_OK:
            self.versiculo_inicial = spin_versiculo.GetValue() - 1  
            wx.CallAfter(self.exibirCapitulo)
        else:
            ui.message("Nenhum versículo foi selecionado.")

    def exibirCapitulo(self):
        """Exibe o conteúdo do capítulo a partir do versículo selecionado."""
        capitulo = self.livro_selecionado["chapters"][self.capitulo_selecionado]
        conteudo = "\n".join(
            [f"{self.versiculo_inicial + i + 1}. {versiculo}" for i, versiculo in enumerate(capitulo[self.versiculo_inicial:])]
        )

        self.progress_manager.update_progress(
            self.versao_selecionada,
            self.livro_selecionado["name"],
            self.capitulo_selecionado + 1,
            self.versiculo_inicial + 1
        )

        frame = wx.Frame(None, title=f"{self.livro_selecionado['name']} - Capítulo {self.capitulo_selecionado + 1}, Versículo {self.versiculo_inicial + 1}", size=(600, 400))
        panel = wx.Panel(frame)

        text_ctrl = wx.TextCtrl(panel, value=conteudo, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL)
        text_ctrl.SetFocus()

        btn_anterior = wx.Button(panel, label="Capítulo Anterior")
        btn_proximo = wx.Button(panel, label="Próximo Capítulo")

        self.btn_anterior = btn_anterior
        self.btn_proximo = btn_proximo

        btn_mais_opcoes = wx.Button(panel, label="Mais Opções")

        menu = wx.Menu()
        item_escolher_livro = menu.Append(wx.ID_ANY, "Livros")
        item_escolher_versao = menu.Append(wx.ID_ANY, "Versões")
        item_menu_inicial = menu.Append(wx.ID_ANY, "Menu Inicial")
        item_criar_nota = menu.Append(wx.ID_ANY, "Criar Nota")

        btn_mais_opcoes.Bind(wx.EVT_BUTTON, lambda event: self.exibirMenu(btn_mais_opcoes, menu))

        frame.Bind(wx.EVT_MENU, lambda event: self.voltarEscolhaLivro(frame), item_escolher_livro)
        frame.Bind(wx.EVT_MENU, lambda event: self.voltarEscolhaVersao(frame), item_escolher_versao)
        frame.Bind(wx.EVT_MENU, lambda event: self.menuInicial(frame), item_menu_inicial)
        frame.Bind(wx.EVT_MENU, self.criarNota, item_criar_nota)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(text_ctrl, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer.Add(btn_anterior, flag=wx.RIGHT, border=10)
        btn_sizer.Add(btn_proximo, flag=wx.RIGHT, border=10)
        btn_sizer.Add(btn_mais_opcoes, flag=wx.RIGHT, border=10)
        sizer.Add(btn_sizer, flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        panel.SetSizer(sizer)

        btn_anterior.Bind(wx.EVT_BUTTON, lambda event: self.alternarCapitulo(-1, frame))
        btn_proximo.Bind(wx.EVT_BUTTON, lambda event: self.alternarCapitulo(1, frame))

        frame.Show()

    def exibirMenu(self, button, menu):
        """Exibe o menu ao lado do botão 'Mais Opções'."""
        pos = button.GetPosition()
        size = button.GetSize()
        menu_pos = (pos.x, pos.y + size.y)  
        button.GetParent().PopupMenu(menu, menu_pos)

    def menuInicial(self, frame_atual):
        menu = GlobalPlugin()
        menu.exibirMenu()
        frame_atual.Destroy()


    def criarNota(self, event):
        try:
            versao = self.versao_selecionada
            livro = self.livro_selecionado["name"]
            capitulo = self.capitulo_selecionado + 1
            versiculos = self.livro_selecionado["chapters"][self.capitulo_selecionado]

            anotacoes.NotasManager(
                versao,
                livro,
                capitulo,
                versiculos,
                self
            )
        except AttributeError as e:
            wx.MessageBox(
                f"Erro ao criar nota: {e}",
                "Erro",
                wx.OK | wx.ICON_ERROR
            )

    def alternarCapitulo(self, direcao, frame_atual):
        novo_indice = self.capitulo_selecionado + direcao
        if 0 <= novo_indice < len(self.livro_selecionado["chapters"]):
            self.capitulo_selecionado = novo_indice
            self.versiculo_inicial = 0
            frame_atual.Destroy()
            wx.CallAfter(self.exibirCapitulo)
        else:
            ui.message("Não há mais capítulos nessa direção.")

    def voltarEscolhaLivro(self, frame_atual):
        """Fecha a janela atual e retorna para a lista de livros."""
        frame_atual.Destroy()
        wx.CallAfter(self.selecionaLivro)

    def voltarEscolhaVersao(self, frame_atual):
        """Fecha a janela atual e retorna ao menu inicial para selecionar a versão da Bíblia."""
        frame_atual.Destroy()
        wx.CallAfter(self.selecionaVersao)


