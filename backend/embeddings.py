import numpy as np

_model = None

def get_model():
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            print(f"Warning: sentence-transformers not available ({e}), using simple vector fallback.")
            _model = "fallback"
    return _model

def get_embedding(text: str) -> np.ndarray:
    model = get_model()
    if model == "fallback" or model is None:
        # Fallback simple deterministic vector representation for fallback testing
        words = text.lower().split()
        vec = np.zeros(384, dtype=np.float32)
        for idx, word in enumerate(words):
            hash_val = sum(ord(c) for c in word)
            vec[hash_val % 384] += 1.0
        norm = np.linalg.norm(vec)
        return vec / norm if norm > 0 else vec
    
    emb = model.encode(text)
    return np.array(emb, dtype=np.float32)

def get_embeddings(texts: list[str]) -> list[np.ndarray]:
    return [get_embedding(t) for t in texts]
