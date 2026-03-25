from dataclasses import dataclass
from typing import List, Dict, Any, Optional

# ToolSchema tanımının başka bir yerde yapıldığı varsayılmıştır
# Tip belirteçlerinde 'Any' yerine 'ToolSchema' yazabilirsiniz

@dataclass
class ToolScore:
    tool: Any  # ToolSchema
    score: float
    matched_capabilities: List[str]
    confidence: float

class CapabilityScorer:
    def __init__(self):
        # Ağırlıkları snake_case isimlendirme ile tanımlıyoruz
        self.weights: Dict[str, float] = {
            'exact_match': 1.0,
            'partial_match': 0.8,
            'category_match': 0.6,
            'description_match': 0.4,
            'semantic_match': 1.0
        }

    def score(self, tools: List[Any], intent: Any, semantic_scores: Optional[Dict[str, float]] = None) -> List[ToolScore]:
        scores: List[ToolScore] = []

        for tool in tools:
            matched_capabilities: List[str] = []
            total_score: float = 0.0

            # Tam (exact) ve kısmi (partial) yetenek eşleşmelerini kontrol et
            for keyword in intent.keywords:
                if keyword in tool.capabilities:
                    total_score += self.weights['exact_match']
                    matched_capabilities.append(keyword)
                elif any(keyword in cap for cap in tool.capabilities):
                    total_score += self.weights['partial_match']
                    matched_capabilities.append(f"{keyword} (partial)")

            # Kategori eşleşmesi bonusu
            if intent.category and getattr(tool, 'category', None) == intent.category:
                total_score += self.weights['category_match']

            # Açıklama (description) ilgisi (basit kelime kesişimi)
            # .split() parametresiz kullanıldığında tüm boşluklara (\s+) göre böler
            desc_words = tool.description.lower().split()
            intent_words = intent.raw_text.lower().split()
            
            # Kesişen kelimelerin sayısını bul
            overlap = sum(1 for w in intent_words if w in desc_words)
            
            # Sıfıra bölünme hatasını (ZeroDivisionError) önlemek için kontrol
            if intent_words:
                total_score += (overlap / len(intent_words)) * self.weights['description_match']

            # Semantic benzerlik skoru (varsa)
            if semantic_scores and tool.name in semantic_scores:
                total_score += semantic_scores[tool.name] * self.weights['semantic_match']

            # Güven (confidence) skorunu 0-1 aralığına normalize et
            max_possible_score = (
                len(intent.keywords) * self.weights['exact_match'] +
                self.weights['category_match'] +
                self.weights['description_match'] +
                self.weights['semantic_match']
            )

            # Olası bir sıfıra bölünme durumunu engellemek için güvenlik adımı
            confidence = min(total_score / max_possible_score, 1.0) if max_possible_score > 0 else 0.0

            scores.append(ToolScore(
                tool=tool,
                score=total_score,
                matched_capabilities=matched_capabilities,
                confidence=confidence
            ))

        # Skora göre büyükten küçüğe (descending) sırala
        return sorted(scores, key=lambda x: x.score, reverse=True)