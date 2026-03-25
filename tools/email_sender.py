"""
E-posta Gönderici (Mock)
Belirtilen adrese e-posta atma simülasyonu yapar.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Tool import ToolSchema, ToolParameter

email_sender_tool = ToolSchema(
    name='email_sender',
    description='Belirtilen adrese e-posta gönderme simülasyonu yapar. Konu, gövde ve ek dosya desteği ile e-posta gönderir.',
    category='communication',
    parameters=[
        ToolParameter(
            name='to',
            type='string',
            description='Alıcı e-posta adresi',
            required=True,
            pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$'
        ),
        ToolParameter(
            name='subject',
            type='string',
            description='E-posta konusu',
            required=True
        ),
        ToolParameter(
            name='body',
            type='string',
            description='E-posta gövde metni',
            required=True
        ),
        ToolParameter(
            name='cc',
            type='string',
            description='CC (karbon kopya) alıcı adresi',
            required=False
        )
    ],
    returns={'type': 'object', 'description': 'Gönderim durumu, mesaj ID ve zaman damgası'},
    examples=[
        {'input': {'to': 'user@example.com', 'subject': 'Toplantı', 'body': 'Yarınki toplantı saat 14:00.'}, 'description': 'E-posta gönder'},
        {'input': {'to': 'team@company.com', 'subject': 'Rapor', 'body': 'Aylık rapor ekte.', 'cc': 'manager@company.com'}, 'description': 'CC ile e-posta gönder'}
    ],
    capabilities=['email', 'send', 'mail', 'message', 'eposta', 'gönder', 'ileti', 'mektup']
)

TOOL_DEFINITIONS = [email_sender_tool]
