"""
Belge Okuyucu (Mock)
Verilen bir URL'deki PDF veya TXT dosyasının içeriğini okur.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Tool import ToolSchema, ToolParameter

document_reader_tool = ToolSchema(
    name='document_reader',
    description='Verilen bir URL veya dosya yolundaki PDF, TXT veya DOCX belgesinin içeriğini okur ve metin olarak döndürür.',
    category='document',
    parameters=[
        ToolParameter(
            name='url',
            type='string',
            description='Belgenin URL adresi veya dosya yolu',
            required=True
        ),
        ToolParameter(
            name='format',
            type='string',
            description='Belge formatı',
            required=False,
            default='auto',
            enum=['auto', 'pdf', 'txt', 'docx']
        ),
        ToolParameter(
            name='max_pages',
            type='number',
            description='Okunacak maksimum sayfa sayısı (PDF için)',
            required=False,
            default=50
        )
    ],
    returns={'type': 'object', 'description': 'Belge metni, sayfa sayısı ve metadata bilgisi'},
    examples=[
        {'input': {'url': 'https://example.com/report.pdf'}, 'description': 'PDF raporu oku'},
        {'input': {'url': '/docs/notes.txt', 'format': 'txt'}, 'description': 'TXT dosyasını oku'}
    ],
    capabilities=['document', 'pdf', 'read', 'text', 'url', 'file', 'belge', 'oku', 'dosya', 'döküman']
)

TOOL_DEFINITIONS = [document_reader_tool]
