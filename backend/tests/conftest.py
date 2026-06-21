import sys
import os
from unittest.mock import MagicMock, AsyncMock
from types import ModuleType

# Resolve name shadowing by pre-emptively registering local 'tests' package in sys.modules
local_tests_dir = os.path.abspath(os.path.dirname(__file__))
local_backend_dir = os.path.abspath(os.path.join(local_tests_dir, ".."))

# Pre-register local tests module
m = ModuleType('tests')
m.__path__ = [local_tests_dir]
m.__file__ = os.path.join(local_tests_dir, '__init__.py')
sys.modules['tests'] = m

# Add backend and tests directories to front of sys.path
sys.path.insert(0, local_tests_dir)
sys.path.insert(0, local_backend_dir)

# Mock heavy ML packages to speed up test collection and execution
sys.modules['keybert'] = MagicMock()
sys.modules['sentence_transformers'] = MagicMock()
sys.modules['hdbscan'] = MagicMock()

# Mock keybert and sentence_transformers classes if they are imported/instantiated
class MockKeyBERT:
    def __init__(self, *args, **kwargs):
        pass
    def extract_keywords(self, *args, **kwargs):
        return [("mock", 0.9)]

class MockSentenceTransformer:
    def __init__(self, *args, **kwargs):
        pass
    def encode(self, *args, **kwargs):
        import numpy as np
        return np.zeros(384)

# Set them in sys.modules
sys.modules['keybert'].KeyBERT = MockKeyBERT
sys.modules['sentence_transformers'].SentenceTransformer = MockSentenceTransformer
