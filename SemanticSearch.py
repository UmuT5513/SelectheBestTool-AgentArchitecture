"""
SemanticSearch - ChromaDB + OpenAI Embedding tabanlı semantik arama modülü.
Tool açıklamalarını vektörleştirip, kullanıcı sorgularıyla anlamsal benzerlik araması yapar.

HyDESearch - Hypothetical Document Embedding yaklaşımı.
Kullanıcı sorgusundan önce LLM ile hipotetik bir tool açıklaması oluşturur,
ardından bu belgeyi vektörleştirerek daha iyi anlamsal eşleşme sağlar.
"""

import os
from typing import List, Dict, Tuple, Any, Optional

import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from openai import OpenAI
from dotenv import load_dotenv

# .env dosyasından API anahtarını yükle
load_dotenv()


class SemanticSearch:
    def __init__(self, collection_name: str = "tool_embeddings"):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY bulunamadı. .env dosyasını kontrol edin.")

        # OpenAI embedding fonksiyonunu oluştur
        self.embedding_fn = OpenAIEmbeddingFunction(
            api_key=api_key.strip().strip('"'),
            model_name="text-embedding-3-small"
        )

        # ChromaDB istemcisi (in-memory — kalıcılık gerekmediği için)
        self.client = chromadb.Client()

        # Koleksiyonu oluştur veya mevcut olanı al
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_fn,
            metadata={"hnsw:space": "cosine"}  # Cosine distance kullan
        )

    def _build_document(self, tool: Any) -> str:
        """Tool bilgilerini tek bir metin belgesine dönüştürür."""
        capabilities_str = ", ".join(tool.capabilities)
        return f"{tool.name}: {tool.description} Capabilities: {capabilities_str}"

    def index_tools(self, tools: List[Any]) -> None:
        """
        Tool listesini ChromaDB'ye indeksler.
        Her tool için name + description + capabilities birleşik metin olarak vektörlenir.
        """
        documents: List[str] = []
        ids: List[str] = []
        metadatas: List[Dict[str, str]] = []

        for tool in tools:
            documents.append(self._build_document(tool))
            ids.append(tool.name)
            metadatas.append({
                "name": tool.name,
                "category": tool.category,
                "description": tool.description
            })

        # Upsert: varsa güncelle, yoksa ekle
        self.collection.upsert(
            documents=documents,
            ids=ids,
            metadatas=metadatas
        )

    def search(self, query: str, n_results: int = 5) -> List[Tuple[str, float]]:
        """
        Kullanıcı sorgusuna göre en yakın tool'ları döndürür.
        Returns: [(tool_name, distance), ...] — düşük distance = yüksek benzerlik
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=min(n_results, self.collection.count())
        )

        matches: List[Tuple[str, float]] = []
        if results and results['ids'] and results['distances']:
            for tool_id, distance in zip(results['ids'][0], results['distances'][0]):
                matches.append((tool_id, distance))

        return matches

    def get_semantic_scores(self, query: str, tool_names: Optional[List[str]] = None) -> Dict[str, float]:
        """
        Kullanıcı sorgusuna göre tool'ların semantic benzerlik skorlarını döndürür.
        Cosine distance'ı similarity'ye çevirir: similarity = 1 - distance
        
        Returns: {tool_name: similarity_score, ...}  (0.0 - 1.0 arası)
        """
        # Tüm tool'lar için arama yap
        all_results = self.search(query, n_results=self.collection.count())

        scores: Dict[str, float] = {}
        for tool_name, distance in all_results:
            # Cosine distance → similarity dönüşümü
            similarity = max(0.0, 1.0 - distance)
            scores[tool_name] = similarity

        # Eğer belirli tool'lar isteniyorsa filtrele
        if tool_names is not None:
            scores = {name: scores.get(name, 0.0) for name in tool_names}

        return scores


# ═══════════════════════════════════════════════════════════════════════
#  HyDESearch — Hypothetical Document Embedding
# ═══════════════════════════════════════════════════════════════════════

HYDE_SYSTEM_PROMPT = (
    "You are a tool description generator for a tool selection system. "
    "Given a user request, write a short hypothetical tool description document "
    "that would be the IDEAL match for the request.\n\n"
    "Format:\n"
    "<tool_name>: <description> Capabilities: <comma-separated capabilities>\n\n"
    "Rules:\n"
    "- Write ONLY the tool description, nothing else.\n"
    "- Keep it concise (1-2 sentences for description).\n"
    "- Include 4-6 relevant capability keywords.\n"
    "- Focus on what the tool DOES, not what the user wants."
)


class HyDESearch:
    """
    Hypothetical Document Embedding (HyDE) tabanlı semantik arama.

    Standart semantic search'te kullanıcı sorgusu direkt embed edilir.
    HyDE yaklaşımında ise önce bir LLM ile kullanıcı sorgusundan
    hipotetik bir tool açıklaması üretilir, ardından BU belge embed
    edilerek arama yapılır. Bu, sorgu ile belge arasındaki kelime
    dağarcığı farkını kapatarak daha iyi eşleşme sağlar.
    """

    def __init__(
        self,
        semantic_search: SemanticSearch,
        model: str = "gpt-4o-mini",
        temperature: float = 0.0,
    ):
        """
        Args:
            semantic_search: Mevcut SemanticSearch örneği (ChromaDB koleksiyonunu paylaşır).
            model: Hipotetik belge üretimi için kullanılacak LLM modeli.
            temperature: LLM sıcaklık parametresi (0.0 = deterministik).
        """
        self.semantic_search = semantic_search
        self.model = model
        self.temperature = temperature

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY bulunamadı. .env dosyasını kontrol edin.")

        self.openai_client = OpenAI(api_key=api_key.strip().strip('"'))

        # İstatistik: kaç sorgu HyDE vs fallback ile çalıştı
        self._stats = {"hyde_calls": 0, "fallback_calls": 0}

    @property
    def collection(self):
        """SemanticSearch'ün ChromaDB koleksiyonuna erişim (uyumluluk için)."""
        return self.semantic_search.collection

    def generate_hypothetical_document(self, query: str) -> Optional[str]:
        """
        Kullanıcı sorgusundan hipotetik bir tool açıklaması üretir.

        Args:
            query: Kullanıcı sorgusu.

        Returns:
            Üretilen hipotetik belge metni, hata durumunda None.
        """
        try:
            response = self.openai_client.chat.completions.create(
                model=self.model,
                temperature=self.temperature,
                max_tokens=150,
                messages=[
                    {"role": "system", "content": HYDE_SYSTEM_PROMPT},
                    {"role": "user", "content": query},
                ],
            )
            hypothetical_doc = response.choices[0].message.content.strip()
            self._stats["hyde_calls"] += 1
            return hypothetical_doc

        except Exception as e:
            print(f"   [!] HyDE belge üretimi başarısız, fallback'e geçiliyor: {e}")
            self._stats["fallback_calls"] += 1
            return None

    def search(self, query: str, n_results: int = 5) -> List[Tuple[str, float]]:
        """
        HyDE yaklaşımıyla arama yapar.
        Önce hipotetik belge üretilir, ardından bu belge embed edilerek
        ChromaDB'de en yakın tool'lar aranır.

        Fallback: Belge üretilemezse standart semantic search kullanılır.

        Returns: [(tool_name, distance), ...] — düşük distance = yüksek benzerlik
        """
        hypothetical_doc = self.generate_hypothetical_document(query)

        if hypothetical_doc:
            # Hipotetik belgeyi sorgu olarak kullan
            search_query = hypothetical_doc
        else:
            # Fallback: orijinal sorguyu kullan
            search_query = query

        results = self.semantic_search.collection.query(
            query_texts=[search_query],
            n_results=min(n_results, self.semantic_search.collection.count()),
        )

        matches: List[Tuple[str, float]] = []
        if results and results["ids"] and results["distances"]:
            for tool_id, distance in zip(results["ids"][0], results["distances"][0]):
                matches.append((tool_id, distance))

        return matches

    def get_semantic_scores(
        self, query: str, tool_names: Optional[List[str]] = None
    ) -> Dict[str, float]:
        """
        HyDE yaklaşımıyla semantic benzerlik skorlarını döndürür.
        Cosine distance'ı similarity'ye çevirir: similarity = 1 - distance

        Returns: {tool_name: similarity_score, ...}  (0.0 - 1.0 arası)
        """
        all_results = self.search(query, n_results=self.semantic_search.collection.count())

        scores: Dict[str, float] = {}
        for tool_name, distance in all_results:
            similarity = max(0.0, 1.0 - distance)
            scores[tool_name] = similarity

        if tool_names is not None:
            scores = {name: scores.get(name, 0.0) for name in tool_names}

        return scores

    def get_stats(self) -> Dict[str, int]:
        """HyDE istatistiklerini döndürür."""
        return dict(self._stats)
