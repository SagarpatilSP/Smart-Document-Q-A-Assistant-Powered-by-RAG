import faiss
import numpy as np

def create_faiss_index(embeds: np.ndarray):
    dim = embeds.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeds.astype("float32"))
    return index

def retrieve_faiss(query, index, chunks, embed_model, k=5):
    q_emb = embed_model.encode([query], convert_to_numpy=True)[0].astype("float32")
    q_emb = np.array([q_emb])
    D, I = index.search(q_emb, k)
    results = []
    for dist, idx in zip(D[0], I[0]):
        if idx < len(chunks):
            results.append({
                "chunk_id": int(idx),
                "score": float(dist),
                "text": chunks[idx]
            })
    return results