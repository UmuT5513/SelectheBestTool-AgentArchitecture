# BestToolSelection

Kullanıcı sorgularını analiz ederek en uygun aracı (tool) seçen akıllı bir pipeline sistemi. **Keyword eşleştirme**, **intent parsing** ve **semantic search** stratejilerini bir arada kullanır.

## 🏗️ Mimari

```
Kullanıcı Sorgusu
       │
       ▼
 ┌─────────────┐
 │ IntentParser │  → Aksiyon, hedef, anahtar kelime, parametre çıkarımı
 └──────┬──────┘
        │
        ▼
 ┌──────────────────┐
 │  Candidate Pool   │  → Kategori + Keyword + Semantic Search ile aday toplama
 └──────┬───────────┘
        │
        ▼
 ┌──────────────────┐
 │CapabilityScorer   │  → Exact/Partial/Category/Description/Semantic skorlama
 └──────┬───────────┘
        │
        ▼
 ┌──────────────────┐
 │ParameterValidator │  → Parametre doğrulama (tip, enum, regex, zorunluluk)
 └──────┬───────────┘
        │
        ▼
 ┌──────────────────┐
 │ FallbackHandler   │  → Düşük güven durumunda yedek plan ve açıklama isteme
 └──────────────────┘
```

## 📁 Dosya Yapısı

| Dosya | Açıklama |
|---|---|
| `Tool.py` | `ToolSchema`, `ToolParameter` ve `ToolRegistry` tanımları |
| `ToolAutoLoader.py` | `tools/` dizinindeki tool'ları otomatik keşfedip yükleyen modül |
| `Intent.py` | Kullanıcı sorgusundan aksiyon, hedef ve parametre çıkarımı |
| `Score.py` | Keyword + semantic benzerlik tabanlı puanlama motoru |
| `SemanticSearch.py` | ChromaDB + OpenAI embedding ile vektörel anlamsal arama |
| `Selector.py` | Tüm bileşenleri birleştiren ana seçim orchestrator'ı |
| `Validate.py` | Parametre tip, enum ve regex doğrulama |
| `Fallback.py` | Düşük güven senaryolarında yedek plan yönetimi |
| `main.py` | Demo ve test senaryoları |
| `tools/` | Otomatik yüklenen tool tanım dosyaları dizini |

### `tools/` Dizini — Kayıtlı Tool'lar

| Dosya | Tool Adı | Açıklama |
|---|---|---|
| `weather.py` | `weather` | Lokasyon bazlı hava durumu sorgulama |
| `code_executor.py` | `code_executor` | Python ile matematiksel hesaplama |
| `web_search.py` | `web_search` | İnternet arama motoru |
| `currency_converter.py` | `currency_converter` | Döviz / Kripto para dönüşümü |
| `calendar_manager.py` | `calendar_manager` | Takvim etkinlik yönetimi |
| `database_query.py` | `database_query` | SQL veritabanı sorgulama |
| `document_reader.py` | `document_reader` | PDF/TXT belge okuyucu |
| `translator.py` | `translator` | Metin çeviri servisi |
| `email_sender.py` | `email_sender` | E-posta gönderme simülasyonu |
| `timer.py` | `timer` | Zamanlayıcı / hatırlatıcı |

## 🔌 Yeni Tool Ekleme

Sisteme yeni bir tool eklemek için `tools/` dizinine bir `.py` dosyası oluşturun. `ToolAutoLoader` dosyayı otomatik keşfeder ve kaydeder.

### Convention

Her tool modülü, modül seviyesinde bir `TOOL_DEFINITIONS` listesi export etmelidir:

```python
from Tool import ToolSchema, ToolParameter

my_tool = ToolSchema(
    name='my_tool',
    description='Tool açıklaması',
    category='category_name',
    parameters=[
        ToolParameter(name='param1', type='string', description='...', required=True)
    ],
    returns={'type': 'string', 'description': '...'},
    examples=[{'input': {'param1': 'value'}, 'description': 'Örnek kullanım'}],
    capabilities=['keyword1', 'keyword2']
)

TOOL_DEFINITIONS = [my_tool]
```

> **Not:** `TOOL_DEFINITIONS` listesi birden fazla `ToolSchema` içerebilir — tek dosyada birden fazla tool tanımlanabilir.

## 🔍 Strateji Katmanları

### 1. Intent Parsing
Regex tabanlı aksiyon (`read`, `write`, `search`, `delete`, `execute`) ve hedef (`file`, `database`, `api`, `code`) algılama. Stop-word filtreleme ile keyword çıkarımı.

### 2. Keyword Matching
Tool capability'leri ile keyword tam/kısmi eşleştirme. Kategori eşleşme bonusu ve description kelime örtüşmesi hesaplama.

### 3. Semantic Search (ChromaDB + OpenAI)
Tool açıklamalarını **OpenAI `text-embedding-3-small`** modeli ile vektörleştirerek ChromaDB'de depolar. Kullanıcı sorgusunu aynı modelle vektörleyip **cosine similarity** ile en yakın tool'ları bulur.

> Keyword eşleşmesi olmasa bile anlamsal yakınlık üzerinden doğru aracı bulmayı sağlar.  
> Örn: *"I want to store some notes on disk"* → `write_file`

## ⚙️ Kurulum

### Gereksinimler
- Python 3.10+
- Conda `ai` ortamı (veya herhangi bir Python ortamı)

### Bağımlılıklar
```bash
pip install chromadb openai python-dotenv
```

### Ortam Değişkenleri
`.env` dosyasında OpenAI API anahtarınızı tanımlayın:
```
OPENAI_API_KEY=sk-...
```

## 🚀 Çalıştırma

```bash
python main.py
```

Çıktı dört bölüm içerir:
1. **Auto-Load** — `tools/` dizininden otomatik tool keşfi ve yükleme
2. **Pipeline Test** — 8 temel sorgu ile tool seçim pipeline'ı
3. **Fallback Test** — Düşük güven ve belirsiz sorgular için yedek plan senaryoları
4. **Semantic Search Test** — Keyword eşleşmesi zayıf, anlamsal yakınlığı yüksek 6 sorgu

## 📊 Skorlama Ağırlıkları

| Strateji | Ağırlık |
|---|---|
| Exact keyword match | 1.0 |
| Semantic match | 0.6 |
| Partial keyword match | 0.5 |
| Category match | 0.3 |
| Description overlap | 0.2 |

**AI yardımcı ile geliştirilmiştir.**

## Referances

https://oneuptime.com/blog/post/2026-01-30-tool-selection/
