"""
Döviz / Kripto Çevirici (Mock)
Güncel pariteler arası dönüşüm yapar.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Tool import ToolSchema, ToolParameter

currency_converter_tool = ToolSchema(
    name='currency_converter',
    description='Döviz ve kripto para birimleri arasında güncel kurlarla dönüşüm yapar. USD, EUR, TRY, BTC gibi birimleri destekler.',
    category='finance',
    parameters=[
        ToolParameter(
            name='amount',
            type='number',
            description='Dönüştürülecek miktar',
            required=True
        ),
        ToolParameter(
            name='from_currency',
            type='string',
            description='Kaynak para birimi kodu (örn: USD, EUR, BTC)',
            required=True
        ),
        ToolParameter(
            name='to_currency',
            type='string',
            description='Hedef para birimi kodu (örn: TRY, EUR, ETH)',
            required=True
        )
    ],
    returns={'type': 'object', 'description': 'Dönüşüm sonucu, kur bilgisi ve zaman damgası'},
    examples=[
        {'input': {'amount': 100, 'from_currency': 'USD', 'to_currency': 'TRY'}, 'description': '100 dolar kaç TL'},
        {'input': {'amount': 1, 'from_currency': 'BTC', 'to_currency': 'USD'}, 'description': '1 Bitcoin kaç dolar'}
    ],
    capabilities=['currency', 'exchange', 'convert', 'crypto', 'bitcoin', 'dolar', 'euro', 'döviz', 'kur', 'parite']
)

TOOL_DEFINITIONS = [currency_converter_tool]
