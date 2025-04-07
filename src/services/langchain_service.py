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
    OPENAI_API_KEY,
    DEFAULT_TOP_K,
    SIMILARITY_THRESHOLD,
    DEFAULT_SYSTEM_PROMPT,
    DEFAULT_RESPONSE_TEMPLATE
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
        
        # デフォルトのプロンプトテンプレート
        self.system_prompt = DEFAULT_SYSTEM_PROMPT
        self.response_template = DEFAULT_RESPONSE_TEMPLATE

    def get_relevant_context(self, query: str, top_k: int = DEFAULT_TOP_K) -> Tuple[str, List[Dict[str, Any]]]:
        """クエリに関連する文脈を取得"""
        # より多くの結果を取得して、後でフィルタリング
        docs = self.vectorstore.similarity_search_with_score(query, k=top_k * 2)
        
        # スコアでフィルタリング
        filtered_docs = [
            doc for doc in docs 
            if doc[1] >= SIMILARITY_THRESHOLD
        ][:top_k]  # 上位K件に制限
        
        # フィルタリング後の結果が0件の場合は、スコアに関係なく上位K件を使用
        if not filtered_docs and docs:
            filtered_docs = docs[:top_k]
        
        context_text = "\n".join([doc[0].page_content for doc in filtered_docs])
        search_details = [
            {
                "スコア": round(doc[1], 4),  # 類似度スコアを小数点4桁まで表示
                "テキスト": doc[0].page_content[:100] + "..."  # テキストの一部を表示
            }
            for doc in filtered_docs
        ]
        
        print(f"検索クエリ: {query}")  # デバッグ用
        print(f"検索結果数: {len(filtered_docs)}")  # デバッグ用
        for detail in search_details:
            print(f"スコア: {detail['スコア']}, テキスト: {detail['テキスト']}")  # デバッグ用
        
        return context_text, search_details

    def get_response(self, query: str, system_prompt: str = None, response_template: str = None) -> Tuple[str, Dict[str, Any]]:
        """クエリに対する応答を生成"""
        # プロンプトの設定
        system_prompt = system_prompt or self.system_prompt
        response_template = response_template or self.response_template
        
        # プロンプトテンプレートの設定
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("system", "参照文脈:\n{context}"),
            ("human", "{input}")
        ])
        
        # チェーンの初期化
        chain = prompt | self.llm
        
        # 関連する文脈を取得
        context, search_details = self.get_relevant_context(query)
        
        # チャット履歴を取得
        chat_history = self.message_history.messages
        
        # 応答を生成
        response = chain.invoke({
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
            },
            "プロンプト": {
                "システムプロンプト": system_prompt,
                "応答テンプレート": response_template
            }
        }
        
        return response.content, details

    def clear_memory(self):
        """会話メモリをクリア"""
        self.message_history.clear() 