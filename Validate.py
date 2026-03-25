import re
from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class ValidationResult:
    is_valid: bool = True
    validated_params: Dict[str, Any] = field(default_factory=dict)
    missing_required: List[str] = field(default_factory=list)
    invalid_params: List[Dict[str, str]] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class ParameterValidator:
    def validate(self, tool: Any, params: Dict[str, Any]) -> ValidationResult:
        result = ValidationResult()

        for param_def in tool.parameters:
            name = getattr(param_def, 'name')
            # Sözlükte anahtar (key) yoksa veya değeri None ise Python'da undefined'a eşdeğer sayabiliriz
            value = params.get(name)
            is_missing = name not in params

            # Gerekli parametreleri kontrol et
            if getattr(param_def, 'required', False) and is_missing:
                result.missing_required.append(name)
                result.is_valid = False
                continue

            # Varsayılan değerleri (default) uygula
            if is_missing and getattr(param_def, 'default', None) is not None:
                result.validated_params[name] = getattr(param_def, 'default')
                continue

            # Eksik (undefined/None) olan isteğe bağlı parametreleri atla
            if is_missing or value is None:
                continue

            # Tip doğrulama
            expected_type = getattr(param_def, 'type', 'any')
            if not self._validate_type(value, expected_type):
                actual_type = type(value).__name__
                result.invalid_params.append({
                    "name": name,
                    "reason": f"Expected {expected_type}, got {actual_type}"
                })
                result.is_valid = False
                continue

            # Enum doğrulama
            enum_list = getattr(param_def, 'enum', None)
            if enum_list and value not in enum_list:
                enum_str = ", ".join(str(e) for e in enum_list)
                result.invalid_params.append({
                    "name": name,
                    "reason": f"Value must be one of: {enum_str}"
                })
                result.is_valid = False
                continue

            # Desen (Pattern - Regex) doğrulama
            pattern = getattr(param_def, 'pattern', None)
            if pattern and isinstance(value, str):
                if not re.search(pattern, value):
                    result.invalid_params.append({
                        "name": name,
                        "reason": f"Value does not match pattern: {pattern}"
                    })
                    result.is_valid = False
                    continue

            result.validated_params[name] = value

        # Ekstra parametreleri kontrol et (sadece uyarı verir)
        defined_params = {getattr(p, 'name') for p in tool.parameters}
        for key in params.keys():
            if key not in defined_params:
                result.warnings.append(f"Unknown parameter: {key}")

        return result

    def _validate_type(self, value: Any, expected_type: str) -> bool:
        if expected_type == 'string':
            return isinstance(value, str)
        elif expected_type == 'number':
            # Python'da bool, int'in alt sınıfı olduğu için bool nesnelerini dışlıyoruz
            return isinstance(value, (int, float)) and not isinstance(value, bool)
        elif expected_type == 'boolean':
            return isinstance(value, bool)
        elif expected_type == 'array':
            return isinstance(value, list)
        elif expected_type == 'object':
            # TypeScript'teki "object" JSON objesine denk geldiği için Python'da dict ile eşleştirilir
            return isinstance(value, dict)
        
        # 'any' veya bilinmeyen bir tip gelirse geçerli say
        return True