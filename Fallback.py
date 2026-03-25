from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Literal
from Intent import IntentParser
from Score import CapabilityScorer


FallbackStatus = Literal[
    'success', 
    'needs_confirmation', 
    'no_match', 
    'fallback_success', 
    'clarification_needed'
]

@dataclass
class FallbackConfig:
    min_confidence_threshold: float = 0.4
    confirmation_threshold: float = 0.7
    max_fallback_attempts: int = 3
    fallback_order: List[str] = field(default_factory=list)

@dataclass
class FallbackResult:
    status: FallbackStatus
    requires_confirmation: bool
    tool: Optional[Any] = None  # ToolSchema
    params: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    suggestions: Optional[List[Dict[str, str]]] = None
    questions: Optional[List[str]] = None

class FallbackHandler:
    def __init__(
        self,
        selector: Any,   # ToolSelector
        registry: Any,   # ToolRegistry
        config_overrides: Optional[Dict[str, Any]] = None
    ):
        self.selector = selector
        self.registry = registry
        self.config = FallbackConfig()
        
        # TypeScript'teki Partial<FallbackConfig> mantığını uygula (Özellikleri ez)
        if config_overrides:
            for key, value in config_overrides.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)

    async def select_with_fallback(self, request: str) -> FallbackResult:
        primary = self.selector.select(request)

        # Durum 1: Hiçbir araç bulunamadı
        if not primary:
            return self._handle_no_match(request)

        # Durum 2: Yüksek güven (confidence) - doğrudan ilerle
        if primary.confidence >= self.config.confirmation_threshold:
            return FallbackResult(
                status='success',
                tool=primary.tool,
                params=primary.validated_params,
                requires_confirmation=False
            )

        # Durum 3: Orta düzey güven - onay iste
        if primary.confidence >= self.config.min_confidence_threshold:
            percentage = round(primary.confidence * 100)
            return FallbackResult(
                status='needs_confirmation',
                tool=primary.tool,
                params=primary.validated_params,
                requires_confirmation=True,
                message=f"I'm {percentage}% confident you want to use {primary.tool.name}. Is this correct?"
            )

        # Durum 4: Düşük güven - yedek planları (fallbacks) dene
        return await self._try_fallbacks(request, primary)

    def _handle_no_match(self, request: str) -> FallbackResult:
        # Açıklama aramasına dayanarak benzer araçlar öner
        # TypeScript'teki .slice(0, 3) yerine Python dilimlemesi (slicing) kullanıyoruz
        suggestions_raw = self.registry.search_tools(request)[:3]
        
        suggestions = [
            {"name": t.name, "description": t.description}
            for t in suggestions_raw
        ]

        return FallbackResult(
            status='no_match',
            requires_confirmation=False,
            message='I could not find a suitable tool for this request.',
            suggestions=suggestions
        )

    async def _try_fallbacks(self, request: str, primary: Any) -> FallbackResult:
        attempts: List[str] = [primary.tool.name]

        for fallback_name in self.config.fallback_order:
            if len(attempts) >= self.config.max_fallback_attempts:
                break

            if fallback_name in attempts:
                continue

            fallback_tool = self.registry.get_tool(fallback_name)
            if not fallback_tool:
                continue

            # Yedek aracın bu isteği yönetip yönetemeyeceğini kontrol et
            parser = IntentParser()
            intent = parser.parse(request)
            scorer = CapabilityScorer()
            scores = scorer.score([fallback_tool], intent)

            # Eşleşme varsa ve güven eşiğini aşıyorsa
            if scores and scores[0].confidence >= self.config.min_confidence_threshold:
                return FallbackResult(
                    status='fallback_success',
                    tool=fallback_tool,
                    params={},
                    requires_confirmation=True,
                    message=f"Primary tool had low confidence. Suggesting {fallback_tool.name} instead."
                )

            attempts.append(fallback_name)

        return FallbackResult(
            status='clarification_needed',
            requires_confirmation=False,
            message='I need more information to select the right tool.',
            questions=[
                'What type of operation do you want to perform?',
                'What data or resource are you working with?'
            ]
        )