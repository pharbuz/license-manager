from __future__ import annotations

import os
import sys
from pathlib import Path

# Ensure project root is on sys.path so `import app...` works in tests
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# Minimal env so security/keycloak modules import without real network
os.environ.setdefault("KEYCLOAK_BASE_URL", "http://example.com")
os.environ.setdefault("KEYCLOAK_REALM", "test")
os.environ.setdefault("OPENSEARCH_URL", "http://localhost:9200")
os.environ.setdefault("ENV", "test")
