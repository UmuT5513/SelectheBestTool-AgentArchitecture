"""
Takvim Yönetimi (Mock)
Etkinlikleri sorgular veya yeni etkinlik oluşturur.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Tool import ToolSchema, ToolParameter

calendar_manager_tool = ToolSchema(
    name='calendar_manager',
    description='Takvim etkinliklerini sorgular, yeni etkinlik oluşturur veya mevcut etkinlikleri günceller. Toplantı, randevu ve hatırlatıcı yönetimi sağlar.',
    category='productivity',
    parameters=[
        ToolParameter(
            name='action',
            type='string',
            description='Yapılacak işlem',
            required=True,
            enum=['list', 'create', 'update', 'delete']
        ),
        ToolParameter(
            name='date',
            type='string',
            description='Tarih (YYYY-MM-DD formatında)',
            required=False
        ),
        ToolParameter(
            name='title',
            type='string',
            description='Etkinlik başlığı (oluşturma/güncelleme için)',
            required=False
        ),
        ToolParameter(
            name='time',
            type='string',
            description='Etkinlik saati (HH:MM formatında)',
            required=False
        ),
        ToolParameter(
            name='description',
            type='string',
            description='Etkinlik açıklaması',
            required=False
        )
    ],
    returns={'type': 'object', 'description': 'Etkinlik listesi veya işlem sonucu'},
    examples=[
        {'input': {'action': 'list', 'date': '2026-03-25'}, 'description': 'Yarınki etkinlikleri listele'},
        {'input': {'action': 'create', 'date': '2026-03-26', 'title': 'Toplantı', 'time': '14:00'}, 'description': 'Yeni toplantı oluştur'}
    ],
    capabilities=['calendar', 'event', 'schedule', 'meeting', 'appointment', 'takvim', 'toplantı', 'randevu', 'etkinlik']
)

TOOL_DEFINITIONS = [calendar_manager_tool]
