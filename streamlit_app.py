import streamlit as st
from src.utils.text_processing import process_text_file
from src.services.pinecone_service import PineconeService
from src.components.file_upload import render_file_upload
from src.components.chat import render_chat
from src.components.settings import render_settings
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
try:
    pinecone_service = PineconeService()
    # インデックスの状態を確認
    stats = pinecone_service.get_index_stats()
    if stats['total_vector_count'] == 0:
        st.info("データベースは空です。ファイルをアップロードしてデータを追加してください。")
    else:
        st.write(f"データベースの状態: {stats['total_vector_count']}件のドキュメント")
except Exception as e:
    st.error(f"Pineconeサービスの初期化に失敗しました: {str(e)}")
    st.stop()

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
            ["チャット", "ファイルアップロード", "設定"],
            index={
                "chat": 0,
                "upload": 1,
                "settings": 2
            }[st.session_state.current_page]
        )
        st.session_state.current_page = {
            "チャット": "chat",
            "ファイルアップロード": "upload",
            "設定": "settings"
        }[page]

    # メインコンテンツの表示
    if st.session_state.current_page == "chat":
        render_chat(pinecone_service)
    elif st.session_state.current_page == "upload":
        render_file_upload(pinecone_service)
    else:
        render_settings(pinecone_service)

if __name__ == "__main__":
    main()
