"""
アプリケーションの設定を管理するモジュール
"""

import streamlit as st
import os
import json
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# API Keys
PINECONE_API_KEY = st.secrets["pinecone_key"]
OPENAI_API_KEY = st.secrets["openai_api_key"]

# Pinecone Settings
PINECONE_INDEX_NAME = st.secrets["index_name"]
PINECONE_ASSISTANT_NAME = st.secrets["assistant_name"]

# Text Processing Settings
CHUNK_SIZE = 500  # テキストを分割する際の1チャンクあたりの文字数
BATCH_SIZE = 100  # Pineconeへのアップロード時のバッチサイズ

# OpenAI Settings
EMBEDDING_MODEL = "text-embedding-ada-002"  # 使用する埋め込みモデル

# Search Settings
DEFAULT_TOP_K = 10  # デフォルトの検索結果数
SIMILARITY_THRESHOLD = 0.7  # 類似度のしきい値（0-1の範囲）

# Prompt Settings
DEFAULT_SYSTEM_PROMPT = """あなたは親切で丁寧なAIアシスタントです。
ユーザーの質問に対して、以下のルールに従って回答してください：

1. 常に日本語で回答してください
2. 専門的な用語は分かりやすく説明してください
3. 必要に応じて具体例を挙げて説明してください
4. 回答は簡潔かつ明確にしてください
5. ユーザーの理解度に合わせて説明の詳細度を調整してください
"""

DEFAULT_RESPONSE_TEMPLATE = """{question}

回答:
{answer}
"""

# プロンプトテンプレートの設定
DEFAULT_PROMPT_TEMPLATES = [
    {
        "name": "デフォルト",
        "system_prompt": DEFAULT_SYSTEM_PROMPT,
        "response_template": DEFAULT_RESPONSE_TEMPLATE
    },
    {
        "name": "詳細な回答",
        "system_prompt": """あなたは詳細な説明が得意なAIアシスタントです。
ユーザーの質問に対して、以下のルールに従って回答してください：

1. 常に日本語で回答してください
2. 専門的な用語は分かりやすく説明してください
3. 具体例を必ず挙げて説明してください
4. 回答は詳細かつ丁寧にしてください
5. 必要に応じて図や表を使用して説明してください
""",
        "response_template": """質問: {question}

詳細な回答:
{answer}

補足説明:
{additional_info}
"""
    },
    {
        "name": "簡潔な回答",
        "system_prompt": """あなたは簡潔な回答が得意なAIアシスタントです。
ユーザーの質問に対して、以下のルールに従って回答してください：

1. 常に日本語で回答してください
2. 回答は簡潔に、要点のみを述べてください
3. 専門用語は避け、平易な言葉で説明してください
4. 箇条書きや短い文で回答してください
5. 余計な説明は省いてください
""",
        "response_template": """質問: {question}

回答:
{answer}
"""
    }
]

# プロンプトテンプレートの保存と読み込み
PROMPT_TEMPLATES_FILE = "prompt_templates.json"

def save_prompt_templates(templates):
    """プロンプトテンプレートを保存"""
    with open(PROMPT_TEMPLATES_FILE, "w", encoding="utf-8") as f:
        json.dump(templates, f, ensure_ascii=False, indent=2)

def load_prompt_templates():
    """プロンプトテンプレートを読み込み"""
    if os.path.exists(PROMPT_TEMPLATES_FILE):
        with open(PROMPT_TEMPLATES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return DEFAULT_PROMPT_TEMPLATES.copy()

# デフォルトプロンプトの保存と読み込み
DEFAULT_PROMPTS_FILE = "default_prompts.json"

def save_default_prompts(system_prompt, response_template):
    """デフォルトプロンプトを保存"""
    with open(DEFAULT_PROMPTS_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "system_prompt": system_prompt,
            "response_template": response_template
        }, f, ensure_ascii=False, indent=2)

def load_default_prompts():
    """デフォルトプロンプトを読み込み"""
    if os.path.exists(DEFAULT_PROMPTS_FILE):
        with open(DEFAULT_PROMPTS_FILE, "r", encoding="utf-8") as f:
            prompts = json.load(f)
            return prompts["system_prompt"], prompts["response_template"]
    return DEFAULT_SYSTEM_PROMPT, DEFAULT_RESPONSE_TEMPLATE

# デフォルトプロンプトの読み込み
DEFAULT_SYSTEM_PROMPT, DEFAULT_RESPONSE_TEMPLATE = load_default_prompts() 