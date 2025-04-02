from typing import List, Dict, Any, Tuple
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

class LangChainService:
    def __init__(self):
        """LangChainサービスの初期化"""
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
        
        # プロンプトテンプレートの設定
        prompt = ChatPromptTemplate.from_messages([
            ("system", """あなたは文脈に基づいて質問に答えるアシスタントです。
            以下の文脈から関連する情報を探し、それに基づいて回答してください。
            文脈に含まれていない情報については、推測せずに「その情報は提供された文脈に含まれていません」と回答してください。"""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("system", "参照文脈:\n{context}"),
            ("human", "{input}")
        ])
        
        # チェーンの初期化
        self.chain = prompt | self.llm

    def get_relevant_context(self, query: str, top_k: int = 3) -> Tuple[str, List[Dict[str, Any]]]:
        """クエリに関連する文脈を取得"""
        docs = self.vectorstore.similarity_search_with_score(query, k=top_k)
        context_text = "\n".join([doc[0].page_content for doc in docs])
        search_details = [
            {
                "スコア": round(doc[1], 4),  # 類似度スコアを小数点4桁まで表示
                "テキスト": doc[0].page_content[:100] + "..."  # テキストの一部を表示
            }
            for doc in docs
        ]
        return context_text, search_details

    def get_response(self, query: str) -> Tuple[str, Dict[str, Any]]:
        """クエリに対する応答を生成"""
        # 関連する文脈を取得
        context, search_details = self.get_relevant_context(query)
        
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
                "マッチしたチャンク": search_details
            }
        }
        
        return response.content, details

    def clear_memory(self):
        """会話メモリをクリア"""
        self.message_history.clear() 