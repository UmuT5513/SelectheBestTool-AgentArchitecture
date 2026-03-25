from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Literal, Set

# Parametre tiplerini kısıtlamak için Literal kullanıyoruz
ParamType = Literal['string', 'number', 'boolean', 'array', 'object']

@dataclass
class ToolParameter:
    name: str
    type: ParamType
    description: str
    required: bool
    default: Any = None
    enum: Optional[List[str]] = None
    pattern: Optional[str] = None

@dataclass
class ToolSchema:
    name: str
    description: str
    category: str
    parameters: List[ToolParameter]
    # returns nesnesini Dict olarak tanımlıyoruz (örn: {"type": "string", "description": "..."})
    returns: Dict[str, str]
    # examples listesini de Dict listesi olarak tutuyoruz
    examples: List[Dict[str, Any]]
    capabilities: List[str]


# --- Tool Registry (Kayıt Defteri) Sınıfı ---

class ToolRegistry:
    def __init__(self):
        # TypeScript'teki Map yerine Python'ın yerleşik sözlük (dict) yapısı kullanılır
        self.tools: Dict[str, ToolSchema] = {}
        # Hızlı arama için Set barındıran yetenek (capability) indeksi
        self.capability_index: Dict[str, Set[str]] = {}

    def register(self, tool: ToolSchema) -> None:
        self.tools[tool.name] = tool

        # Hızlı erişim için capabilities indekslemesi
        for capability in tool.capabilities:
            if capability not in self.capability_index:
                self.capability_index[capability] = set()
            self.capability_index[capability].add(tool.name)

    def get_tool(self, name: str) -> Optional[ToolSchema]:
        # get() metodu anahtar yoksa None döndürür (TS'deki undefined karşılığı)
        return self.tools.get(name)

    def find_by_capability(self, capability: str) -> List[ToolSchema]:
        tool_names = self.capability_index.get(capability, set())
        # Dict içinde mevcut olan araçları listeye çeviriyoruz (.filter(Boolean) mantığı)
        return [self.tools[name] for name in tool_names if name in self.tools]

    def get_all_tools(self) -> List[ToolSchema]:
        return list(self.tools.values())

    def search_tools(self, query: str) -> List[ToolSchema]:
        query_lower = query.lower()
        results: List[ToolSchema] = []
        
        for tool in self.get_all_tools():
            if (query_lower in tool.name.lower() or
                query_lower in tool.description.lower() or
                any(query_lower in cap.lower() for cap in tool.capabilities)):
                results.append(tool)
                
        return results