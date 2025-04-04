import streamlit as st
from src.utils.text_processing import process_text_file
from src.services.pinecone_service import PineconeService
from src.components.file_upload import render_file_upload
from src.components.chat import render_chat
from src.components.settings import render_settings
from src.components.prompts import render_prompt_management
from src.config.settings import DEFAULT_SYSTEM_PROMPT, DEFAULT_RESPONSE_TEMPLATE

# セッション状態の初期化
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_page" not in st.session_state:
    st.session_state.current_page = "chat"
if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = DEFAULT_SYSTEM_PROMPT
if "response_template" not in st.session_state:
    st.session_state.response_template = DEFAULT_RESPONSE_TEMPLATE

# Pineconeサービスの初期化
pinecone_service = PineconeService()

def read_file_content(file) -> str:
    """ファイルの内容を適切なエンコーディングで読み込む"""
    encodings = ['utf-8', 'shift-jis', 'cp932', 'euc-jp']
    content = file.getvalue()
    
    for encoding in encodings:
        try:
            return content.decode(encoding)
        except UnicodeDecodeError:
            continue
    
    raise ValueError("ファイルのエンコーディングを特定できませんでした。UTF-8、Shift-JIS、CP932、EUC-JPのいずれかで保存されているファイルをアップロードしてください。")

def main():
    # サイドバーにメニューを配置
    with st.sidebar:
        st.title("メニュー")
        page = st.radio(
            "機能を選択",
            ["チャット", "ファイルアップロード", "プロンプト管理", "設定"],
            index={
                "chat": 0,
                "upload": 1,
                "prompts": 2,
                "settings": 3
            }[st.session_state.current_page]
        )
        st.session_state.current_page = {
            "チャット": "chat",
            "ファイルアップロード": "upload",
            "プロンプト管理": "prompts",
            "設定": "settings"
        }[page]

    # メインコンテンツの表示
    if st.session_state.current_page == "chat":
        render_chat(pinecone_service)
    elif st.session_state.current_page == "upload":
        render_file_upload(pinecone_service)
    elif st.session_state.current_page == "prompts":
        render_prompt_management()
    else:
        render_settings(pinecone_service)

if __name__ == "__main__":
    main()
