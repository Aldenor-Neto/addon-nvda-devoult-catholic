import wx
import ui
import datetime

from .liturgia_cache import get_liturgia_by_date
from . import anotacoes
from .__init__ import GlobalPlugin


class SelecionarDataDialog(wx.Dialog):
    def __init__(self, parent, data_atual):
        super().__init__(parent, title="Selecionar Data", size=(300, 200))

        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        self.spinDia = wx.SpinCtrl(panel, min=1, max=31, initial=data_atual.day)
        self.spinMes = wx.SpinCtrl(panel, min=1, max=12, initial=data_atual.month)
        self.spinAno = wx.SpinCtrl(
            panel,
            min=2020,
            max=datetime.date.today().year + 2,
            initial=data_atual.year
        )

        grid = wx.FlexGridSizer(3, 2, 10, 10)
        grid.Add(wx.StaticText(panel, label="Dia"))
        grid.Add(self.spinDia)
        grid.Add(wx.StaticText(panel, label="Mês"))
        grid.Add(self.spinMes)
        grid.Add(wx.StaticText(panel, label="Ano"))
        grid.Add(self.spinAno)

        btnOk = wx.Button(panel, label="Confirmar")
        btnOk.Bind(wx.EVT_BUTTON, lambda e: self.EndModal(wx.ID_OK))

        sizer.Add(grid, 0, wx.ALL | wx.CENTER, 15)
        sizer.Add(btnOk, 0, wx.ALL | wx.CENTER, 10)

        panel.SetSizer(sizer)


class LiturgiaUI(wx.Frame):
    def __init__(self, frame_para_fechar=None):
        if frame_para_fechar:
            try:
                frame_para_fechar.Destroy()
            except Exception:
                pass

        super().__init__(None, title="Liturgia Diária", size=(800, 650))

        self.data_atual = datetime.date.today()
        self.liturgia = None

        panel = wx.Panel(self)
        mainSizer = wx.BoxSizer(wx.VERTICAL)

        btnSizer = wx.BoxSizer(wx.HORIZONTAL)

        btnData = wx.Button(panel, label="Selecionar Data")
        btnLeituras = wx.Button(panel, label="Leituras do Dia")
        btnOracoes = wx.Button(panel, label="Orações do Dia")
        btnAntifonas = wx.Button(panel, label="Antífonas")

        btnData.Bind(wx.EVT_BUTTON, self.selecionar_data)
        btnLeituras.Bind(wx.EVT_BUTTON, lambda e: self.mostrar_secao("leituras"))
        btnOracoes.Bind(wx.EVT_BUTTON, lambda e: self.mostrar_secao("oracoes"))
        btnAntifonas.Bind(wx.EVT_BUTTON, lambda e: self.mostrar_secao("antifonas"))

        for b in (btnData, btnLeituras, btnOracoes, btnAntifonas):
            btnSizer.Add(b, 0, wx.ALL, 5)

        mainSizer.Add(btnSizer, 0, wx.CENTER | wx.ALL, 10)

        infoBox = wx.StaticBox(panel, label="Informações")
        infoSizer = wx.StaticBoxSizer(infoBox, wx.VERTICAL)

        self.txtInfo = wx.TextCtrl(
            panel,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_WORDWRAP
        )

        infoSizer.Add(self.txtInfo, 1, wx.EXPAND | wx.ALL, 5)
        mainSizer.Add(infoSizer, 0, wx.EXPAND | wx.ALL, 10)

        self.scroll = wx.ScrolledWindow(panel, style=wx.VSCROLL)
        self.scroll.SetScrollRate(10, 10)
        scrollSizer = wx.BoxSizer(wx.VERTICAL)

        self.boxPrimeira = self._box(self.scroll, "Primeira Leitura")
        self.boxSalmo = self._box(self.scroll, "Salmo")
        self.boxSegunda = self._box(self.scroll, "Segunda Leitura")
        self.boxEvangelho = self._box(self.scroll, "Evangelho")

        self.boxOracaoDia = self._box(self.scroll, "Oração do Dia")
        self.boxOferendas = self._box(self.scroll, "Oferendas")
        self.boxPosComunhao = self._box(self.scroll, "Pós-Comunhão")

        self.boxAntEntrada = self._box(self.scroll, "Antífona de Entrada")
        self.boxAntOfertorio = self._box(self.scroll, "Antífona do Ofertório")
        self.boxAntComunhao = self._box(self.scroll, "Antífona da Comunhão")

        self.todos = [
            self.boxPrimeira, self.boxSalmo, self.boxSegunda, self.boxEvangelho,
            self.boxOracaoDia, self.boxOferendas, self.boxPosComunhao,
            self.boxAntEntrada, self.boxAntOfertorio, self.boxAntComunhao
        ]

        for box in self.todos:
            scrollSizer.Add(box, 0, wx.EXPAND | wx.ALL, 8)

        self.scroll.SetSizer(scrollSizer)
        mainSizer.Add(self.scroll, 1, wx.EXPAND | wx.ALL, 10)

        bottom = wx.BoxSizer(wx.HORIZONTAL)

        btnMenu = wx.Button(panel, label="Menu Principal")
        btnFechar = wx.Button(panel, label="Fechar")
        btnNota = wx.Button(panel, label="Criar Nota")

        btnMenu.Bind(wx.EVT_BUTTON, self.voltar_menu_principal)
        btnFechar.Bind(wx.EVT_BUTTON, lambda e: self.Destroy())
        btnNota.Bind(wx.EVT_BUTTON, self.criar_nota)

        bottom.Add(btnMenu, 0, wx.ALL, 10)
        bottom.Add(btnFechar, 0, wx.ALL, 10)
        bottom.Add(btnNota, 0, wx.ALL, 10)

        mainSizer.Add(bottom, 0, wx.CENTER)

        panel.SetSizer(mainSizer)

        self.buscar_liturgia()
        self.mostrar_secao("leituras")
        self.Show()

    def _box(self, parent, titulo):
        panel = wx.Panel(parent)
        box = wx.StaticBox(panel, label=titulo)
        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)

        txt = wx.TextCtrl(
            panel,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_WORDWRAP
        )

        sizer.Add(txt, 1, wx.EXPAND | wx.ALL, 5)
        panel.SetSizer(sizer)
        panel.txt = txt
        return panel

    def selecionar_data(self, event):
        dlg = SelecionarDataDialog(self, self.data_atual)
        if dlg.ShowModal() == wx.ID_OK:
            try:
                self.data_atual = datetime.date(
                    dlg.spinAno.GetValue(),
                    dlg.spinMes.GetValue(),
                    dlg.spinDia.GetValue()
                )
                self.buscar_liturgia()
            except ValueError:
                ui.message("Data inválida.")
        dlg.Destroy()

    def mostrar_secao(self, secao):
        for box in self.todos:
            box.Hide()

        if secao == "leituras":
            for b in (
                self.boxPrimeira,
                self.boxSalmo,
                self.boxSegunda,
                self.boxEvangelho
            ):
                b.Show()

        elif secao == "oracoes":
            for b in (
                self.boxOracaoDia,
                self.boxOferendas,
                self.boxPosComunhao
            ):
                b.Show()

        elif secao == "antifonas":
            self.boxAntEntrada.Show()
            self.boxAntComunhao.Show()

            if self.boxAntOfertorio.txt.GetValue().strip():
                self.boxAntOfertorio.Show()
            else:
                self.boxAntOfertorio.Hide()

        self.Layout()
        self.scroll.FitInside()

    def buscar_liturgia(self):
        self.liturgia = get_liturgia_by_date(self.data_atual)
        if not self.liturgia:
            ui.message("Liturgia não encontrada.")
            return

        l = self.liturgia

        self.txtInfo.SetValue(
            f"{l.get('data','')}\n"
            f"{l.get('liturgia','')}\n"
            f"Cor: {l.get('cor','')}"
        )

        p = l.get("primeiraLeitura", {})
        self.boxPrimeira.txt.SetValue(
            f"{p.get('referencia','')}\n\n"
            f"{p.get('titulo','')}\n\n"
            f"{p.get('texto','')}\n\n"
            f"Palavra do Senhor."
        )

        s = l.get("salmo", {})
        self.boxSalmo.txt.SetValue(
            f"{s.get('referencia','')}\n\n"
            f"Refrão: {s.get('refrao','')}\n\n"
            f"{s.get('texto','')}"
        )

        if isinstance(l.get("segundaLeitura"), dict):
            s2 = l["segundaLeitura"]
            self.boxSegunda.Show()
            self.boxSegunda.txt.SetValue(
                f"{s2.get('referencia','')}\n\n"
                f"{s2.get('titulo','')}\n\n"
                f"{s2.get('texto','')}\n\n"
                f"Palavra do Senhor."
            )
        else:
            self.boxSegunda.Hide()

        e = l.get("evangelho", {})
        self.boxEvangelho.txt.SetValue(
            f"{e.get('referencia','')}\n\n"
            f"{e.get('titulo','')}\n\n"
            f"{e.get('texto','')}\n\n"
            f"Palavra da Salvação."
        )

        self.boxOracaoDia.txt.SetValue(l.get("dia", ""))
        self.boxOferendas.txt.SetValue(l.get("oferendas", ""))
        self.boxPosComunhao.txt.SetValue(l.get("comunhao", ""))

        a = l.get("antifonas", {})
        self.boxAntEntrada.txt.SetValue(a.get("entrada", ""))

        if a.get("ofertorio"):
            self.boxAntOfertorio.Show()
            self.boxAntOfertorio.txt.SetValue(a["ofertorio"])
        else:
            self.boxAntOfertorio.Hide()

        self.boxAntComunhao.txt.SetValue(a.get("comunhao", ""))

        self.Layout()
        self.scroll.FitInside()

    def criar_nota(self, event):
        anotacoes.NotasManager(
            versao=None,
            livro=None,
            capitulo=None,
            versiculos=None,
            pluginRef=self,
            origem="liturgia"
        )

    def voltar_menu_principal(self, event):
        self.Destroy()
        menu = GlobalPlugin()
        wx.CallAfter(menu.exibirMenu)
