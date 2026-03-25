"""
ToolAutoLoader — Tool'ları otomatik keşfeden ve kaydeden modül.

`tools/` dizinindeki Python dosyalarını tarar, her birindeki
TOOL_DEFINITIONS listesini okur ve ToolRegistry'ye kaydeder.

Convention:
    Her tool modülü, modül seviyesinde bir TOOL_DEFINITIONS listesi export etmelidir.
    Bu liste, ToolSchema nesnelerinden oluşmalıdır.

Kullanım:
    from ToolAutoLoader import ToolAutoLoader
    from Tool import ToolRegistry

    registry = ToolRegistry()
    loader = ToolAutoLoader()
    stats = loader.load_all(registry)
    print(stats)  # {'loaded': 10, 'failed': 0, 'tools': [...], 'errors': [...]}
"""

import os
import importlib
import importlib.util
from typing import List, Dict, Any

from Tool import ToolSchema, ToolRegistry


class ToolAutoLoader:
    """tools/ dizininden tool tanımlarını otomatik keşfedip yükler."""

    def __init__(self, tools_dir: str = None):
        """
        Args:
            tools_dir: Tool tanımlarının bulunduğu dizin yolu.
                       Varsayılan: bu dosyanın bulunduğu dizindeki 'tools/' klasörü.
        """
        if tools_dir is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            self.tools_dir = os.path.join(base_dir, "tools")
        else:
            self.tools_dir = os.path.abspath(tools_dir)

    def discover_modules(self) -> List[str]:
        """
        tools/ dizinindeki yüklenebilir Python dosyalarını keşfeder.
        __init__.py ve _ ile başlayan dosyalar hariç tutulur.

        Returns:
            Dosya yollarının listesi.
        """
        if not os.path.isdir(self.tools_dir):
            print(f"[!] Tool dizini bulunamadı: {self.tools_dir}")
            return []

        modules = []
        for filename in sorted(os.listdir(self.tools_dir)):
            if (
                filename.endswith(".py")
                and filename != "__init__.py"
                and not filename.startswith("_")
            ):
                modules.append(os.path.join(self.tools_dir, filename))

        return modules

    def load_module(self, module_path: str) -> List[ToolSchema]:
        """
        Tek bir Python modülünü yükler ve içindeki TOOL_DEFINITIONS listesini döndürür.

        Args:
            module_path: Yüklenecek .py dosyasının tam yolu.

        Returns:
            Modüldeki ToolSchema listesi. Hata durumunda boş liste.

        Raises:
            ImportError: Modül yüklenemezse.
            AttributeError: TOOL_DEFINITIONS bulunamazsa.
        """
        module_name = os.path.splitext(os.path.basename(module_path))[0]
        full_module_name = f"tools.{module_name}"

        # importlib.util ile dinamik modül yükleme
        spec = importlib.util.spec_from_file_location(full_module_name, module_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Modül spec oluşturulamadı: {module_path}")

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Convention: modülde TOOL_DEFINITIONS listesi olmalı
        if not hasattr(module, "TOOL_DEFINITIONS"):
            raise AttributeError(
                f"'{module_name}' modülünde TOOL_DEFINITIONS bulunamadı. "
                f"Her tool modülü bir TOOL_DEFINITIONS listesi export etmelidir."
            )

        definitions = module.TOOL_DEFINITIONS

        if not isinstance(definitions, list):
            raise TypeError(
                f"'{module_name}.TOOL_DEFINITIONS' bir liste olmalı, "
                f"ancak {type(definitions).__name__} bulundu."
            )

        # Her elemanın ToolSchema olduğunu doğrula
        valid_tools = []
        for tool in definitions:
            if isinstance(tool, ToolSchema):
                valid_tools.append(tool)
            else:
                print(
                    f"   [!] '{module_name}' modülünde geçersiz tool tanımı atlandı: "
                    f"{type(tool).__name__}"
                )

        return valid_tools

    def load_all(self, registry: ToolRegistry) -> Dict[str, Any]:
        """
        Tüm tool modüllerini keşfeder, yükler ve registry'ye kaydeder.

        Args:
            registry: Tool'ların kaydedileceği ToolRegistry nesnesi.

        Returns:
            Yükleme istatistikleri:
            {
                'loaded': int,       # Başarıyla yüklenen tool sayısı
                'failed': int,       # Başarısız modül sayısı
                'tools': List[str],  # Yüklenen tool isimleri
                'errors': List[str]  # Hata mesajları
            }
        """
        modules = self.discover_modules()

        stats: Dict[str, Any] = {
            "loaded": 0,
            "failed": 0,
            "tools": [],
            "errors": [],
        }

        if not modules:
            print(f"[!] '{self.tools_dir}' dizininde tool modülü bulunamadı.")
            return stats

        print(f"[*] {len(modules)} tool modülü keşfedildi.")

        for module_path in modules:
            module_name = os.path.splitext(os.path.basename(module_path))[0]
            try:
                tools = self.load_module(module_path)

                for tool in tools:
                    registry.register(tool)
                    stats["tools"].append(tool.name)
                    stats["loaded"] += 1
                    print(f"   [+] {tool.name:25s} ({module_name}.py)")

            except Exception as e:
                error_msg = f"{module_name}: {type(e).__name__}: {e}"
                stats["errors"].append(error_msg)
                stats["failed"] += 1
                print(f"   [X] {module_name:25s} HATA — {e}")

        return stats
