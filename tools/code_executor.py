"""
Matematiksel Kod Yürütücü (Mock)
Karmaşık matematiksel hesaplamaları Python kodu yazarak ve çalıştırarak çözer.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Tool import ToolSchema, ToolParameter

code_executor_tool = ToolSchema(
    name='code_executor',
    description='Karmaşık matematiksel hesaplamaları Python kodu yazarak ve çalıştırarak çözer. Formül, denklem ve istatistiksel işlemleri destekler.',
    category='execution',
    parameters=[
        ToolParameter(
            name='code',
            type='string',
            description='Çalıştırılacak Python kodu',
            required=True
        ),
        ToolParameter(
            name='timeout',
            type='number',
            description='Maksimum çalışma süresi (saniye)',
            required=False,
            default=30
        )
    ],
    returns={'type': 'object', 'description': 'Kodun çıktısı ve çalışma süresi bilgisi'},
    examples=[
        {'input': {'code': 'import math; print(math.factorial(10))'}, 'description': '10 faktöriyel hesapla'},
        {'input': {'code': 'print(sum(range(1, 101)))'}, 'description': '1den 100e kadar topla'}
    ],
    capabilities=['math', 'calculate', 'compute', 'code', 'execute', 'python', 'formula', 'hesapla', 'matematik']
)

TOOL_DEFINITIONS = [code_executor_tool]
