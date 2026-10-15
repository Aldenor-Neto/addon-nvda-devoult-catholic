import wx
import ui
import globalPluginHandler


class GlobalPlugin(globalPluginHandler.GlobalPlugin):

    def script_openMainMenu(self, gesture):
        self.showMenu()

    script_openMainMenu.__doc__ = _("Menu principal do Devout Catholic")
    script_openMainMenu.category = _("Devout Catholic")

    def showMenu(self):
        wx.CallLater(0, self.exibirMenu)

    def exibirMenu(self):
        self.dialog = wx.Dialog(
            None,
            title="Devout Catholic",
            size=(350, 450)
        )

        panel = wx.Panel(self.dialog)
        sizer = wx.BoxSizer(wx.VERTICAL)

        botoes = [
            ("Bíblia Sagrada", self.abrirBiblia),
            ("Liturgia Diária", self.abrirLiturgia),
            #("Celebração da Palavra", self.abrirCelebracao),
            #("Orações Eucarísticas", self.abrirOracoes),
            ("Catecismo (CIC)", self.abrirCatecismo),
            ("Santo do Dia", self.abrirSantoDoDia),
            ("Motivacional", self.abrirMotivacional),
            ("Anotações", self.abrirAnotacoes),
        ]

        for label, handler in botoes:
            btn = wx.Button(panel, label=label)
            btn.Bind(wx.EVT_BUTTON, handler)
            sizer.Add(btn, 0, wx.EXPAND | wx.ALL, 8)

        panel.SetSizerAndFit(sizer)
        self.dialog.ShowModal()

    # ==== Aberturas de telas ====

    def abrirBiblia(self, event):
        from .biblia import Biblias
        Biblias().script_openBible()
        self.dialog.Destroy()

    def abrirLiturgia(self, event):
        from .liturgia import LiturgiaUI
        LiturgiaUI()
        self.dialog.Destroy()

    def abrirCelebracao(self, event):
        from .celebracao import CelebracaoUI
        CelebracaoUI().show()
        self.dialog.Destroy()

    def abrirOracoes(self, event):
        from .oracoes import OracoesUI
        OracoesUI().show()
        self.dialog.Destroy()

    def abrirCatecismo(self, event):
        from .catecismo import CatecismoUI
        CatecismoUI().show()
        self.dialog.Destroy()

    def abrirSantoDoDia(self, event):
        from .santo_do_dia import SantoDoDiaUI
        SantoDoDiaUI().show()
        self.dialog.Destroy()

    def abrirMotivacional(self, event):
        from .motivacional import Motivacional
        Motivacional().show()
        self.dialog.Destroy()

    def abrirAnotacoes(self, event):
        from .anotacoes import NotasStorage
        NotasStorage(self).exibirNotas()
        self.dialog.Destroy()

    __gestures = {
        "kb:NVDA+shift+l": "openMainMenu"
    }
