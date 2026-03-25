"""
Zamanlayıcı / Alarm (Mock)
Belirli bir süre sonrasına hatırlatıcı kurar.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Tool import ToolSchema, ToolParameter

timer_tool = ToolSchema(
    name='timer',
    description='Belirli bir süre sonrasına hatırlatıcı veya alarm kurar. Dakika, saat veya belirli bir zaman için zamanlayıcı ayarlar.',
    category='productivity',
    parameters=[
        ToolParameter(
            name='duration',
            type='number',
            description='Süre (dakika cinsinden)',
            required=False
        ),
        ToolParameter(
            name='time',
            type='string',
            description='Hedef zaman (HH:MM formatında, duration yerine kullanılır)',
            required=False
        ),
        ToolParameter(
            name='message',
            type='string',
            description='Hatırlatıcı mesajı',
            required=True
        ),
        ToolParameter(
            name='repeat',
            type='boolean',
            description='Tekrarlansın mı',
            required=False,
            default=False
        )
    ],
    returns={'type': 'object', 'description': 'Zamanlayıcı ID, kalan süre ve durum bilgisi'},
    examples=[
        {'input': {'duration': 30, 'message': 'Toplantıya 5 dakika kaldı'}, 'description': '30 dakika sonra hatırlat'},
        {'input': {'time': '09:00', 'message': 'Sabah standup toplantısı', 'repeat': True}, 'description': 'Her gün 09:00 alarmı kur'}
    ],
    capabilities=['timer', 'alarm', 'reminder', 'schedule', 'zamanlayıcı', 'hatırlatıcı', 'süre', 'kronometre']
)

TOOL_DEFINITIONS = [timer_tool]
