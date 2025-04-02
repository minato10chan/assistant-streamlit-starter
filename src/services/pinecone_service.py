from typing import List, Dict, Any
from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI
from ..config.settings import (
    PINECONE_API_KEY,
    PINECONE_INDEX_NAME,
    OPENAI_API_KEY,
    EMBEDDING_MODEL,
    BATCH_SIZE
)

class PineconeService:
    def __init__(self):
        """Pineconeサービスの初期化"""
        # OpenAIクライアントの初期化
        self.openai_client = OpenAI(api_key=OPENAI_API_KEY)
        
        # Pineconeの初期化
        self.pc = Pinecone(api_key=PINECONE_API_KEY)
        
        # インデックスの取得（存在しない場合は作成）
        try:
            self.index = self.pc.Index(PINECONE_INDEX_NAME)
        except Exception:
            # インデックスが存在しない場合は作成
            spec = ServerlessSpec(
                cloud="aws",
                region="us-west-2"
            )
            self.pc.create_index(
                name=PINECONE_INDEX_NAME,
                dimension=1536,  # OpenAIの埋め込みモデルの次元数
                metric="cosine",
                spec=spec
            )
            # 作成したインデックスを取得
            self.index = self.pc.Index(PINECONE_INDEX_NAME)

    def get_embedding(self, text: str) -> List[float]:
        """テキストの埋め込みベクトルを取得"""
        response = self.openai_client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text
        )
        return response.data[0].embedding

    def upload_chunks(self, chunks: List[Dict[str, Any]], batch_size: int = 100) -> None:
        """チャンクをPineconeにアップロード"""
        # チャンクをバッチに分割
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            
            # バッチ内の各チャンクの埋め込みベクトルを取得
            vectors = []
            for chunk in batch:
                vector = self.get_embedding(chunk["text"])
                vectors.append({
                    "id": chunk["id"],
                    "values": vector,
                    "metadata": {
                        "text": chunk["text"]
                    }
                })
            
            # バッチをアップロード
            self.index.upsert(vectors=vectors)

    def query(self, query_text: str, top_k: int = 3) -> Any:
        """クエリに基づいて類似チャンクを検索"""
        query_vector = self.get_embedding(query_text)
        results = self.index.query(
            vector=query_vector,
            top_k=top_k,
            include_metadata=True
        )
        return results

    def get_index_stats(self) -> Dict[str, Any]:
        """インデックスの統計情報を取得"""
        try:
            stats = self.index.describe_index_stats()
            return {
                "total_vector_count": stats.total_vector_count,
                "dimension": stats.dimension,
                "index_name": stats.name,
                "metric": stats.metric
            }
        except Exception as e:
            raise Exception(f"インデックスの統計情報の取得に失敗しました: {str(e)}")

    def clear_index(self) -> None:
        """インデックスをクリア"""
        try:
            self.index.delete(delete_all=True)
        except Exception as e:
            raise Exception(f"インデックスのクリアに失敗しました: {str(e)}") 