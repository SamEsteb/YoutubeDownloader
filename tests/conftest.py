"""
Configuración de pytest para los tests.
"""

import sys
from pathlib import Path

# Agregar el directorio src al path
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Agregar también src/app para imports relativos
app_path = src_path / "app"
if str(app_path) not in sys.path:
    sys.path.insert(0, str(app_path))
