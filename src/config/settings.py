"""
アプリケーションの設定を管理するモジュール
"""

import streamlit as st

# API Keys
PINECONE_API_KEY = st.secrets["pinecone_key"]
OPENAI_API_KEY = st.secrets["openai_api_key"]

# Pinecone Settings
PINECONE_INDEX_NAME = st.secrets["index_name"]

# Text Processing Settings
CHUNK_SIZE = 500  # テキストを分割する際の1チャンクあたりの文字数
BATCH_SIZE = 100  # Pineconeへのアップロード時のバッチサイズ

# OpenAI Settings
EMBEDDING_MODEL = "text-embedding-ada-002"  # 使用する埋め込みモデル

# Prompt Settings
DEFAULT_SYSTEM_PROMPT = """あなたは親切なアシスタントです。
質問に対して、提供された文脈に基づいて回答してください。
文脈に含まれていない情報については、推測せずに「その情報は提供された文脈に含まれていません」と回答してください。"""

DEFAULT_RESPONSE_TEMPLATE = """検索結果に基づいて回答します：

{context}

この回答は、アップロードされたドキュメントの内容に基づいています。"""

# Search Settings
DEFAULT_TOP_K = 3  # デフォルトの検索結果数 