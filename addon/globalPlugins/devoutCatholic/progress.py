import os
import json
from datetime import datetime


class ReadingProgressManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ReadingProgressManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.file_path = os.path.join(os.path.dirname(__file__), "dados", "progresso_leitura.json")
        self._progress_cache = None
        self._load_from_disk()

    def _load_from_disk(self):
        try:
            if os.path.exists(self.file_path):
                with open(self.file_path, "r", encoding="utf-8") as f:
                    self._progress_cache = json.load(f)
            else:
                self._progress_cache = None
        except Exception:
            self._progress_cache = None

    def _save_to_disk(self):
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self._progress_cache, f, ensure_ascii=False, indent=2)
        except Exception:
            # Falha silenciosa para não quebrar a UX no NVDA
            pass

    def get_progress(self):
        return self._progress_cache

    def update_progress(self, versao, livro, capitulo, versiculo):
        self._progress_cache = {
            "versao": versao,
            "livro": livro,
            "capitulo": capitulo,
            "versiculo": versiculo,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self._save_to_disk()


