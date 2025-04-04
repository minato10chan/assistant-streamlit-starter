from typing import List, Dict, Any, Tuple, Optional
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import HumanMessage, AIMessage
import os
from ..config.settings import (
    PINECONE_API_KEY,
    PINECONE_INDEX_NAME,
    OPENAI_API_KEY
)
import logging
from dataclasses import dataclass
from datetime import datetime

@dataclass
class SearchResult:
    """検索結果を表すデータクラス"""
    content: str
    score: float
    metadata: Dict[str, Any]
    timestamp: datetime = datetime.now()

class LangChainService:
    def __init__(self):
        """LangChainサービスの初期化"""
        # ロガーの設定
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # コンソールハンドラの設定
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        
        # チャットモデルの初期化
        self.llm = ChatOpenAI(
            api_key=OPENAI_API_KEY,
            model_name="gpt-3.5-turbo",
            temperature=0.7
        )
        
        # 埋め込みモデルの初期化
        self.embeddings = OpenAIEmbeddings(
            api_key=OPENAI_API_KEY,
            model="text-embedding-ada-002"
        )
        
        # PineconeのAPIキーを環境変数に設定
        os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY
        
        # Pineconeベクトルストアの初期化
        self.vectorstore = PineconeVectorStore.from_existing_index(
            index_name=PINECONE_INDEX_NAME,
            embedding=self.embeddings
        )
        
        # チャット履歴の初期化
        self.message_history = ChatMessageHistory()
        
        # デフォルトのシステムプロンプト
        self.system_prompt = """あなたは文脈に基づいて質問に答えるアシスタントです。
        以下の文脈から関連する情報を探し、それに基づいて回答してください。
        文脈に含まれていない情報については、推測せずに「その情報は提供された文脈に含まれていません」と回答してください。"""
        
        # プロンプトテンプレートの設定
        self._update_prompt_template()
        
        # 類似度スコアの閾値を設定
        self.similarity_threshold = 0.7

    def _update_prompt_template(self):
        """プロンプトテンプレートを更新"""
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("system", "参照文脈:\n{context}"),
            ("human", "{input}")
        ])
        
        # チェーンの更新
        self.chain = self.prompt | self.llm

    def set_system_prompt(self, prompt: str) -> None:
        """システムプロンプトを設定"""
        self.system_prompt = prompt
        self._update_prompt_template()

    def get_relevant_context(
        self,
        query: str,
        top_k: int = 5,
        min_similarity: Optional[float] = None
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """クエリに関連する文脈を取得"""
        try:
            # 類似度閾値の設定
            threshold = min_similarity or 0.5
            
            # デバッグ情報をログに出力
            self.logger.info(f"=== 検索開始 ===")
            self.logger.info(f"検索クエリ: {query}")
            self.logger.info(f"類似度閾値: {threshold}")
            self.logger.info(f"取得件数: {top_k}")
            
            # ベクトル検索の実行
            docs = self.vectorstore.similarity_search_with_score(query, k=top_k)
            
            # 検索結果の詳細をログに出力
            self.logger.info(f"検索結果数: {len(docs)}")
            for i, (doc, score) in enumerate(docs, 1):
                self.logger.info(f"結果 {i}:")
                self.logger.info(f"  スコア: {score}")
                self.logger.info(f"  メタデータ: {doc.metadata}")
                self.logger.info(f"  内容: {doc.page_content[:200]}...")
            
            # 検索結果の処理
            valid_docs = []
            for doc, score in docs:
                if score >= threshold:
                    valid_docs.append(SearchResult(
                        content=doc.page_content,
                        score=score,
                        metadata=doc.metadata
                    ))
            
            # 検索結果が空の場合の処理
            if not valid_docs:
                self.logger.warning(f"閾値({threshold})以上の検索結果が見つかりませんでした")
                return "", []
            
            # コンテキストの構築
            context_parts = []
            search_details = []
            
            for doc in valid_docs:
                # メタデータから情報を取得
                source = doc.metadata.get('filename', 'Unknown source')
                chunk_id = doc.metadata.get('chunk_id', 'Unknown position')
                
                # コンテキストを構築
                context_parts.append(
                    f"[出典: {source}, 位置: {chunk_id}]\n{doc.content}\n"
                )
                
                # 検索詳細を構築
                search_details.append({
                    "スコア": round(doc.score, 4),
                    "テキスト": self._format_preview(doc.content),
                    "メタデータ": {
                        "ファイル": source,
                        "位置": chunk_id,
                        "タイムスタンプ": doc.timestamp.isoformat()
                    }
                })
            
            # 最終的なコンテキストを作成
            context_text = "\n---\n".join(context_parts)
            
            self.logger.info(f"=== 検索完了 ===")
            self.logger.info(f"有効な検索結果数: {len(valid_docs)}")
            
            return context_text, search_details
            
        except Exception as e:
            self.logger.error(f"検索中にエラーが発生しました: {str(e)}")
            raise RuntimeError(f"文脈の検索中にエラーが発生しました: {str(e)}")

    def _format_preview(self, text: str, max_length: int = 100) -> str:
        """テキストのプレビューを生成"""
        if len(text) <= max_length:
            return text
            
        # 文単位での切り取りを試みる
        sentences = text[:max_length].split('。')
        if len(sentences) > 1:
            return sentences[0] + '。...'
        
        # 文での区切りがない場合は単語単位で
        words = text[:max_length].split()
        if len(words) > 1:
            return ' '.join(words[:-1]) + '...'
            
        # それ以外は単純な切り取り
        return text[:max_length] + '...'

    def get_response(self, query: str) -> Tuple[str, Dict[str, Any]]:
        """クエリに対する応答を生成"""
        try:
            # 関連する文脈を取得
            context, search_details = self.get_relevant_context(query)
            
            # 文脈が見つからない場合の処理
            if not context:
                return (
                    "申し訳ありません。質問に関連する情報が見つかりませんでした。",
                    {
                        "モデル": "GPT-3.5-turbo",
                        "会話履歴": "有効",
                        "文脈検索": {
                            "検索結果数": 0,
                            "マッチしたチャンク": []
                        }
                    }
                )
            
            # チャット履歴を取得
            chat_history = self.message_history.messages
            
            # 応答を生成
            response = self.chain.invoke({
                "chat_history": chat_history,
                "context": context,
                "input": query
            })
            
            # メッセージを履歴に追加
            self.message_history.add_user_message(query)
            self.message_history.add_ai_message(response.content)
            
            # 詳細情報の作成
            details = {
                "モデル": "GPT-3.5-turbo",
                "会話履歴": "有効",
                "文脈検索": {
                    "検索結果数": len(search_details),
                    "マッチしたチャンク": search_details,
                    "検索時刻": datetime.now().isoformat()
                }
            }
            
            return response.content, details
            
        except Exception as e:
            self.logger.error(f"Error generating response: {str(e)}")
            raise RuntimeError(f"応答の生成中にエラーが発生しました: {str(e)}")

    def clear_memory(self):
        """会話メモリをクリア"""
        self.message_history.clear() 