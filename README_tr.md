# SelectheBestTool - Araç Seçimi İçin Ajan Mimarisi (basit özel MCP sunucusu)

## Mimari 

3 ana bileşenimiz bulunmaktadır:

### 1. Araçlar (tools) hakkında hiçbir şey bilmeyen Ana Ajan. 
Önceden araçlar hakkında hiçbir şey bilmeyen (`gpt-4o-mini` tabanlı) bir ajan. Niyetini (intent) dinamik olarak belirtmek için bir meta-araç (`find_and_select_tool`) kullanır ve sistem onun için uygun araçları bulmaya çalışır.

### 2. Araç açıklamalarını JSON formatında saklayan Araç Kayıt Defteri (Tool Registry).
Araç açıklamalarını JSON formatında ve şema nesnelerinde saklar. Araçları otomatik olarak keşfeder.

### 3. Ana ajan ile araç kayıt defteri arasında köprü kuran Araç Seçici (Tool Selector).

Ana ajan ve araç kayıt defteri arasında bir köprü görevi görür. Bir kullanıcı olarak ana ajana bir şey sorduğunuzda, filtreleme ve puanlama boru hattını (pipeline) uygulayarak en iyi aracı bulmak için araç seçiciyi kullanacaktır.

## Diğer/Alt Bileşenler

- **Intent Parser (Niyet Ayrıştırıcı):** Kullanıcı sorgusunu anahtar kelimelere, kategoriye, eyleme (action) ve hedefe (target) göre ayrıştırır.
- **Capability Scorer (Yetki Puanlayıcı):** Araçları; tam eşleşme (exact match), kısmi eşleşme (partial match) (ayrıştırıcı tarafından çıkarılan anahtar kelimelere kadar), kategori eşleşmesi, araç açıklaması ve anlamsal eşleşme (semantic match - HyDE araması veya normal anlamsal arama) yöntemleriyle puanlar. Şu temel ağırlıkları kullanır:
  - `exact_match`: 1.0
  - `partial_match`: 0.8
  - `category_match`: 0.6
  - `description_match`: 0.4
  - `semantic_match`: 1.0
- **Validate Mechanism (Doğrulama Mekanizması):** Tip ve regex (düzenli ifade) desenlerini kontrol etmesinin yanı sıra, Ayrıştırıcı tarafından elde edilen sorgu parametrelerinin araç parametreleri ile uyumluluğunu da kontrol eder.
- **Fallback Mechanism (Yedek Plan Mekanizması):** Capability Scorer tarafından yapılan hesaplamada düşük güven (low confidence) durumu oluştuğunda alternatif bir plan uygular.
- **Semantic Search Mechanism (HyDE) (Anlamsal Arama Mekanizması):** HyDE, vektör veritabanını kullanarak kullanıcı sorgusundan hipotetik (varsayımsal) belgeler üretir. Hipotetik belgeler araç açıklamalarına göre tasarlanmış bir tür sorgu niteliğinde olduğundan, kelime eşleştirme işlemi bu sayede verimli bir şekilde uygulanabilir.

## Araçlar (Tools)

Sistem, araçları `tools/` dizininden otomatik olarak keşfeder ve kaydeder.
- **Web Araması** & **Hava Durumu**
- **Veritabanı SQL Üreticileri** & **Kod Çalıştırıcıları**
- **Takvim & Görev Yöneticileri**
- **Dosya Sistemi Araçları** (Okuma/Yazma/Silme/Arama)
- **Çevirmenler** & **Döviz Çeviriciler**
- **Yapay Zeka Görsel Üreticileri**, **Mail Gönderimi** & **Slack Entegrasyonu**

## Yeni bir araç ekleme
ToolAutoLoader bu süreci kolaylaştırır. 
Yeni bir araç eklemek için yeni bir `[arac_adi].py` dosyası oluşturun. Dosyayı doğru araç şeması (tool schema) ile doldurun.

```python
from Tool import ToolSchema, ToolParameter

my_tool = ToolSchema(
    name='my_tool',
    description='Aracın açıklaması',
    category='kategori_adi',
    parameters=[
        ToolParameter(name='param1', type='string', description='...', required=True)
    ],
    returns={'type': 'string', 'description': '...'},
    examples=[{'input': {'param1': 'value'}, 'description': 'Örnek kullanım'}],
    capabilities=['keyword1', 'keyword2']
)

TOOL_DEFINITIONS = [my_tool]
```


## Dosya Yapısı

| Dosya | Açıklama |
|---|---|
| `Tool.py` | `ToolSchema`, `ToolParameter` ve `ToolRegistry` tanımlamaları |
| `ToolAutoLoader.py` | `tools/` dizininde bulunan araçları otomatik olarak keşfeden modül |
| `Intent.py` | Kullanıcı sorgusundan eylemlerin, hedeflerin ve parametrelerin çıkarılması |
| `Score.py` | Anahtar kelime + anlamsal benzerliğe dayalı puanlama motoru |
| `SemanticSearch.py` | ChromaDB + OpenAI embedding ile vektörel anlamsal arama |
| `Selector.py` | Ana ajan ile araç kayıt defterini birbirine bağlayan ana seçim orkestratörü |
| `Validate.py` | Parametre tipi, enum ve regex doğrulaması |
| `Fallback.py` | Düşük güven senaryoları ve yedekleme (fallback) mekanizması |
| `main.py` | Demolar ve Testler |
| `tools/` | Araçların bulunduğu dizin |

## Kurulum

### 1. Repoyu (depoyu) klonlayın

```bash
git clone <repository-url>
cd SelectheBestTool
```

### 2. Çalışma alanınızı izole etmek için Sanal Ortam (Virtual Environment) oluşturun

```bash
python -m venv .venv

# Ortamı seçin (aktif edin)
# Windows
.venv\Scripts\activate # powershell kullanıyorsanız .venv\Scripts\Activate.ps1 kullanın

# Linux/Mac
source .venv/bin/activate
```

### 3. Bağımlılıkları yükleyin

```bash
pip install -r requirements.txt
```

### 4. Ortam değişkenlerini ayarlayın

Root (kök) dizinde aşağıdaki değişkenlerle birlikte bir `.env` dosyası oluşturun:

```env
OPENAI_API_KEY=sizin_openai_api_anahtariniz
```

### 5. Uygulamayı çalıştırın

```bash
python main.py
```

Not: Uygulamayı çalıştırdığınızda, `tools/` dizinindeki araçları otomatik olarak keşfedecek ve bunları araç kayıt defterine (tool registry) kaydedecektir. Dosyanın çalışma akışı şu şekildedir: İlk olarak ana ajan olmadan sistemin demolarını size gösterecektir. Ardından, durmaksızın veya kullanıcıya herhangi bir şey sormaksızın birkaç örnekle ana ajanı test edecektir.


## Sorunlar (Issues)
Parametre yakalama mekanizması yeterince iyi çalışmıyor.

![Missing Parameters](source_photos/missing_params.png)

**Sorun muhtemelen Araç tanımlarıyla, açıklamalarıyla ve örnekleriyle ilgilidir. Araçlar net ve belirgin bir şekilde tanımlanırsa mekanizma daha iyi çalışacaktır.**


## Standart Anlamsal (Semantic) Arama ile HyDE'ın Karşılaştırılması

- **Kullanıcı sorgusu:** *"150 USD'yi EUR'ya çevir"*

**Standart Anlamsal Arama:**
> Sadece kullanıcı sorgusunu vektör veritabanına gönderir. Vektör veritabanı, kullanıcı sorgusuna en çok benzeyen belgeleri döndürür.

**HyDE:**
> **Vektör veritabanına gönderilecek olan hipotetik (varsayımsal) belge:** *"CurrencyConverter Pro: Para birimlerini gerçek zamanlı olarak isabetli bir şekilde çeviren, kullanıcıların USD'yi EUR'ya ve tam tersine hızlı ve verimli bir şekilde dönüştürmesini sağlayan güçlü bir araç. Yetenekler: gerçek zamanlı dönüştürme, çoklu para birimi desteği, geçmiş veri analizi, kullanıcı dostu arayüz, özelleştirilebilir döviz kurları."*

**Sonuç:**
![Standard Semantic vs HyDE](source_photos/standartsemantic_vs_HyDE.png)




## Ana Ajan'ın Kullanımı (Use of Main Agent)

![Main Agent Example](source_photos/main_agent_example_1_1.png)

Paylaşmadığım diğer sonuçlar ve buradaki sonuç şunu gösteriyor ki, sistem bir tür demo olduğu için Capability Scorer (Yetki Puanlayıcı) konfigürasyonu hayati önem taşımaktadır. Sorun şu ki, ana ajan en iyi aracı bulmak istediğinde araçların puanını kontrol ediyor. Puanlar bir aracı seçmek için yeterince iyi olmadığından, yanıtlar alakasız sonuçlar veriyor veya netleştirme istenmesine yol açıyor.

## Referanslar

https://oneuptime.com/blog/post/2026-01-30-tool-selection/
