"""
Çeviri Servisi (Mock)
Verilen metni istenen dile çevirir.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Tool import ToolSchema, ToolParameter

translator_tool = ToolSchema(
    name='translator',
    description='Verilen metni kaynak dilden hedef dile çevirir. Türkçe, İngilizce, Almanca, Fransızca ve daha birçok dili destekler.',
    category='language',
    parameters=[
        ToolParameter(
            name='text',
            type='string',
            description='Çevrilecek metin',
            required=True
        ),
        ToolParameter(
            name='target_language',
            type='string',
            description='Hedef dil kodu (örn: en, tr, de, fr)',
            required=True
        ),
        ToolParameter(
            name='source_language',
            type='string',
            description='Kaynak dil kodu (otomatik algılama için boş bırakılabilir)',
            required=False,
            default='auto'
        )
    ],
    returns={'type': 'object', 'description': 'Çevrilmiş metin, algılanan kaynak dil ve güven skoru'},
    examples=[
        {'input': {'text': 'Merhaba dünya', 'target_language': 'en'}, 'description': 'Türkçe metni İngilizceye çevir'},
        {'input': {'text': 'Hello world', 'target_language': 'tr', 'source_language': 'en'}, 'description': 'İngilizceden Türkçeye çevir'}
    ],
    capabilities=['translate', 'language', 'çeviri', 'text', 'localize', 'dil', 'tercüme', 'çevir']
)

TOOL_DEFINITIONS = [translator_tool]
