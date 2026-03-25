"""
BestToolSelection - Demo & Test
Tum modulleri (Tool, Intent, Score, Validate, Selector, Fallback) bir araya getirip
ornek sorgularla tool secim pipeline'ini test eder.
"""

import asyncio
import os
import json
from openai import AsyncOpenAI
from typing import Optional, List, Dict

from Tool import ToolSchema, ToolParameter, ToolRegistry
from ToolAutoLoader import ToolAutoLoader
from Intent import IntentParser
from Score import CapabilityScorer
from Validate import ParameterValidator
from Selector import ToolSelector
from Fallback import FallbackHandler
from SemanticSearch import SemanticSearch, HyDESearch


# ─── Main Agent (Ana Ajan) ───────────────────────────────────────

class MainAgent:
    """
    Kullanıcıdan gelen talebi (task) alan, planlayan ve süreci yöneten Ana Ajan.
    Önemli Kısıt: Başlangıçta sistemdeki araçları bilmez ve onlara doğrudan erişimi yoktur.
    İhtiyaç duyduğunda "find_and_select_tool" (meta-tool) aracını kullanarak niyetini (intent) belirtir
    ve uygun aracı bulup kullanır.
    """
    def __init__(self, fallback_handler: FallbackHandler):
        self.fallback_handler = fallback_handler
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))
        self.model = "gpt-4o-mini"
        self.system_prompt = (
            "Sen kullanıcı taleplerini alan, planlayan ve süreci yöneten Ana Ajan'sın (Main Agent).\n"
            "ÖNEMLİ KISIT: Başlangıçta sistemde hangi araçların (tool) bulunduğunu/tanımlarını BİLMİYORSUN.\n"
            "Eğer hava durumu, e-posta gönderme, web araması gibi bir eylem/araç gerektiren bir talebi yerine getirmen gerekirse, "
            "`find_and_select_tool` aracını(fonksiyonunu) çağırmak ZORUNDASIN. Parametre olarak ne yapmak istediğini (intent) "
            "doğal dilde 'intent_description' olarak ver (Örn: 'İstanbul hava durumunu bul'). \n"
            "Sistem sana uygun aracı, parametrelerini veya eksik parametre durumlarını döndürecektir.\n"
            "Gelen tool bilgilerine göre kullanıcıya ne yapacağını ve hangi aracı bulduğunu açıkla."
        )

    async def process_request(self, user_request: str) -> str:
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_request}
        ]

        tools = [
            {
                "type": "function",
                "function": {
                    "name": "find_and_select_tool",
                    "description": "Sistemdeki en uygun aracı bulmak ve seçmek için kullanılır. Araç setini bilmediğinizde bu metodu niyetiniz ile çağırın.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "intent_description": {
                                "type": "string",
                                "description": "Yapmak istediğiniz eylemin doğal dildeki açıklaması."
                            }
                        },
                        "required": ["intent_description"]
                    }
                }
            }
        ]

        # 1. Aşama: LLM'den planlama ve varsa tool_call al
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools,
            temperature=0.0
        )
        message = response.choices[0].message
        
        if message.tool_calls:
            # Asistanın mesajını geçmişe ekle
            messages.append(message)
            
            for tool_call in message.tool_calls:
                if tool_call.function.name == "find_and_select_tool":
                    args = json.loads(tool_call.function.arguments)
                    intent_query = args.get("intent_description", user_request)
                    
                    # Sistem pipeline'ı üzerinden tool ara (fallback mekanizmalı)
                    fb_result = await self.fallback_handler.select_with_fallback(intent_query)
                    
                    if fb_result.status == "success" and fb_result.tool:
                        result_data = {
                            "status": "success",
                            "selected_tool": fb_result.tool.name,
                            "description": fb_result.tool.description,
                            "params": fb_result.params
                        }
                    elif fb_result.status == "needs_confirmation":
                        result_data = {
                            "status": "needs_confirmation",
                            "message": fb_result.message,
                            "suggestions": [s['name'] for s in (fb_result.suggestions or [])]
                        }
                    else:
                        result_data = {
                            "status": fb_result.status,
                            "message": fb_result.message or "Uygun tool bulunamadı."
                        }
                        
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_call.function.name,
                        "content": json.dumps(result_data, ensure_ascii=False)
                    })
                    
            # 2. Aşama: Gelen tool sonucuna göre nihai cevabı oluştur
            final_response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.0
            )
            return final_response.choices[0].message.content
        
        return message.content or ""




# ─── Registry'ye Tool'ları Kaydet ────────────────────────────────

def build_registry() -> ToolRegistry:
    registry = ToolRegistry()

    # tools/ dizinindeki tool'lari otomatik yukle
    print("\n[*] ToolAutoLoader baslatiliyor...")
    loader = ToolAutoLoader()
    stats = loader.load_all(registry)
    print(f"[OK] Otomatik yukleme tamamlandi: "
          f"{stats['loaded']} basarili, {stats['failed']} basarisiz")
    if stats['errors']:
        for err in stats['errors']:
            print(f"   [!] {err}")
    print()

    return registry


# ─── Test Sorguları ───────────────────────────────────────────────

TEST_QUERIES = [
    "What is the weather like in Izmir today?",
    "Search the web for the latest machine learning trends",
    "Convert 150 USD to EUR",
    "Get the current stock price of TSLA",
    "Add a new task: Send the weekly report",
    "Generate a SQL query for the last 7 days of sales",
    "Track my package with number TR123456789",
    "Send a Slack message to #general: Meeting starts in 5 minutes",
    # ─── Fallback Test Sorguları ──────────────────────────────────────
    # Dusuk guven, eslesmeme ve belirsiz sorgulari test etmek icin
    "What's the temperature in Tokyo?",             # Yuksek guven -> success (weather)
    "Do something about the problem",               # Belirsiz -> clarification_needed
    "Bake a chocolate cake for me",                 # Hicbir tool yok -> no_match
    "Maybe send an email or a Slack message",       # Orta guven -> needs_confirmation (email / slack)
    "Create a new database for marketing",          # Orta/yuksek -> success/confirmation (sql_query_generator)
    "Adjust the quantum hyperdrive engines",        # Alakasiz -> no_match / clarification
    # ─── HyDE Test Sorguları ──────────────────────────────────────────
    # Doğal dilde yazılmış, keyword eşleşmesi çok zayıf olan sorgular.
    # HyDE bu tarz sorgularda standart semantic search'ten daha iyi sonuç vermeli.
    "I'm planning a trip to Paris, should I pack an umbrella?",       # weather
    "I need to know if the latest shipment has arrived yet",          # package_tracker
    "How do I say 'Good morning' in Spanish?",                        # translator
    "I need to pull the total revenue from the sales table",          # sql_query_generator
    "Can you block out my afternoon for a focused work session?",     # calendar_manager
    "I want to create a cyberpunk style avatar for my profile",       # image_generator
]





# ─── Ana Çalıştırma Fonksiyonu ───────────────────────────────────

async def main():
    # Bileşenleri oluştur
    registry = build_registry()
    parser = IntentParser()
    scorer = CapabilityScorer()
    validator = ParameterValidator()

    

    # Semantic Search'ü başlat ve tool'ları indeksle
    print("[*] Hypotetical (HyDE) Search baslatiliyor (OpenAI embedding)...")
    semantic_search = SemanticSearch()
    semantic_search.index_tools(registry.get_all_tools())
    hyde_search = HyDESearch(semantic_search)
    #NOT: hyde_search yalnızca arama yapmadan önce sorguyu hipotetik bir belgeye dönüştürüp 
    # sonra mevcut semantic_search üzerinden aramayı yürütmek için sarmalayıcı (wrapper) 
    # bir sınıf olarak çalışıyor.
    print("[OK] Tool'lar ChromaDB'ye indekslendi.\n")

    selector = ToolSelector(registry, parser, scorer, validator, hyde_search=hyde_search)

    # FallbackHandler'i başlat
    fallback_handler = FallbackHandler(
        selector=selector,
        registry=registry,
        config_overrides={
            'min_confidence_threshold': 0.3,
            'confirmation_threshold': 0.6,
            'max_fallback_attempts': 3,
            'fallback_order': ['web_search', 'weather', 'task_creator', 'sql_query_generator']
        }
    )

    print(f"\n[*] Fallback Config:")
    print(f"   - min_confidence_threshold : {fallback_handler.config.min_confidence_threshold}")
    print(f"   - confirmation_threshold   : {fallback_handler.config.confirmation_threshold}")
    print(f"   - max_fallback_attempts    : {fallback_handler.config.max_fallback_attempts}")
    print(f"   - fallback_order           : {fallback_handler.config.fallback_order}")

    print("\n" + "-" * 70)

    print("=" * 70)
    print("  BestToolSelection - Pipeline Test")
    print("=" * 70)

    # Registry'deki tum tool'lari listele
    print(f"\n[*] Kayitli Tool Sayisi: {len(registry.get_all_tools())}")
    for tool in registry.get_all_tools():
        print(f"   - {tool.name:20s} [{tool.category}] - {tool.description[:60]}...")

    print("\n" + "-" * 70)

    from itertools import chain
    for i, query in enumerate(list(chain(TEST_QUERIES[2:5], TEST_QUERIES[10:13], TEST_QUERIES[16:18])), 1):
        print(f"\n[?] Sorgu {i}: \"{query}\"")

        # 1) Intent ayristirma
        intent = parser.parse(query)
        print(f"   |-- Action   : {intent.action}")
        print(f"   |-- Target   : {intent.target}")
        print(f"   |-- Category : {intent.category}")
        print(f"   |-- Keywords : {intent.keywords}")
        print(f"   |-- Params   : {intent.parameters}")

        # 2) Tool secimi
        result = selector.select(query)


        if result:
            print(f"   |-- [OK] Secilen Tool  : {result.tool.name}")
            print(f"   |-- Confidence         : {result.confidence:.2%}")
            print(f"   |-- Validated Params   : {result.validated_params}")
            if result.missing_params:
                print(f"   |-- [!] Missing Params : {result.missing_params}")
            if result.warnings:
                print(f"   +-- [!] Warnings       : {result.warnings}")
            else:
                print(f"   +-- (Uyari yok)")
        else:
            print(f"   +-- [X] Uygun tool bulunamadi!")

        
        print(f"\n[?] Fallback Sorgu {i}: \"{query}\"")

        fb_result = await fallback_handler.select_with_fallback(query)

        print(f"   |-- Status              : {fb_result.status}")
        print(f"   |-- Requires Confirmation: {fb_result.requires_confirmation}")

        if fb_result.tool:
            print(f"   |-- Secilen Tool        : {fb_result.tool.name}")
        if fb_result.params:
            print(f"   |-- Params              : {fb_result.params}")
        if fb_result.message:
            print(f"   |-- Message             : {fb_result.message}")
        if fb_result.suggestions:
            print(f"   |-- Suggestions:")
            for s in fb_result.suggestions:
                print(f"   |     - {s['name']:20s} : {s['description'][:50]}...")
        if fb_result.questions:
            print(f"   |-- Questions:")
            for q in fb_result.questions:
                print(f"   |     - {q}")

        print("-" * 70)

    print("\n[OK] Tum testler (pipeline + fallback) tamamlandi.\n")


    # ══════════════════════════════════════════════════════════════
    #  HyDE (HYPOTHETICAL DOCUMENT EMBEDDING) TESTLERİ
    # ══════════════════════════════════════════════════════════════

    print("=" * 70)
    print("  HyDE (Hypothetical Document Embedding) - Test")
    print("=" * 70)

    # HyDESearch oluştur (mevcut semantic_search'ü sarar)
    print("\n[*] HyDESearch baslatiliyor (gpt-4o-mini)...")
    hyde_search = HyDESearch(semantic_search)
    print("[OK] HyDESearch hazir.\n")

    print("-" * 70)
    print("  KARSILASTIRMA: Standard Semantic vs HyDE")
    print("-" * 70)

    from itertools import chain
    for i, query in enumerate(list(chain(TEST_QUERIES[2:5], TEST_QUERIES[10:13], TEST_QUERIES[16:18])), 1):
        print(f"\n[?] HyDE Sorgu {i}: \"{query}\"")

        # Hipotetik belgeyi göster
        hypo_doc = hyde_search.generate_hypothetical_document(query)
        if hypo_doc:
            print(f"   |-- Hypothetical Document: \n {hypo_doc}")
        else:
            print(f"   |-- Hypothetical Doc : (uretim basarisiz, fallback)")

        # Standart Semantic Search skorları
        std_scores = semantic_search.get_semantic_scores(query)
        std_top3 = sorted(std_scores.items(), key=lambda x: x[1], reverse=True)[:3]

        # HyDE skorları
        hyde_scores = hyde_search.get_semantic_scores(query) # hemen üstte tanımlanan hypo_docs u parametre olarak vermeye gerek yok zaten hyde_search icinde olusturuluyor. O sadece hypo docs u göstermek için idi.
        hyde_top3 = sorted(hyde_scores.items(), key=lambda x: x[1], reverse=True)[:3]

        print(f"   |")
        print(f"   |-- Standard Semantic Top-3:")
        for name, score in std_top3:
            print(f"   |     - {name:20s} : {score:.4f}")
        print(f"   |")
        print(f"   |-- HyDE Semantic Top-3:")
        for name, score in hyde_top3:
            print(f"   |     - {name:20s} : {score:.4f}")

        # Fark analizi (top-1 karşılaştırması)
        std_best = std_top3[0] if std_top3 else ("N/A", 0.0)
        hyde_best = hyde_top3[0] if hyde_top3 else ("N/A", 0.0)
        diff = hyde_best[1] - std_best[1]
        indicator = "▲" if diff > 0 else ("▼" if diff < 0 else "=")
        print(f"   |")
        print(f"   +-- Top-1 Fark: {indicator} {abs(diff):.4f} "
              f"(Std: {std_best[0]}={std_best[1]:.4f}, "
              f"HyDE: {hyde_best[0]}={hyde_best[1]:.4f})")

        print("-" * 70)

    # HyDE istatistikleri
    stats = hyde_search.get_stats()
    print(f"\n[*] HyDE Istatistikleri:")
    print(f"   - Basarili HyDE cagrilari : {stats['hyde_calls']}")
    print(f"   - Fallback cagrilari      : {stats['fallback_calls']}")
    print(f"\n[OK] HyDE testleri tamamlandi.\n")

    # ══════════════════════════════════════════════════════════════
    #  MAIN AGENT TEST
    # ══════════════════════════════════════════════════════════════

    print("=" * 70)
    print("  Main Agent Testi (gpt-4o-mini)")
    print("=" * 70)

    main_agent = MainAgent(fallback_handler)

    agent_test_queries = [
        "Bana İstanbul'daki güncel hava durumunu söyle, ardından sonucu ali@example.com adresine e-posta at.",
        "Şirketin 2025 yılı hedefleri nedir?"
    ]

    for i, q in enumerate(agent_test_queries, 1):
        print(f"\n[?] Agent Sorgu {i}: \"{q}\"")
        try:
            response = await main_agent.process_request(q)
            print(f"   |-- Agent Yaniti:\n{response}\n")
        except Exception as e:
            print(f"   [!] Agent hatasi: {e}")

    print("[OK] Main Agent testleri tamamlandi.\n")


if __name__ == '__main__':
    asyncio.run(main())
