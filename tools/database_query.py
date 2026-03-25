"""
Veritabanı Sorgulayıcı (Mock)
Basit bir SQL veritabanından veri çeker.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Tool import ToolSchema, ToolParameter

database_query_tool = ToolSchema(
    name='database_query',
    description='SQL veritabanından veri çeker. SELECT sorguları çalıştırır ve sonuçları tablo formatında döndürür.',
    category='data',
    parameters=[
        ToolParameter(
            name='query',
            type='string',
            description='Çalıştırılacak SQL sorgusu',
            required=True
        ),
        ToolParameter(
            name='database',
            type='string',
            description='Hedef veritabanı adı',
            required=False,
            default='default'
        ),
        ToolParameter(
            name='limit',
            type='number',
            description='Döndürülecek maksimum satır sayısı',
            required=False,
            default=100
        )
    ],
    returns={'type': 'object', 'description': 'Sorgu sonuçları (sütunlar ve satırlar) ve etkilenen satır sayısı'},
    examples=[
        {'input': {'query': 'SELECT * FROM users WHERE active = 1'}, 'description': 'Aktif kullanıcıları getir'},
        {'input': {'query': 'SELECT COUNT(*) FROM orders', 'database': 'sales'}, 'description': 'Sipariş sayısını sorgula'}
    ],
    capabilities=['database', 'sql', 'query', 'select', 'table', 'data', 'veritabanı', 'sorgu', 'veri']
)

TOOL_DEFINITIONS = [database_query_tool]
