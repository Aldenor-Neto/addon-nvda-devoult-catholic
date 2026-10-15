import wx
import json
import os
import ui
import random

from .__init__ import GlobalPlugin


class Motivacional:
    def __init__(self):
        self.frame = None
        self.txtMeditacao = None

        self.meditacoes = []
        self.carregar_dados()

    # =========================
    # EXIBIR TELA
    # =========================
    def show(self):
        self.frame = wx.Frame(None, title="Motivacional", size=(700, 600))

        panel = wx.Panel(self.frame)
        mainSizer = wx.BoxSizer(wx.VERTICAL)

        # ===== TÍTULO =====
        titulo = wx.StaticText(panel, label="Meditação")
        mainSizer.Add(titulo, 0, wx.ALL | wx.CENTER, 10)

        # ===== TEXTO =====
        self.txtMeditacao = wx.TextCtrl(
            panel,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_WORDWRAP
        )

        mainSizer.Add(self.txtMeditacao, 1, wx.EXPAND | wx.ALL, 10)

        # ===== BOTÕES =====
        btnSizer = wx.BoxSizer(wx.HORIZONTAL)

        btnNova = wx.Button(panel, label="Gerar Nova Meditação")
        btnMenu = wx.Button(panel, label="Menu Principal")
        btnFechar = wx.Button(panel, label="Fechar")

        btnSizer.Add(btnNova, 0, wx.ALL, 5)
        btnSizer.Add(btnMenu, 0, wx.ALL, 5)
        btnSizer.Add(btnFechar, 0, wx.ALL, 5)

        mainSizer.Add(btnSizer, 0, wx.CENTER)

        panel.SetSizer(mainSizer)

        # ===== BINDS =====
        btnNova.Bind(wx.EVT_BUTTON, self.gerar_nova_meditacao)
        btnMenu.Bind(wx.EVT_BUTTON, self.voltar_menu)
        btnFechar.Bind(wx.EVT_BUTTON, lambda e: self.frame.Destroy())

        # 🔥 SEMPRE GERA NOVA AO ABRIR (SEM CACHE)
        wx.CallAfter(self.gerar_meditacao_inicial)

        self.frame.Show()

    # =========================
    # CARREGAR JSON
    # =========================
    def carregar_dados(self):
        caminho = os.path.join(
            os.path.dirname(__file__), "dados", "motivacional.json"
        )

        try:
            with open(caminho, "r", encoding="utf-8") as f:
                self.meditacoes = json.load(f)
        except Exception as e:
            wx.MessageBox(f"Erro ao carregar meditações: {e}", "Erro")

    # =========================
    # GERAR ALEATÓRIA
    # =========================
    def gerar_meditacao(self):
        if not self.meditacoes:
            return {
                "titulo": "Erro",
                "descricao": "Nenhuma meditação disponível."
            }

        return random.choice(self.meditacoes)

    # =========================
    # AO ABRIR
    # =========================
    def gerar_meditacao_inicial(self):
        med = self.gerar_meditacao()
        self.mostrar_meditacao(med)

    # =========================
    # BOTÃO NOVA
    # =========================
    def gerar_nova_meditacao(self, event):
        med = self.gerar_meditacao()
        self.mostrar_meditacao(med)

        ui.message("Nova meditação gerada")

    # =========================
    # EXIBIR
    # =========================
    def mostrar_meditacao(self, med):
        texto = f"{med.get('titulo','')}\n\n{med.get('descricao','')}"
        self.txtMeditacao.SetValue(texto)
        self.txtMeditacao.SetFocus()

        ui.message(med.get("titulo", "Meditação"))

    # =========================
    # VOLTAR MENU
    # =========================
    def voltar_menu(self, event):
        self.frame.Destroy()

        menu = GlobalPlugin()
        wx.CallAfter(menu.exibirMenu)