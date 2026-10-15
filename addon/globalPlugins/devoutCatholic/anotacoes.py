import wx
import ui
import json
import os
import globalPluginHandler

class NotasStorage:

    def __init__(self, pluginRef, arquivo="dados/notas.json"):
        self.pluginRef = pluginRef  
        self.caminho = os.path.join(os.path.dirname(__file__), arquivo)
        self.notas = self.carregarNotas()

    def carregarNotas(self):
        if os.path.exists(self.caminho):
            with open(self.caminho, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def salvarNotas(self):
        try:
            with open(self.caminho, "w", encoding="utf-8") as arquivo:
                json.dump(self.notas, arquivo, ensure_ascii=False, indent=4)
        except Exception as e:
            wx.MessageBox(f"Erro ao salvar as notas: {str(e)}", "Erro", wx.OK | wx.ICON_ERROR)

    def adicionarNota(self, nota):
        self.notas.append(nota)
        self.salvarNotas()

    def exibirNotas(self):
        if not self.notas:
            wx.MessageBox(
                "Você não tem anotações salvas!",
                "Aviso",
                wx.OK | wx.ICON_INFORMATION
            )
            wx.CallLater(0, self.pluginRef.exibirMenu)
            return

        self.frame = wx.Frame(None, title="Notas Salvas", size=(600, 400))
        panel = wx.Panel(self.frame)
        sizer = wx.BoxSizer(wx.VERTICAL)

        for i, nota in enumerate(self.notas):
            btn_nota = wx.Button(panel, label=f"{i + 1}. {nota['titulo']}")
            btn_nota.Bind(wx.EVT_BUTTON, lambda event, n=nota: self.mostrarNota(n))
            sizer.Add(btn_nota, flag=wx.EXPAND | wx.ALL, border=5)

        btn_menu = wx.Button(panel, label="Voltar ao Menu")
        btn_menu.Bind(wx.EVT_BUTTON, lambda event: self.voltarAoMenu())
        sizer.Add(btn_menu, flag=wx.ALIGN_CENTER | wx.TOP, border=10)

        btn_fechar = wx.Button(panel, label="Fechar")
        btn_fechar.Bind(wx.EVT_BUTTON, lambda event: self.frame.Close())
        sizer.Add(btn_fechar, flag=wx.ALIGN_CENTER | wx.TOP, border=20)

        panel.SetSizer(sizer)
        self.frame.Show()

    def voltarAoMenu(self):
        """Fecha a tela de notas e exibe o menu principal do plugin."""
        if hasattr(self, "frame") and self.frame:
            self.frame.Close()
        wx.CallLater(0, self.pluginRef.exibirMenu)

    def mostrarNota(self, nota):
        """Exibe o conteúdo de uma nota e permite edição e exclusão."""
        frame = wx.Frame(None, title=f"Nota: {nota['titulo']}", size=(600, 500))
        panel = wx.Panel(frame)
        sizer = wx.BoxSizer(wx.VERTICAL)

        if hasattr(self, "frame") and self.frame:
            try:
                if self.frame.IsShown():
                    self.frame.Close()
            except RuntimeError:
                pass


        conteudo = f"Título: {nota['titulo']}\n"

        if nota.get("origem") != "liturgia":
            conteudo += f"Versão: {nota['versao']}\n"
            conteudo += f"{nota['livro']} {nota['capitulo']}\n\n"

        if nota.get('versiculos'):
            conteudo += "Versículos:\n"
            for v in nota['versiculos']:
                conteudo += f"{v['numero']}. {v['texto']}\n"

        conteudo += f"\nDescrição:\n{nota['descricao']}"


        txt_conteudo = wx.TextCtrl(
            panel,
            value=conteudo,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL
        )

        sizer.Add(txt_conteudo, 1, wx.EXPAND | wx.ALL, 10)

        btn_editar = wx.Button(panel, label="Editar")
        btn_excluir = wx.Button(panel, label="Excluir")
        btn_lista = wx.Button(panel, label="Lista de Notas")
        btn_fechar = wx.Button(panel, label="Fechar")

        sizer_botoes = wx.BoxSizer(wx.HORIZONTAL)
        sizer_botoes.Add(btn_editar, 0, wx.RIGHT, 5)
        sizer_botoes.Add(btn_excluir, 0, wx.LEFT, 5)
        sizer_botoes.Add(btn_lista, 0, wx.LEFT, 5)
        sizer_botoes.Add(btn_fechar, 0, wx.LEFT, 5)

        sizer.Add(sizer_botoes, 0, wx.ALIGN_CENTER | wx.ALL, 10)

        def abrir_editor(event):
            frame.Close()
            EditorNotaExistente(self, nota, callback_reabrir=self.mostrarNota)

        btn_editar.Bind(wx.EVT_BUTTON, abrir_editor)

        btn_excluir.Bind(wx.EVT_BUTTON, lambda e: self.excluirNota(frame, nota))
        btn_lista.Bind(wx.EVT_BUTTON, lambda e: (frame.Close(), self.exibirNotas()))
        btn_fechar.Bind(wx.EVT_BUTTON, lambda e: frame.Close())

        panel.SetSizer(sizer)
        frame.Show()

    def excluirNota(self, frame, nota):
        dialogo = wx.MessageDialog(
            frame,
            "Deseja realmente excluir esta nota? Esta ação não poderá ser desfeita.",
            "Confirmar Exclusão",
            wx.YES_NO | wx.ICON_WARNING
        )

        if dialogo.ShowModal() == wx.ID_YES:
            self.notas.remove(nota)
            self.salvarNotas()
            wx.MessageBox("Nota excluída com sucesso!", "Sucesso", wx.OK | wx.ICON_INFORMATION)
            frame.Close()
            self.exibirNotas()


class NotasManager:
    def __init__(self, versao, livro, capitulo, versiculos, pluginRef, origem="biblia"):
        self.versao = versao
        self.livro = livro
        self.capitulo = capitulo
        self.versiculos = versiculos or []
        self.origem = origem
        self.selecionados = []
        self.titulo = ""

        self.notasStorage = NotasStorage(pluginRef)

        if self.origem == "liturgia":
            self.exibirTituloNota(frame_anterior=None)
        else:
            self.exibirSelecaoVersiculos()
            
    def exibirSelecaoVersiculos(self):
        frame = wx.Frame(None, title=f"Selecione os versículos - {self.livro} {self.capitulo}", size=(600, 400))
        panel = wx.Panel(frame)

        
        sizer = wx.BoxSizer(wx.VERTICAL)
        labels = [f"{i + 1}. {texto}" for i, texto in enumerate(self.versiculos)]

        self.lista_versiculos = wx.CheckListBox(
            panel,
            choices=labels,
            style=wx.LB_SINGLE
        )

        sizer.Add(self.lista_versiculos, 1, wx.EXPAND | wx.ALL, 10)

        
        btn_avancar = wx.Button(panel, label="Avançar")
        btn_avancar.Bind(wx.EVT_BUTTON, lambda event: self.exibirTituloNota(frame))

        
        btn_cancelar = wx.Button(panel, label="Cancelar")
        btn_cancelar.Bind(wx.EVT_BUTTON, lambda event: frame.Close())

        
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer.Add(btn_cancelar, flag=wx.RIGHT, border=10)
        btn_sizer.Add(btn_avancar)

        
        sizer.Add(btn_sizer, flag=wx.ALIGN_CENTER | wx.TOP, border=20)
        panel.SetSizer(sizer)
        frame.Show()

        btn_avancar.Enable(False)

        def on_check(event):
            index = event.GetInt()
            texto = self.lista_versiculos.GetString(index)

            if self.lista_versiculos.IsChecked(index):
                ui.message("marcado")
            else:
                ui.message("desmarcado")

            self.ativarBotaoAvancar(btn_avancar)

        self.lista_versiculos.Bind(wx.EVT_CHECKLISTBOX, on_check)
        

    def ativarBotaoAvancar(self, btn_avancar):
        if self.lista_versiculos.GetCheckedItems():
            btn_avancar.Enable(True)
        else:
            btn_avancar.Enable(False)

    def exibirTituloNota(self, frame_anterior):
        """Exibe a caixa para o usuário inserir o título da nota usando wx.TextEntryDialog.

        Se nenhuma seleção de versículos ocorreu, segue sem versículos.
        """
        if frame_anterior is not None:
            try:
                self.selecionados = [
                    (i + 1, self.versiculos[i])
                    for i in self.lista_versiculos.GetCheckedItems()
                ]
                frame_anterior.Destroy()
            except Exception:
                self.selecionados = []
        else:
            self.selecionados = []

        dialog = wx.TextEntryDialog(None, "Digite o título da sua nota:", "Título da Nota", "", style=wx.OK | wx.CANCEL)

        if dialog.ShowModal() == wx.ID_OK:
            titulo = dialog.GetValue()

            if not titulo.strip():
                wx.MessageBox("O título não pode estar vazio.", "Erro", wx.OK | wx.ICON_ERROR)
                dialog.Destroy()
                return

            dialog.Destroy()

            self.exibirNotaEditavel(titulo)

    def exibirNotaEditavel(self, titulo):
        self.titulo = titulo

        frame = wx.Frame(None, title="Editar Nota", size=(600, 500))
        panel = wx.Panel(frame)
        sizer = wx.BoxSizer(wx.VERTICAL)

        info = f"Título: {self.titulo}\n"

        if self.origem != "liturgia":
            info += f"Versão: {self.versao}\n"
            info += f"{self.livro} {self.capitulo}\n\n"

            if self.selecionados:
                info += "Versículos selecionados:\n"
                for num, texto in self.selecionados:
                    info += f"{num}. {texto}\n"

        txt_info = wx.TextCtrl(
            panel,
            value=info,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL
        )

        sizer.Add(txt_info, 0, wx.EXPAND | wx.ALL, 10)

        self.txt_nota = wx.TextCtrl(
            panel,
            value="",
            style=wx.TE_MULTILINE | wx.HSCROLL
        )

        sizer.Add(self.txt_nota, 1, wx.EXPAND | wx.ALL, 10)

        btn_salvar = wx.Button(panel, label="Salvar Nota")
        btn_cancelar = wx.Button(panel, label="Cancelar")

        btn_salvar.Bind(wx.EVT_BUTTON, lambda e: self.salvarNota(frame))
        btn_cancelar.Bind(wx.EVT_BUTTON, lambda e: frame.Destroy())

        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer.Add(btn_salvar, 0, wx.ALL, 10)
        btn_sizer.Add(btn_cancelar, 0, wx.ALL, 10)

        sizer.Add(btn_sizer, 0, wx.ALIGN_CENTER)

        panel.SetSizer(sizer)
        frame.Show()

        txt_info.SetFocus()

    def fecharJanela(self, frame):
        """Fecha a janela de edição sem salvar as alterações."""
        frame.Destroy()

    def salvarNota(self, frame):
        descricao = self.txt_nota.GetValue().strip()

        if not descricao:
            wx.MessageBox(
                "A descrição não pode estar vazia.",
                "Erro",
                wx.OK | wx.ICON_ERROR
            )
            return

        nota = {
            "titulo": self.titulo,
            "versao": self.versao if self.origem != "liturgia" else None,
            "livro": self.livro if self.origem != "liturgia" else None,
            "capitulo": self.capitulo if self.origem != "liturgia" else None,
            "versiculos": (
                [{"numero": num, "texto": texto} for num, texto in self.selecionados]
                if self.origem != "liturgia"
                else []
            ),
            "descricao": descricao,
            "origem": self.origem
        }

        self.notasStorage.adicionarNota(nota)

        wx.MessageBox(
            "Nota salva com sucesso!",
            "Confirmação",
            wx.OK | wx.ICON_INFORMATION
        )

        frame.Destroy()

class EditorNotaExistente:
    def __init__(self, storage, nota, callback_reabrir=None):
        self.storage = storage
        self.nota = nota
        self.callback_reabrir = callback_reabrir
        self.exibirTela()

    def exibirTela(self):
        self.frame = wx.Frame(
            None,
            title=f"Editar Nota: {self.nota['titulo']}",
            size=(600, 500)
        )
        panel = wx.Panel(self.frame)
        sizer = wx.BoxSizer(wx.VERTICAL)

        info = f"Título: {self.nota['titulo']}\n"
        info += f"Versão: {self.nota['versao']}\n"
        info += f"{self.nota['livro']} {self.nota['capitulo']}\n\n"

        if self.nota.get("versiculos"):
            info += "Versículos:\n"
            for v in self.nota["versiculos"]:
                info += f"{v['numero']}. {v['texto']}\n"

        txt_info = wx.TextCtrl(
            panel,
            value=info,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL
        )

        sizer.Add(txt_info, 0, wx.EXPAND | wx.ALL, 10)

        self.txt_descricao = wx.TextCtrl(
            panel,
            value=self.nota["descricao"],
            style=wx.TE_MULTILINE | wx.HSCROLL
        )

        sizer.Add(self.txt_descricao, 1, wx.EXPAND | wx.ALL, 10)

        btn_salvar = wx.Button(panel, label="Salvar Alteração")
        btn_cancelar = wx.Button(panel, label="Cancelar")

        btn_salvar.Bind(wx.EVT_BUTTON, self.salvar)
        btn_cancelar.Bind(wx.EVT_BUTTON, lambda e: self.frame.Destroy())

        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer.Add(btn_salvar, 0, wx.ALL, 10)
        btn_sizer.Add(btn_cancelar, 0, wx.ALL, 10)

        sizer.Add(btn_sizer, 0, wx.ALIGN_CENTER)

        panel.SetSizer(sizer)
        self.frame.Show()

        txt_info.SetFocus()

    def salvar(self, event):
        nova_descricao = self.txt_descricao.GetValue().strip()

        if not nova_descricao:
            wx.MessageBox(
                "A descrição não pode estar vazia.",
                "Erro",
                wx.OK | wx.ICON_ERROR
            )
            return

        self.nota["descricao"] = nova_descricao
        self.storage.salvarNotas()

        wx.MessageBox(
            "Nota atualizada com sucesso!",
            "Sucesso",
            wx.OK | wx.ICON_INFORMATION
        )

        self.frame.Destroy()

        if self.callback_reabrir:
            wx.CallLater(0, self.callback_reabrir, self.nota)
