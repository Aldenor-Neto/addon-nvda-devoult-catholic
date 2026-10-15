import wx
import os
import json
import ui


class BuscaBiblica:
    def __init__(
        self,
        parent,
        termo,
        json_files,
        versoes_selecionadas,
        abrir_callback,
        voltar_callback
    ):
        self.parent = parent
        self.termo = termo.lower()
        self.json_files = json_files
        self.versoes_selecionadas = versoes_selecionadas
        self.abrir_callback = abrir_callback
        self.voltar_callback = voltar_callback
        self.resultados = []

        self.executar()

    def executar(self):
        total = self._calcularTotalVersiculos()
        if total == 0:
            ui.message("Nenhum conteúdo disponível para busca.")
            return

        progresso_frame = wx.Frame(None, title="Busca Bíblica", size=(400, 100))
        panel = wx.Panel(progresso_frame)
        sizer = wx.BoxSizer(wx.VERTICAL)
        gauge = wx.Gauge(panel, range=100, size=(350, 25))
        sizer.Add(wx.StaticText(panel, label="Buscando na Bíblia..."), 0, wx.ALL, 10)
        sizer.Add(gauge, 0, wx.ALL | wx.EXPAND, 10)
        panel.SetSizer(sizer)
        progresso_frame.Show()
        wx.YieldIfNeeded()

        try:
            passo_atual = 0
            base = os.path.join(os.path.dirname(__file__), "dados", "versions")

            for versao in self.versoes_selecionadas:
                arquivo = self.json_files.get(versao)
                if not arquivo:
                    continue

                caminho = os.path.join(base, arquivo)
                try:
                    with open(caminho, "r", encoding="utf-8-sig") as f:
                        biblia = json.load(f)

                    for livro in biblia:
                        for c_idx, cap in enumerate(livro.get("chapters", [])):
                            for v_idx, vers in enumerate(cap):
                                passo_atual += 1
                                porcentagem = int((passo_atual / total) * 100)
                                wx.CallAfter(gauge.SetValue, porcentagem)
                                wx.YieldIfNeeded()

                                if self.termo in vers.lower():
                                    self.resultados.append({
                                        "versao": versao,
                                        "livro": livro.get("name", ""),
                                        "capitulo": c_idx,
                                        "versiculo": v_idx,
                                        "texto": vers
                                    })

                except Exception:
                    pass
        finally:
            progresso_frame.Destroy()

        if not self.resultados:
            dlg = wx.MessageDialog(
                self.parent if self.parent else None,
                "Nenhum resultado encontrado.",
                "Busca Bíblica",
                wx.OK | wx.ICON_INFORMATION
            )
            dlg.ShowModal()
            dlg.Destroy()
            return

        if self.parent:
            try:
                self.parent.Destroy()
            except Exception:
                pass

        self.exibirResultados(self.resultados)

    def _calcularTotalVersiculos(self):
        total = 0
        base = os.path.join(os.path.dirname(__file__), "dados", "versions")
        for versao in self.versoes_selecionadas:
            arquivo = self.json_files.get(versao)
            if not arquivo:
                continue
            caminho = os.path.join(base, arquivo)
            try:
                with open(caminho, "r", encoding="utf-8-sig") as f:
                    biblia = json.load(f)
                for livro in biblia:
                    for cap in livro.get("chapters", []):
                        total += len(cap)
            except Exception:
                pass
        return total

    def exibirResultados(self, resultados):
        frame = wx.Frame(None, title="Resultados da Busca", size=(650, 400))
        panel = wx.Panel(frame)

        sizer = wx.BoxSizer(wx.VERTICAL)

        qtd = len(resultados)
        texto_topo = wx.StaticText(
            panel,
            label=(f"{qtd} resultado{'s' if qtd > 1 else ''} "
                   f"encontrado{'s' if qtd > 1 else ''} para a busca \"{self.termo}\"")
        )
        sizer.Add(texto_topo, 0, wx.ALL, 10)

        lista = wx.ListBox(panel)
        for i, r in enumerate(resultados, start=1):
            lista.Append(
                f"{i}. {r['versao']} - {r['livro']} "
                f"{r['capitulo'] + 1}:{r['versiculo'] + 1} - {r['texto']}"
            )
        sizer.Add(lista, 1, wx.EXPAND | wx.ALL, 10)

        btn_abrir = wx.Button(panel, label="Abrir")
        btn_voltar = wx.Button(panel, label="Voltar ao Menu Bíblia")
        sizer.Add(btn_abrir, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        sizer.Add(btn_voltar, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        panel.SetSizer(sizer)

        def abrir(event):
            idx = lista.GetSelection()
            if idx == wx.NOT_FOUND:
                ui.message("Nenhum resultado selecionado.")
                return
            self.abrir_callback(resultados[idx])
            frame.Destroy()

        def voltar(event):
            frame.Destroy()
            if self.voltar_callback:
                wx.CallAfter(self.voltar_callback)

        btn_abrir.Bind(wx.EVT_BUTTON, abrir)
        btn_voltar.Bind(wx.EVT_BUTTON, voltar)

        frame.Show()
        lista.SetFocus()

