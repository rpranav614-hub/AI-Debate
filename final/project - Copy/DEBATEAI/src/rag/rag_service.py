import os
import json
from typing import List, Dict, Any, Optional
from src.config.settings import settings

try:
    from sentence_transformers import SentenceTransformer
    import chromadb
    from chromadb.utils import embedding_functions
    HAS_RAG_DEPS = True
except ImportError:
    HAS_RAG_DEPS = False
    print("⚠️ RAG dependencies not installed. Run: pip install chromadb sentence-transformers")

class RAGService:
    """Service for Retrieval-Augmented Generation"""
    
    def __init__(self):
        self.documents = []
        self.embeddings = None
        self.collection = None
        self.client = None
        self._initialize()
    
    def _initialize(self):
        """Initialize the RAG system"""
        if not HAS_RAG_DEPS:
            print("⚠️ Using fallback mode (no RAG)")
            self._initialize_fallback()
            return
        
        try:
            # Initialize ChromaDB
            os.makedirs(settings.chroma_persist_dir, exist_ok=True)
            self.client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
            
            # Get or create collection with embedding function
            self.collection = self.client.get_or_create_collection(
                name=settings.collection_name,
                embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(
                    model_name='all-MiniLM-L6-v2'
                )
            )
            
            # Add sample documents if collection is empty
            if self.collection.count() == 0:
                self._add_sample_documents()
            
            print(f"✅ RAG initialized with {self.collection.count()} documents")
            
        except Exception as e:
            print(f"⚠️ RAG initialization failed: {e}")
            self._initialize_fallback()
    
    def _add_sample_documents(self):
        """Add sample documents to the collection"""
        sample_docs = [
            ("Microservices allow independent deployment and scaling of services. This improves scalability and team autonomy.", {"source": "architecture", "topic": "microservices"}),
            ("Monolithic architecture is simpler to develop and deploy. All code is in one codebase, making debugging and testing easier.", {"source": "architecture", "topic": "monolithic"}),
            ("Cloud migration requires careful planning, security considerations, and cost analysis. Start with a pilot project.", {"source": "cloud", "topic": "migration"}),
            ("Remote work increases productivity and access to global talent but reduces team culture and collaboration.", {"source": "hr", "topic": "remote"}),
            ("AI adoption requires investment in data infrastructure, talent, and training. ROI typically takes 2-3 years.", {"source": "ai", "topic": "adoption"}),
            ("The Strangler Fig pattern allows incremental migration from monolith to microservices. Replace pieces gradually.", {"source": "architecture", "topic": "migration_pattern"}),
            ("AWS offers comprehensive cloud services including EC2, S3, Lambda, and RDS. Best for enterprises.", {"source": "cloud", "topic": "aws"}),
            ("Azure provides seamless integration with Microsoft products. Best for Windows-based applications.", {"source": "cloud", "topic": "azure"}),
            ("Security in distributed systems requires service-to-service authentication and proper IAM policies.", {"source": "security", "topic": "distributed_systems"}),
            ("Container orchestration with Kubernetes helps manage microservices at scale.", {"source": "devops", "topic": "kubernetes"})
        ]
        
        for content, metadata in sample_docs:
            try:
                self.collection.add(
                    documents=[content],
                    metadatas=[metadata],
                    ids=[f"doc_{hash(content)}"]
                )
            except Exception as e:
                pass
        
        print(f"✅ Added {len(sample_docs)} sample documents")
    
    def _initialize_fallback(self):
        """Fallback mode - use keyword search"""
        self.documents = [
            {
                "id": "doc1",
                "content": "Microservices improve scalability and allow independent deployment. Each service can be developed, deployed, and scaled independently.",
                "metadata": {"source": "architecture_guide", "topic": "benefits"}
            },
            {
                "id": "doc2",
                "content": "Microservices increase operational complexity. You need distributed tracing, service discovery, API gateways, and container orchestration.",
                "metadata": {"source": "architecture_guide", "topic": "challenges"}
            },
            {
                "id": "doc3",
                "content": "Monolithic architecture is simpler to develop, test, and deploy. All code is in one place, making debugging and monitoring easier.",
                "metadata": {"source": "architecture_guide", "topic": "monolithic"}
            },
            {
                "id": "doc4",
                "content": "The Strangler Fig pattern allows incremental migration from monolith to microservices. Replace pieces of functionality gradually.",
                "metadata": {"source": "migration_guide", "topic": "strategy"}
            },
            {
                "id": "doc5",
                "content": "AWS offers comprehensive cloud services including EC2, S3, Lambda, and RDS. Best for enterprises needing full control.",
                "metadata": {"source": "cloud_guide", "topic": "aws"}
            },
            {
                "id": "doc6",
                "content": "Azure provides seamless integration with Microsoft products. Best for Windows-based applications and enterprise environments.",
                "metadata": {"source": "cloud_guide", "topic": "azure"}
            },
            {
                "id": "doc7",
                "content": "Remote work increases productivity and access to global talent but reduces team culture and collaboration.",
                "metadata": {"source": "hr_guide", "topic": "remote_work"}
            },
            {
                "id": "doc8",
                "content": "AI adoption requires significant investment in infrastructure, data, and talent. ROI typically takes 2-3 years.",
                "metadata": {"source": "ai_guide", "topic": "adoption"}
            },
            {
                "id": "doc9",
                "content": "Cloud migration reduces infrastructure costs but increases operational complexity. Requires careful planning and security consideration.",
                "metadata": {"source": "cloud_guide", "topic": "migration"}
            },
            {
                "id": "doc10",
                "content": "Security in distributed systems requires service-to-service authentication, encryption, and proper IAM policies.",
                "metadata": {"source": "security_guide", "topic": "distributed_systems"}
            }
        ]
        print(f"✅ Fallback RAG initialized with {len(self.documents)} documents")
    
    def add_document(self, content: str, metadata: Dict = None, doc_id: str = None):
        """Add a document to the knowledge base"""
        if not HAS_RAG_DEPS or self.collection is None:
            # Fallback mode
            doc_id = doc_id or f"doc{len(self.documents)+1}"
            self.documents.append({
                "id": doc_id,
                "content": content,
                "metadata": metadata or {}
            })
            print(f"✅ Added document (fallback): {content[:50]}...")
            return
        
        try:
            doc_id = doc_id or f"doc_{hash(content)}"
            metadata = metadata or {"source": "user_added"}
            
            self.collection.add(
                documents=[content],
                metadatas=[metadata],
                ids=[doc_id]
            )
            print(f"✅ Added document: {content[:50]}...")
        except Exception as e:
            print(f"⚠️ Error adding to ChromaDB, using fallback: {e}")
            # Fallback: store locally
            doc_id = doc_id or f"doc{len(self.documents)+1}"
            self.documents.append({
                "id": doc_id,
                "content": content,
                "metadata": metadata or {}
            })
    
    def add_documents(self, documents: List[str], metadatas: List[Dict] = None):
        """Add multiple documents"""
        for i, doc in enumerate(documents):
            metadata = metadatas[i] if metadatas and i < len(metadatas) else {"source": f"doc_{i}"}
            self.add_document(doc, metadata, f"doc_{i+1}")
    
    def search(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """Search for relevant documents"""
        # If no ChromaDB, use fallback
        if not HAS_RAG_DEPS or self.collection is None:
            return self._keyword_search(query, k)
        
        try:
            # Query ChromaDB
            results = self.collection.query(
                query_texts=[query],
                n_results=max(k, 5)  # Get more results for better ranking
            )
            
            if results and results['documents'] and len(results['documents']) > 0:
                docs = results['documents'][0]
                metadatas = results['metadatas'][0] if results['metadatas'] and results['metadatas'][0] else []
                distances = results['distances'][0] if results['distances'] and results['distances'][0] else []
                
                formatted_results = []
                for i in range(len(docs)):
                    # Calculate score (0-1, higher is better)
                    score = 1 - (distances[i] / 2) if distances and i < len(distances) else 0.5
                    score = max(0, min(1, score))  # Clamp between 0 and 1
                    
                    formatted_results.append({
                        "content": docs[i],
                        "metadata": metadatas[i] if metadatas and i < len(metadatas) else {},
                        "distance": distances[i] if distances and i < len(distances) else 0,
                        "score": score
                    })
                
                # Sort by score and return top k
                formatted_results.sort(key=lambda x: x['score'], reverse=True)
                return formatted_results[:k]
            
            return []
            
        except Exception as e:
            print(f"⚠️ Search error: {e}")
            return self._keyword_search(query, k)
    
    def _keyword_search(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """Fallback: simple keyword-based search"""
        query_lower = query.lower()
        query_words = query_lower.split()
        
        results = []
        for doc in self.documents:
            content_lower = doc['content'].lower()
            matches = sum(1 for word in query_words if word in content_lower)
            score = matches / len(query_words) if query_words else 0
            
            if score > 0:
                results.append({
                    "content": doc['content'],
                    "metadata": doc.get('metadata', {}),
                    "score": score,
                    "id": doc.get('id', '')
                })
        
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:k]
    
    def get_context(self, query: str, k: int = 3) -> str:
        """Get context string from search results"""
        results = self.search(query, k)
        if not results:
            return "No relevant information found."
        
        context = "📚 Relevant Information:\n\n"
        for i, result in enumerate(results, 1):
            context += f"{i}. {result['content']}\n"
            if result.get('score', 0) > 0:
                context += f"   (Relevance: {result['score']:.2f})\n"
            context += "\n"
        
        return context
    
    def get_all_documents(self) -> List[Dict[str, Any]]:
        """Get all documents in the knowledge base"""
        if not HAS_RAG_DEPS or self.collection is None:
            return self.documents
        
        try:
            results = self.collection.get()
            if results and results['documents']:
                return [
                    {
                        "content": results['documents'][i],
                        "metadata": results['metadatas'][i] if results['metadatas'] else {},
                        "id": results['ids'][i] if results['ids'] else f"doc_{i}"
                    }
                    for i in range(len(results['documents']))
                ]
            return []
        except Exception as e:
            return self.documents