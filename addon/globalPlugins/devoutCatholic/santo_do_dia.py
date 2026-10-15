import wx
import json
import os
import ui
import datetime

from .__init__ import GlobalPlugin


# =========================
# DIALOG DE DATA (IGUAL LITURGIA)
# =========================
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


# =========================
# UI PRINCIPAL
# =========================
class SantoDoDiaUI:
    def __init__(self):
        self.santos = []
        self.data_atual = datetime.date.today()
        self.txtResultado = None

        self.carregar_dados()

    # =========================
    def carregar_dados(self):
        caminho = os.path.join(os.path.dirname(__file__), "dados", "santos.json")

        try:
            with open(caminho, "r", encoding="utf-8") as f:
                self.santos = json.load(f)
        except Exception as e:
            wx.MessageBox(f"Erro ao carregar santos: {e}", "Erro")

    def formatar_data(self, data):
        return data.strftime("%d/%m")

    # =========================
    def show(self):
        self.menu()

    def menu(self):
        frame = wx.Frame(None, title="Santo do Dia", size=(700, 600))
        panel = wx.Panel(frame)

        sizer = wx.BoxSizer(wx.VERTICAL)

        # ===== BOTÕES SUPERIORES =====
        btnSizer = wx.BoxSizer(wx.HORIZONTAL)

        btnBuscar = wx.Button(panel, label="Buscar Santo")
        btnData = wx.Button(panel, label="Selecionar Data")

        btnSizer.Add(btnBuscar, 0, wx.ALL, 5)
        btnSizer.Add(btnData, 0, wx.ALL, 5)

        sizer.Add(btnSizer, 0, wx.CENTER | wx.ALL, 10)

        # ===== ÁREA DE TEXTO (IGUAL LITURGIA) =====
        self.txtResultado = wx.TextCtrl(
            panel,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_WORDWRAP
        )

        sizer.Add(self.txtResultado, 1, wx.EXPAND | wx.ALL, 10)

        # ===== BOTÕES INFERIORES =====
        bottom = wx.BoxSizer(wx.HORIZONTAL)

        btnVoltar = wx.Button(panel, label="Menu Principal")
        btnFechar = wx.Button(panel, label="Fechar")

        bottom.Add(btnVoltar, 0, wx.ALL, 10)
        bottom.Add(btnFechar, 0, wx.ALL, 10)

        sizer.Add(bottom, 0, wx.CENTER)

        panel.SetSizer(sizer)

        # =========================
        # FUNÇÃO MOSTRAR TEXTO
        # =========================
        def mostrar_texto(santo):
            texto = f"{santo['nome']}\n\n{santo['descricao']}"
            self.txtResultado.SetValue(texto)
            self.txtResultado.SetFocus()
            ui.message(santo["nome"])

        # =========================
        # BUSCAR SANTO (JANELA)
        # =========================
        def abrir_busca(event):
            dlg = wx.Dialog(frame, title="Buscar Santo", size=(400, 200))
            p = wx.Panel(dlg)
            sz = wx.BoxSizer(wx.VERTICAL)

            lbl = wx.StaticText(p, label="Digite o nome do santo")
            txt = wx.TextCtrl(p)
            btn = wx.Button(p, label="Buscar")

            sz.Add(lbl, 0, wx.ALL, 10)
            sz.Add(txt, 0, wx.EXPAND | wx.ALL, 10)
            sz.Add(btn, 0, wx.ALL | wx.CENTER, 10)

            p.SetSizer(sz)

            def executar_busca(e):
                termo = txt.GetValue().lower().strip()

                if not termo:
                    ui.message("Digite um nome")
                    return

                encontrados = [
                    s for s in self.santos
                    if termo in s["nome"].lower()
                ]

                dlg.Destroy()
                self.exibir_resultados(encontrados, frame, mostrar_texto)

            btn.Bind(wx.EVT_BUTTON, executar_busca)

            dlg.ShowModal()

        # =========================
        # SELECIONAR DATA (IGUAL LITURGIA)
        # =========================
        def selecionar_data(event):
            dlg = SelecionarDataDialog(frame, self.data_atual)

            if dlg.ShowModal() == wx.ID_OK:
                try:
                    self.data_atual = datetime.date(
                        dlg.spinAno.GetValue(),
                        dlg.spinMes.GetValue(),
                        dlg.spinDia.GetValue()
                    )

                    data_formatada = self.formatar_data(self.data_atual)

                    encontrados = [
                        s for s in self.santos
                        if s["data"] == data_formatada
                    ]

                    self.exibir_resultados(encontrados, frame, mostrar_texto)

                except ValueError:
                    ui.message("Data inválida.")

            dlg.Destroy()

        # =========================
        # BINDS
        # =========================
        btnBuscar.Bind(wx.EVT_BUTTON, abrir_busca)
        btnData.Bind(wx.EVT_BUTTON, selecionar_data)

        btnVoltar.Bind(wx.EVT_BUTTON, lambda e: self.voltar_menu(frame))
        btnFechar.Bind(wx.EVT_BUTTON, lambda e: frame.Destroy())

        # =========================
        # CARREGA AUTOMATICO (HOJE)
        # =========================
        def carregar_hoje():
            hoje = self.formatar_data(self.data_atual)

            encontrados = [
                s for s in self.santos
                if s["data"] == hoje
            ]

            self.exibir_resultados(encontrados, frame, mostrar_texto)

        wx.CallAfter(carregar_hoje)

        frame.Show()

    # =========================
    # RESULTADOS
    # =========================
    def exibir_resultados(self, encontrados, frame, callback):
        if not encontrados:
            self.txtResultado.SetValue("")
            ui.message("Nenhum santo encontrado")
            return

        # 🔥 Se for só 1
        if len(encontrados) == 1:
            callback(encontrados[0])
            return

        # 🔥 Se vários → janela de escolha
        dlg = wx.Dialog(frame, title="Escolher Santo", size=(400, 400))
        panel = wx.Panel(dlg)
        sizer = wx.BoxSizer(wx.VERTICAL)

        for santo in encontrados:
            btn = wx.Button(panel, label=santo["nome"])
            btn.Bind(wx.EVT_BUTTON, lambda e, s=santo: (dlg.Destroy(), callback(s)))
            sizer.Add(btn, 0, wx.EXPAND | wx.ALL, 5)

        panel.SetSizer(sizer)

        ui.message(f"{len(encontrados)} santos encontrados")
        dlg.ShowModal()

    # =========================
    def voltar_menu(self, frame):
        menu = GlobalPlugin()
        menu.exibirMenu()
        frame.Destroy()