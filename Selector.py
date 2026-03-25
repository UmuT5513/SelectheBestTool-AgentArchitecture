from dataclasses import dataclass
from typing import List, Dict, Any, Optional

from Tool import ToolSchema, ToolRegistry
from Validate import ParameterValidator
from Score import CapabilityScorer
from Intent import IntentParser
from SemanticSearch import SemanticSearch, HyDESearch


@dataclass
class SelectionResult:
    tool: ToolSchema  # ToolSchema
    confidence: float
    validated_params: Dict[str, Any]
    missing_params: List[str]
    warnings: List[str]

class ToolSelector:
    def __init__(
        self,
        registry: ToolRegistry,   # ToolRegistry
        parser: IntentParser,     # IntentParser
        scorer: CapabilityScorer,     # CapabilityScorer
        validator: ParameterValidator,   # ParameterValidator
        semantic_search: Optional[SemanticSearch] = None,  # Semantic Search (opsiyonel)
        hyde_search: Optional[HyDESearch] = None
    ):
        # Bağımlılık Enjeksiyonu (Dependency Injection)
        self.registry = registry
        self.parser = parser
        self.scorer = scorer
        self.validator = validator
        self.semantic_search = semantic_search
        self.hyde_search = hyde_search


    def select(self, user_request: str) -> Optional[SelectionResult]:
        # 1. Adım: Niyeti (intent) ayrıştır
        intent = self.parser.parse(user_request)

        # 2. Adım: Aday araçları getir (semantic search dahil)
        candidates = self._get_candidates(intent, user_request)

        if not candidates:
            return None

        # 3. Adım: Semantic skorları hesapla (varsa)
        semantic_scores = None
        if self.hyde_search:
            print("HyDE Semantic Search kullaniliyor...")
            candidate_names = [t.name for t in candidates]
            semantic_scores = self.hyde_search.get_semantic_scores(user_request, candidate_names)
        elif self.semantic_search:
            print("Standard Semantic Search kullaniliyor...")
            candidate_names = [t.name for t in candidates]
            semantic_scores = self.semantic_search.get_semantic_scores(user_request, candidate_names)

        # 4. Adım: Araçları puanla ve sırala (semantic skorlar dahil)
        scored = self.scorer.score(candidates, intent, semantic_scores=semantic_scores)
        
        # Güvenlik kontrolü (skorlanan araç yoksa)
        if not scored:
            return None

        # 5. Adım: En iyi eşleşmeyi seç
        best_match = scored[0]

        # 6. Adım: Parametreleri doğrula
        validation = self.validator.validate(
            best_match.tool,
            intent.parameters
        )

        return SelectionResult(
            tool=best_match.tool,
            confidence=best_match.confidence,
            validated_params=validation.validated_params,
            missing_params=validation.missing_required,
            warnings=validation.warnings
        )

    def _get_candidates(self, intent: Any, user_request: str = "") -> List[Any]:

        candidates: Dict[str, Any] = {}

        # Kategori ile eşleşen araçları ekle
        if intent.category:
            for tool in self.registry.get_all_tools():
                if getattr(tool, 'category', None) == intent.category:
                    candidates[tool.name] = tool

        # Anahtar kelimelerle eşleşen araçları ekle
        for keyword in intent.keywords:
            for tool in self.registry.find_by_capability(keyword):
                candidates[tool.name] = tool

        # Semantic search veya HyDE ile eşleşen araçları ekle
        if self.hyde_search and user_request:
            semantic_results = self.hyde_search.search(user_request, n_results=3)
            for tool_name, _distance in semantic_results:
                tool = self.registry.get_tool(tool_name)
                if tool:
                    candidates[tool.name] = tool
        elif self.semantic_search and user_request:
            semantic_results = self.semantic_search.search(user_request, n_results=3)
            for tool_name, _distance in semantic_results:
                tool = self.registry.get_tool(tool_name)
                if tool:
                    candidates[tool.name] = tool



        # Eğer hiçbir eşleşme bulunamadıysa, puanlama için tüm araçları döndür
        if not candidates:
            return self.registry.get_all_tools()

        # Sözlükteki değerleri listeye çevirip döndür
        return list(candidates.values())