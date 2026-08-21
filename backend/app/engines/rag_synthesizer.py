import json
import os
from pathlib import Path

class RAGSynthesizer:
    def __init__(self, persist_dir: str = "./chroma_db"):
        self.persist_dir = persist_dir
        self.has_chroma = False
        self.documents = []
        self.metadatas = []
        self.ids = []
        
        try:
            import chromadb
            if not os.path.exists(persist_dir):
                os.makedirs(persist_dir, exist_ok=True)
            self.client = chromadb.PersistentClient(path=persist_dir)
            self.collection = self.client.get_or_create_collection(name="operational_logs")
            self.has_chroma = True
        except Exception:
            self.has_chroma = False
            self.collection = None
        
    def load_documents(self, logs_path: str = None):
        """Loads logs from JSON into vector store / local memory."""
        if logs_path is None:
            base_dir = Path(__file__).resolve().parent.parent.parent
            logs_path = base_dir / "mock_data" / "operational_logs.json"
            
        if not os.path.exists(logs_path):
            print(f"No logs found at {logs_path}")
            return
            
        with open(logs_path, 'r', encoding='utf-8') as f:
            logs = json.load(f)
            
        self.ids = [f"log_{i}" for i in range(len(logs))]
        self.documents = [log['content'] for log in logs]
        self.metadatas = [{
            "source": log['source'],
            "type": log['type'],
            "timestamp": log['timestamp']
        } for log in logs]
            
        if self.has_chroma and self.collection:
            try:
                self.collection.upsert(
                    ids=self.ids,
                    documents=self.documents,
                    metadatas=self.metadatas
                )
            except Exception as e:
                print(f"Chroma upsert error, falling back to local search: {e}")
                self.has_chroma = False
        
    def search_context(self, root_cause_node: str, timestamp_context: str = None, top_k: int = 3) -> list:
        """
        Retrieves logs semantically related to the identified root cause node and time window.
        """
        query_map = {
            "redis_hit_rate": "Redis cache hit rate failure database load primary node failover",
            "db_query_time_ms": "Database query timeout slow database postgres",
            "api_latency_ms": "API latency timeout gateway slow response PagerDuty",
            "checkout_success_rate": "Checkout payment failure cart error spinning",
            "hourly_revenue_usd": "Revenue drop sales down"
        }
        
        query_text = query_map.get(root_cause_node, root_cause_node.replace("_", " "))
        
        if timestamp_context:
            query_text = f"{query_text} {timestamp_context}"
        
        # If ChromaDB is available and has docs
        if self.has_chroma and self.collection:
            try:
                results = self.collection.query(
                    query_texts=[query_text],
                    n_results=top_k
                )
                context = []
                if results['documents'] and results['documents'][0]:
                    for i in range(len(results['documents'][0])):
                        context.append({
                            "content": results['documents'][0][i],
                            "metadata": results['metadatas'][0][i]
                        })
                return context
            except Exception as e:
                print(f"Chroma query failed, using fallback: {e}")
        
        # High-precision Semantic Keyword Matching Fallback
        keywords = set(query_text.lower().split())
        scored_docs = []
        for i, doc in enumerate(self.documents):
            doc_lower = doc.lower()
            score = sum(1 for kw in keywords if kw in doc_lower)
            scored_docs.append((score, i))
            
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        top_matches = scored_docs[:top_k]
        
        context = []
        for score, idx in top_matches:
            if idx < len(self.documents):
                context.append({
                    "content": self.documents[idx],
                    "metadata": self.metadatas[idx]
                })
        return context

rag_synthesizer = RAGSynthesizer()
