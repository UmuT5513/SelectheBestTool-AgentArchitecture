"""
Hava Durumu Servisi (Mock)
Belirli bir lokasyonun güncel hava durumunu getirir.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Tool import ToolSchema, ToolParameter

weather_tool = ToolSchema(
    name='weather',
    description='Belirli bir lokasyonun güncel hava durumunu getirir. Sıcaklık, nem, rüzgar hızı ve genel durum bilgisini döndürür.',
    category='service',
    parameters=[
        ToolParameter(
            name='location',
            type='string',
            description='Hava durumu sorgulanacak şehir veya konum (örn: İstanbul, Ankara)',
            required=True
        ),
        ToolParameter(
            name='unit',
            type='string',
            description='Sıcaklık birimi',
            required=False,
            default='celsius',
            enum=['celsius', 'fahrenheit']
        )
    ],
    returns={'type': 'object', 'description': 'Sıcaklık, nem, rüzgar hızı ve genel hava durumu bilgisi'},
    examples=[
        {'input': {'location': 'İstanbul'}, 'description': 'İstanbul hava durumu sorgula'},
        {'input': {'location': 'Ankara', 'unit': 'fahrenheit'}, 'description': 'Ankara hava durumunu Fahrenheit olarak getir'}
    ],
    capabilities=['weather', 'forecast', 'temperature', 'climate', 'hava', 'sıcaklık', 'meteoroloji']
)

TOOL_DEFINITIONS = [weather_tool]
