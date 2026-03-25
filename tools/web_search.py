"""
İnternet Arama (Mock)
Güncel bilgiler için internette arama yapar.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Tool import ToolSchema, ToolParameter

web_search_tool = ToolSchema(
    name='web_search',
    description='Güncel bilgiler için internette arama yapar. Arama sonuçlarını başlık, URL ve özet olarak döndürür.',
    category='network',
    parameters=[
        ToolParameter(
            name='query',
            type='string',
            description='Arama sorgusu',
            required=True
        ),
        ToolParameter(
            name='max_results',
            type='number',
            description='Döndürülecek maksimum sonuç sayısı',
            required=False,
            default=5
        ),
        ToolParameter(
            name='language',
            type='string',
            description='Arama dili',
            required=False,
            default='tr',
            enum=['tr', 'en', 'de', 'fr']
        )
    ],
    returns={'type': 'array', 'description': 'Arama sonuçları listesi (başlık, URL, özet)'},
    examples=[
        {'input': {'query': 'Python 3.12 yenilikleri'}, 'description': 'Python ile ilgili güncel haber ara'},
        {'input': {'query': 'machine learning trends', 'language': 'en'}, 'description': 'İngilizce arama yap'}
    ],
    capabilities=['search', 'web', 'internet', 'google', 'browse', 'query', 'find', 'ara', 'arama']
)

TOOL_DEFINITIONS = [web_search_tool]
