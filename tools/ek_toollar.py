"""
Toollar toplu olarak tek bir dosya halinde de eklenebilir. Tool sayısı: 6
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Tool import ToolSchema, ToolParameter

# --- BİLGİ VE ARAŞTIRMA ---
stock_market_tool = ToolSchema(
    name='stock_market_tracker',
    description='Belirli bir hisse senedi veya kripto varlığın anlık fiyat, hacim ve değişim verilerini getirir.',
    category='finance',
    parameters=[
        ToolParameter(name='symbol', type='string', description='Hisse kodu veya sembolü (örn: AAPL, BTC-USD, THYAO)', required=True),
        ToolParameter(name='interval', type='string', description='Zaman aralığı', required=False, default='1d', enum=['1m', '15m', '1h', '1d', '1wk'])
    ],
    returns={'type': 'object', 'description': 'Fiyat, değişim yüzdesi ve piyasa verileri'},
    examples=[{'input': {'symbol': 'NVDA'}, 'description': 'Nvidia hisse verisini getir'}],
    capabilities=['search', 'api', 'finance', 'price', 'borsa', 'hisse']
)

# --- ÜRETKENLİK VE ORGANİZASYON ---
task_creator_tool = ToolSchema(
    name='task_creator',
    description='Todo listesine veya proje yönetim sistemine yeni bir görev ekler.',
    category='productivity',
    parameters=[
        ToolParameter(name='title', type='string', description='Görevin başlığı', required=True),
        ToolParameter(name='due_date', type='string', description='Bitiş tarihi (YYYY-MM-DD)', required=False),
        ToolParameter(name='priority', type='string', description='Öncelik seviyesi', required=False, default='medium', enum=['low', 'medium', 'high'])
    ],
    returns={'type': 'object', 'description': 'Oluşturulan görev ID\'si ve durum bilgisi'},
    examples=[{'input': {'title': 'Raporu hazırla', 'priority': 'high'}, 'description': 'Yüksek öncelikli görev oluştur'}],
    capabilities=['write', 'api', 'task', 'todo', 'görev', 'ekle']
)

# --- VERİ VE YAZILIM ---
sql_generator_tool = ToolSchema(
    name='sql_query_generator',
    description='Doğal dildeki isteği SQL sorgusuna dönüştürür ve opsiyonel olarak hedef veritabanında çalıştırır.',
    category='data',
    parameters=[
        ToolParameter(name='prompt', type='string', description='Sorgulanmak istenen veri tanımı', required=True),
        ToolParameter(name='dialect', type='string', description='SQL lehçesi', required=False, default='postgresql', enum=['postgresql', 'mysql', 'sqlite']),
        ToolParameter(name='execute', type='boolean', description='Sorgu oluşturulduktan sonra çalıştırılsın mı?', required=False, default=False)
    ],
    returns={'type': 'object', 'description': 'Oluşturulan SQL kodu ve eğer çalıştırıldıysa sonuç kümesi'},
    examples=[{'input': {'prompt': 'Son 30 gündeki satışları getir', 'execute': True}, 'description': 'Satış verilerini sorgula'}],
    capabilities=['write', 'execute', 'database', 'sql', 'query', 'data']
)

# --- MEDYA VE TASARIM ---
image_generator_tool = ToolSchema(
    name='image_generator',
    description='Metin açıklamasından yapay zeka ile görsel oluşturur.',
    category='media',
    parameters=[
        ToolParameter(name='prompt', type='string', description='Görselin detaylı tanımı', required=True),
        ToolParameter(name='aspect_ratio', type='string', description='En-boy oranı', required=False, default='1:1', enum=['1:1', '16:9', '4:3']),
        ToolParameter(name='style', type='string', description='Görsel stili', required=False, default='photorealistic', enum=['photorealistic', 'sketch', 'digital_art', 'anime'])
    ],
    returns={'type': 'object', 'description': 'Görsel URL adresi ve metadata'},
    examples=[{'input': {'prompt': 'Cyberpunk bir şehirde koşan robot', 'aspect_ratio': '16:9'}, 'description': 'Fütüristik görsel üret'}],
    capabilities=['write', 'execute', 'api', 'image', 'generate', 'görsel', 'çiz']
)

# --- İLETİŞİM VE SOSYAL MEDYA ---
slack_sender_tool = ToolSchema(
    name='slack_message_sender',
    description='Belirli bir Slack kanalına veya kullanıcıya mesaj gönderir.',
    category='communication',
    parameters=[
        ToolParameter(name='channel', type='string', description='Kanal adı veya ID', required=True),
        ToolParameter(name='message', type='string', description='Gönderilecek mesaj metni', required=True),
        ToolParameter(name='thread_ts', type='string', description='Yanıtlanacak mesajın timestamp değeri (opsiyonel)', required=False)
    ],
    returns={'type': 'boolean', 'description': 'Mesajın başarıyla gönderilip gönderilmediği'},
    examples=[{'input': {'channel': '#genel', 'message': 'Toplantı başladı!'}, 'description': 'Kanala duyuru yap'}],
    capabilities=['write', 'api', 'slack', 'message', 'send', 'mesaj']
)

# --- ALIŞVERİŞ VE LOJİSTİK ---
package_tracker_tool = ToolSchema(
    name='package_tracker',
    description='Kargo takip numarasını kullanarak paket durumunu sorgular.',
    category='logistics',
    parameters=[
        ToolParameter(name='tracking_number', type='string', description='Kargo takip numarası', required=True),
        ToolParameter(name='carrier', type='string', description='Kargo firması', required=False, default='auto')
    ],
    returns={'type': 'object', 'description': 'Paketin konumu, durumu ve tahmini teslim tarihi'},
    examples=[{'input': {'tracking_number': 'TR123456789'}, 'description': 'Kargo durumunu sorgula'}],
    capabilities=['read', 'api', 'track', 'package', 'kargo', 'takip']
)

# --- DOSYA SİSTEMİ ARAÇLARI ---

read_file_tool = ToolSchema(
    name='read_file',
    description='Dosya sistemindeki bir dosyanın içeriğini okur.',
    category='document',
    parameters=[
        ToolParameter(name='path', type='string', description='Okunacak dosyanın tam yolu', required=True)
    ],
    returns={'type': 'string', 'description': 'Dosyanın metin içeriği'},
    examples=[{'input': {'path': 'config.json'}, 'description': 'config.json dosyasını oku'}],
    capabilities=['read', 'file', 'filesystem', 'document']
)

write_file_tool = ToolSchema(
    name='write_file',
    description='Dosya sistemine içerik yazar. Dosya yoksa oluşturur, varsa üzerine yazar.',
    category='document',
    parameters=[
        ToolParameter(name='path', type='string', description='Yazılacak dosyanın yolu', required=True),
        ToolParameter(name='content', type='string', description='Dosyaya yazılacak içerik', required=True)
    ],
    returns={'type': 'boolean', 'description': 'Yazma işlemi başarılıysa true döner'},
    examples=[{'input': {'path': 'notes.txt', 'content': 'Merhaba Dünya'}, 'description': 'Yeni bir not dosyası oluştur'}],
    capabilities=['write', 'file', 'filesystem', 'create']
)

search_files_tool = ToolSchema(
    name='search_files',
    description='Belirli bir dizin ağacında desene (pattern) uygun dosyaları arar.',
    category='document',
    parameters=[
        ToolParameter(name='directory', type='string', description='Aramanın başlayacağı kök dizin', required=True),
        ToolParameter(name='pattern', type='string', description='Dosya adı deseni (örn: *.py, data_*)', required=True)
    ],
    returns={'type': 'array', 'description': 'Eşleşen dosya yollarının listesi'},
    examples=[{'input': {'directory': './src', 'pattern': '*.js'}, 'description': 'src içindeki tüm javascript dosyalarını bul'}],
    capabilities=['search', 'find', 'filesystem', 'glob']
)

delete_file_tool = ToolSchema(
    name='delete_file',
    description='Dosya sisteminden bir dosyayı kalıcı olarak siler.',
    category='document',
    parameters=[
        ToolParameter(name='path', type='string', description='Silinecek dosyanın yolu', required=True)
    ],
    returns={'type': 'boolean', 'description': 'Silme işlemi başarılıysa true döner'},
    examples=[{'input': {'path': 'temp.log'}, 'description': 'Geçici log dosyasını sil'}],
    capabilities=['delete', 'remove', 'filesystem']
)

# --- NETWORK VE EXECUTION ARAÇLARI ---

http_request_tool = ToolSchema(
    name='http_request',
    description='Bir API uç noktasına HTTP isteği gönderir ve yanıtı döner.',
    category='network',
    parameters=[
        ToolParameter(name='url', type='string', description='İstek gönderilecek URL', required=True),
        ToolParameter(name='method', type='string', description='HTTP Metodu (GET, POST, PUT, DELETE)', required=False, default='GET'),
        ToolParameter(name='body', type='string', description='İstek gövdesi (JSON string vb.)', required=False),
        ToolParameter(name='headers', type='object', description='HTTP başlıkları (headers)', required=False)
    ],
    returns={'type': 'object', 'description': 'Yanıt kodu ve gövdesi'},
    examples=[{'input': {'url': 'https://api.example.com/v1/users', 'method': 'GET'}, 'description': 'Kullanıcı listesini getir'}],
    capabilities=['network', 'api', 'http', 'request']
)

run_script_tool = ToolSchema(
    name='run_script',
    description='Shell ortamında bir script veya komut çalıştırır.',
    category='execution',
    parameters=[
        ToolParameter(name='command', type='string', description='Çalıştırılacak shell komutu veya script yolu', required=True)
    ],
    returns={'type': 'object', 'description': 'Standart çıktı (stdout) ve hata (stderr) verileri'},
    examples=[{'input': {'command': 'python3 process_data.py'}, 'description': 'Veri işleme scriptini çalıştır'}],
    capabilities=['execute', 'shell', 'script', 'command']
)


TOOL_DEFINITIONS = [
    stock_market_tool, 
    task_creator_tool, 
    sql_generator_tool, 
    image_generator_tool, 
    slack_sender_tool,
    package_tracker_tool,
    read_file_tool,
    write_file_tool,
    search_files_tool,
    delete_file_tool,
    http_request_tool,
    run_script_tool
]