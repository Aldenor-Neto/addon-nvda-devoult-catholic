import wx
import json
import os
import ui
import unicodedata
import globalPluginHandler


class CatecismoUI:
    def __init__(self):
        self.data = []
        self.sections = []

        self.carregar_dados()

    # =========================
    # UTIL
    # =========================
    def normalize(self, s):
        return unicodedata.normalize('NFD', s.lower()).encode('ascii', 'ignore').decode('utf-8')

    def carregar_dados(self):
        caminho = os.path.join(os.path.dirname(__file__), "dados", "catecismo.json")
        with open(caminho, "r", encoding="utf-8") as f:
            self.data = json.load(f)

        self.processar_estrutura(self.data)

    # =========================
    # PROCESSAMENTO
    # =========================
    def processar_estrutura(self, dados):
        SECTION_KEYS = [
            'PRÓLOGO',
            'PARTE 1: A PROFISSÃO DA FÉ',
            'PARTE II: OS SACRAMENTOS DE FÉ',
            'PARTE III: A VIDA DA FÉ',
            'PARTE IV: A ORAÇÃO NA VIDA DA FÉ',
        ]

        sections = []
        current_section = None
        current_sub = None

        for item in dados:
            texto = item["texto"].strip()
            tipo = item["tipo"].lower()

            if tipo == "titulo" and texto in SECTION_KEYS:
                current_section = {"title": texto, "content": []}
                sections.append(current_section)
                current_sub = None
                continue

            if not current_section:
                continue

            if "sub" in tipo:
                current_sub = {"title": texto, "content": []}
                current_section["content"].append({"type": "sub", "node": current_sub})
                continue

            if tipo in ["capitulo", "artigo", "titulo"]:
                node = {"type": "highlight", "text": texto}
            else:
                node = {"type": "text", "text": texto}

            if current_sub:
                current_sub["content"].append(node)
            else:
                current_section["content"].append(node)

        self.sections = sections

    # =========================
    # 🔥 FUNÇÃO PARA BUSCA (CORRETA)
    # =========================
    def pegar_ate_fim_paragrafos(self, grupo):
        resultado = []

        for item in grupo:
            tipo = item["tipo"].lower()

            if tipo not in ["paragrafo", "texto"]:
                break

            resultado.append({"text": item["texto"]})

        return resultado

    # =========================
    # 🔥 VOLTAR PARA MENU DO ADDON
    # =========================
    def voltar_menu_principal_app(self, frame):
        frame.Destroy()

        for plugin in globalPluginHandler.runningPlugins:
            if hasattr(plugin, "exibirMenu"):
                wx.CallLater(100, plugin.exibirMenu)
                break

    # =========================
    # UI PRINCIPAL
    # =========================
    def show(self):
        self.menu_principal()

    def menu_principal(self):
        frame = wx.Frame(None, title="Catecismo da Igreja Católica - CIC", size=(450, 500))
        panel = wx.Panel(frame)

        sizer = wx.BoxSizer(wx.VERTICAL)

        titulo = wx.StaticText(panel, label="Catecismo da Igreja Católica - CIC")
        fonte = titulo.GetFont()
        fonte.PointSize += 3
        fonte = fonte.Bold()
        titulo.SetFont(fonte)

        sizer.Add(titulo, 0, wx.ALL | wx.CENTER, 10)

        btn_buscar = wx.Button(panel, label="Buscar")
        sizer.Add(btn_buscar, 0, wx.EXPAND | wx.ALL, 10)

        for secao in self.sections:
            btn = wx.Button(panel, label=secao["title"])
            btn.Bind(wx.EVT_BUTTON, lambda e, s=secao: (frame.Destroy(), self.exibir_secao(s)))
            sizer.Add(btn, 0, wx.EXPAND | wx.ALL, 5)

        btn_voltar = wx.Button(panel, label="Voltar ao Menu Principal")
        sizer.Add(btn_voltar, 0, wx.EXPAND | wx.ALL, 10)

        panel.SetSizer(sizer)

        btn_buscar.Bind(wx.EVT_BUTTON, lambda e: (frame.Destroy(), self.abrir_busca()))

        # 🔥 AQUI ESTÁ A CORREÇÃO
        btn_voltar.Bind(wx.EVT_BUTTON, lambda e: self.voltar_menu_principal_app(frame))

        frame.Show()

    # =========================
    # EXIBIR SEÇÃO
    # =========================
    def exibir_secao(self, secao):
        frame = wx.Frame(None, title=secao["title"], size=(500, 500))
        panel = wx.Panel(frame)

        sizer = wx.BoxSizer(wx.VERTICAL)

        conteudo = secao["content"]

        for i, item in enumerate(conteudo):
            if item["type"] == "sub":
                titulo = item["node"]["title"]
                btn = wx.Button(panel, label=titulo)
                btn.Bind(wx.EVT_BUTTON, lambda e, n=item["node"]: (frame.Destroy(), self.exibir_sub(n)))
            else:
                texto = item["text"][:60]
                btn = wx.Button(panel, label=texto)
                btn.Bind(wx.EVT_BUTTON, lambda e, c=conteudo[i:]: self.exibir_texto(c))

            sizer.Add(btn, 0, wx.EXPAND | wx.ALL, 5)

        btn_voltar = wx.Button(panel, label="Voltar")
        btn_voltar.Bind(wx.EVT_BUTTON, lambda e: (frame.Destroy(), self.menu_principal()))

        sizer.Add(btn_voltar, 0, wx.EXPAND | wx.ALL, 10)

        panel.SetSizer(sizer)
        frame.Show()

    # =========================
    # SUBSEÇÃO
    # =========================
    def exibir_sub(self, sub):
        frame = wx.Frame(None, title=sub["title"], size=(500, 500))
        panel = wx.Panel(frame)

        sizer = wx.BoxSizer(wx.VERTICAL)

        conteudo = sub["content"]

        for i, item in enumerate(conteudo):
            texto = item["text"][:60]
            btn = wx.Button(panel, label=texto)
            btn.Bind(wx.EVT_BUTTON, lambda e, c=conteudo[i:]: self.exibir_texto(c))
            sizer.Add(btn, 0, wx.EXPAND | wx.ALL, 5)

        btn_voltar = wx.Button(panel, label="Voltar")
        btn_voltar.Bind(wx.EVT_BUTTON, lambda e: (frame.Destroy(), self.menu_principal()))

        sizer.Add(btn_voltar, 0, wx.EXPAND | wx.ALL, 10)

        panel.SetSizer(sizer)
        frame.Show()

    # =========================
    # TEXTO
    # =========================
    def exibir_texto(self, conteudos, titulo="Leitura"):
        texto = "\n\n".join([c["text"] for c in conteudos if "text" in c])

        frame = wx.Frame(None, title=titulo, size=(600, 500))
        panel = wx.Panel(frame)

        txt = wx.TextCtrl(
            panel,
            value=texto,
            style=wx.TE_MULTILINE | wx.TE_READONLY
        )

        txt.SetFocus()

        btn_fechar = wx.Button(panel, label="Fechar leitura")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(txt, 1, wx.EXPAND | wx.ALL, 10)
        sizer.Add(btn_fechar, 0, wx.EXPAND | wx.ALL, 10)

        btn_fechar.Bind(wx.EVT_BUTTON, lambda e: frame.Destroy())

        panel.SetSizer(sizer)
        frame.Show()

    # =========================
    # BUSCA
    # =========================
    def abrir_busca(self):
        frame = wx.Frame(None, title="Buscar no Catecismo", size=(500, 500))
        panel = wx.Panel(frame)

        sizer = wx.BoxSizer(wx.VERTICAL)

        txt_busca = wx.TextCtrl(panel)
        btn_buscar = wx.Button(panel, label="Buscar")

        resultados_sizer = wx.BoxSizer(wx.VERTICAL)

        btn_voltar = wx.Button(panel, label="Voltar")

        sizer.Add(txt_busca, 0, wx.EXPAND | wx.ALL, 10)
        sizer.Add(btn_buscar, 0, wx.ALL, 10)
        sizer.Add(resultados_sizer, 1, wx.EXPAND | wx.ALL, 10)
        sizer.Add(btn_voltar, 0, wx.EXPAND | wx.ALL, 10)

        panel.SetSizer(sizer)

        def executar_busca(event):
            termo = self.normalize(txt_busca.GetValue())

            for child in resultados_sizer.GetChildren():
                child.GetWindow().Destroy()

            encontrados = []

            for i, item in enumerate(self.data):
                if termo in self.normalize(item["texto"]):
                    encontrados.append(self.data[i:])

            for grupo in encontrados:
                btn = wx.Button(panel, label=grupo[0]["texto"][:80])

                btn.Bind(
                    wx.EVT_BUTTON,
                    lambda e, g=grupo: self.exibir_texto(self.pegar_ate_fim_paragrafos(g))
                )

                resultados_sizer.Add(btn, 0, wx.EXPAND | wx.ALL, 5)

            panel.Layout()
            ui.message(f"{len(encontrados)} resultados encontrados")

        btn_buscar.Bind(wx.EVT_BUTTON, executar_busca)
        btn_voltar.Bind(wx.EVT_BUTTON, lambda e: (frame.Destroy(), self.menu_principal()))

        frame.Show()
        txt_busca.SetFocus()