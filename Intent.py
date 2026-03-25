import re
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass
class ParsedIntent:
    raw_text: str
    action: str
    target: str
    keywords: List[str]
    parameters: Dict[str, Any]
    category: Optional[str] = None


class IntentParser:
    def __init__(self):
        # Python'da regex kalıplarını hız için önceden derliyoruz (re.I = re.IGNORECASE)
        self.action_patterns: Dict[str, List[re.Pattern]] = {
            'read': [re.compile(r'read', re.I), re.compile(r'get', re.I), re.compile(r'fetch', re.I), re.compile(r'load', re.I), re.compile(r'open', re.I), re.compile(r'view', re.I), re.compile(r'oku', re.I), re.compile(r'getir', re.I), re.compile(r'öğren', re.I), re.compile(r'göster', re.I)],
            'write': [re.compile(r'write', re.I), re.compile(r'save', re.I), re.compile(r'create', re.I), re.compile(r'store', re.I), re.compile(r'put', re.I), re.compile(r'yaz', re.I), re.compile(r'oluştur', re.I), re.compile(r'ekle', re.I), re.compile(r'kaydet', re.I)],
            'search': [re.compile(r'search', re.I), re.compile(r'find', re.I), re.compile(r'look for', re.I), re.compile(r'query', re.I), re.compile(r'ara', re.I), re.compile(r'bul', re.I), re.compile(r'sorgula', re.I)],
            'delete': [re.compile(r'delete', re.I), re.compile(r'remove', re.I), re.compile(r'erase', re.I), re.compile(r'sil', re.I), re.compile(r'kaldır', re.I)],
            'execute': [re.compile(r'run', re.I), re.compile(r'execute', re.I), re.compile(r'invoke', re.I), re.compile(r'call', re.I), re.compile(r'çalıştır', re.I), re.compile(r'hesapla', re.I), re.compile(r'üret', re.I), re.compile(r'çiz', re.I)],
            'send': [re.compile(r'send', re.I), re.compile(r'gönder', re.I), re.compile(r'ilet', re.I), re.compile(r'mesaj at', re.I), re.compile(r'mail at', re.I)],
            'track': [re.compile(r'track', re.I), re.compile(r'takip et', re.I), re.compile(r'nerede', re.I)],
            'translate': [re.compile(r'translate', re.I), re.compile(r'çevir', re.I), re.compile(r'tercüme et', re.I)],
            'set': [re.compile(r'set', re.I), re.compile(r'kur', re.I), re.compile(r'ayarla', re.I)]
        }

        self.target_patterns: Dict[str, List[re.Pattern]] = {
            'file': [re.compile(r'file', re.I), re.compile(r'document', re.I), re.compile(r'\.txt', re.I), re.compile(r'\.json', re.I), re.compile(r'\.md', re.I), re.compile(r'belge', re.I), re.compile(r'dosya', re.I), re.compile(r'pdf', re.I)],
            'database': [re.compile(r'database', re.I), re.compile(r'\bdb\b', re.I), re.compile(r'table', re.I), re.compile(r'record', re.I), re.compile(r'veritabanı', re.I), re.compile(r'veri', re.I), re.compile(r'sorgu', re.I)],
            'network': [re.compile(r'api', re.I), re.compile(r'endpoint', re.I), re.compile(r'http', re.I), re.compile(r'url', re.I), re.compile(r'web', re.I), re.compile(r'internet', re.I), re.compile(r'arama', re.I)],
            'code': [re.compile(r'code', re.I), re.compile(r'script', re.I), re.compile(r'function', re.I), re.compile(r'program', re.I), re.compile(r'python', re.I), re.compile(r'sql', re.I), re.compile(r'hesap', re.I), re.compile(r'matematik', re.I)],
            'service': [re.compile(r'weather', re.I), re.compile(r'hava', re.I), re.compile(r'sıcaklık', re.I), re.compile(r'iklim', re.I)],
            'finance': [re.compile(r'stock', re.I), re.compile(r'hisse', re.I), re.compile(r'borsa', re.I), re.compile(r'fiyat', re.I), re.compile(r'currency', re.I), re.compile(r'\bkur\b', re.I), re.compile(r'dolar', re.I), re.compile(r'euro', re.I), re.compile(r'kripto', re.I), re.compile(r'bitcoin', re.I), re.compile(r'para', re.I)],
            'productivity': [re.compile(r'task', re.I), re.compile(r'todo', re.I), re.compile(r'görev', re.I), re.compile(r'calendar', re.I), re.compile(r'takvim', re.I), re.compile(r'toplantı', re.I), re.compile(r'randevu', re.I), re.compile(r'etkinlik', re.I), re.compile(r'timer', re.I), re.compile(r'alarm', re.I), re.compile(r'hatırlatıcı', re.I), re.compile(r'süre', re.I)],
            'media': [re.compile(r'image', re.I), re.compile(r'görsel', re.I), re.compile(r'resim', re.I), re.compile(r'fotoğraf', re.I), re.compile(r'çizim', re.I)],
            'communication': [re.compile(r'slack', re.I), re.compile(r'email', re.I), re.compile(r'mail', re.I), re.compile(r'mesaj', re.I), re.compile(r'eposta', re.I), re.compile(r'ileti', re.I)],
            'logistics': [re.compile(r'package', re.I), re.compile(r'kargo', re.I), re.compile(r'kurye', re.I), re.compile(r'paket', re.I), re.compile(r'takip', re.I)],
            'language': [re.compile(r'language', re.I), re.compile(r'\bdil\b', re.I), re.compile(r'metin', re.I), re.compile(r'text', re.I), re.compile(r'çeviri', re.I), re.compile(r'tercüme', re.I)]
        }

    def parse(self, text: str) -> ParsedIntent:
        """parse the text"""
        action = self._detect_action(text)
        target = self._detect_target(text)
        
        intent = ParsedIntent(
            raw_text=text,
            action=action,
            target=target,
            keywords=self._extract_keywords(text),
            parameters=self._extract_parameters(text)
        )

        # Action ve target üzerinden kategoriyi belirle
        intent.category = self._infer_category(intent)

        return intent

    def _detect_action(self, text: str) -> str:
        for action, patterns in self.action_patterns.items():
            if any(pattern.search(text) for pattern in patterns):
                return action
        return 'unknown'

    def _detect_target(self, text: str) -> str:
        for target, patterns in self.target_patterns.items():
            if any(pattern.search(text) for pattern in patterns):
                return target
        return 'unknown'

    def _extract_keywords(self, text: str) -> List[str]:
        # Sık kullanılan kelimeleri (stop words) çıkar ve anlamlı terimleri al
        stop_words = {'the', 'a', 'an', 'to', 'from', 'in', 'on', 'at', 'for', 'of', 'and', 'or', 'is', 'it'}
        
        words = re.split(r'\s+', text.lower())
        return [word for word in words if len(word) > 2 and word not in stop_words]

    def _extract_parameters(self, text: str) -> Dict[str, Any]:
        params: Dict[str, Any] = {}

        # Dosya yollarını çıkar
        path_match = re.search(r'["\']?([\/\w\-\.]+\.\w+)["\']?', text)
        if path_match:
            params['file_path'] = path_match.group(1)

        # URL'leri çıkar
        url_match = re.search(r'(https?://[^\s]+)', text)
        if url_match:
            params['url'] = url_match.group(1)

        # Sayıları çıkar
        number_match = re.search(r'\b(\d+)\b', text)
        if number_match:
            params['number'] = int(number_match.group(1))

        return params

    def _infer_category(self, intent: ParsedIntent) -> str:
        category_map: Dict[str, str] = {
            'file': 'document',
            'database': 'data',
            'network': 'network',
            'code': 'execution',
            'service': 'service',
            'finance': 'finance',
            'productivity': 'productivity',
            'media': 'media',
            'communication': 'communication',
            'logistics': 'logistics',
            'language': 'language'
        }
        # Sözlükte eşleşme yoksa 'general' döner
        return category_map.get(intent.target, 'general')