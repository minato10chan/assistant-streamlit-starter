import streamlit as st
import json
from datetime import datetime
from src.services.pinecone_service import PineconeService
from src.services.langchain_service import LangChainService

def save_chat_history(messages, filename=None):
    """チャット履歴をJSONファイルとして保存"""
    if filename is None:
        filename = f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    # メッセージを保存可能な形式に変換
    save_data = {
        "timestamp": datetime.now().isoformat(),
        "messages": messages
    }
    
    # JSONファイルとして保存
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(save_data, f, ensure_ascii=False, indent=2)
    
    return filename

def load_chat_history(file):
    """チャット履歴をJSONファイルから読み込み"""
    data = json.load(file)
    return data.get("messages", [])

def render_chat(pinecone_service: PineconeService):
    """チャット機能のUIを表示"""
    st.title("チャット")
    st.write("アップロードしたドキュメントについて質問できます。")
    
    # LangChainサービスの初期化
    if "langchain_service" not in st.session_state:
        st.session_state.langchain_service = LangChainService()
    
    # サイドバーに履歴管理機能を配置
    with st.sidebar:
        st.header("チャット履歴管理")
        
        # 履歴の保存
        if st.button("現在の履歴を保存"):
            filename = save_chat_history(st.session_state.messages)
            st.success(f"履歴を保存しました: {filename}")
        
        # 履歴の読み込み
        uploaded_file = st.file_uploader("保存した履歴を読み込む", type=['json'])
        if uploaded_file is not None:
            try:
                loaded_messages = load_chat_history(uploaded_file)
                st.session_state.messages = loaded_messages
                st.session_state.langchain_service.clear_memory()
                st.success("履歴を読み込みました")
            except Exception as e:
                st.error(f"履歴の読み込みに失敗しました: {str(e)}")
        
        # 履歴のクリア
        if st.button("履歴をクリア"):
            st.session_state.messages = []
            st.session_state.langchain_service.clear_memory()
            st.success("履歴をクリアしました")
        
        # 履歴の表示
        st.header("会話履歴")
        for i, message in enumerate(st.session_state.messages):
            with st.container():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.text(f"{message['role']}: {message['content'][:50]}...")
                with col2:
                    if st.button("削除", key=f"delete_{i}"):
                        st.session_state.messages.pop(i)
                        st.rerun()
    
    # メインのチャット表示
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            # 詳細情報が含まれている場合は表示
            if "details" in message:
                with st.expander("詳細情報"):
                    st.json(message["details"])

    # ユーザー入力
    if prompt := st.chat_input("メッセージを入力してください"):
        # ユーザーメッセージを表示
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # LangChainを使用して応答を生成
        with st.spinner("応答を生成中..."):
            response, details = st.session_state.langchain_service.get_response(prompt)
            
            # アシスタントの応答を表示
            st.session_state.messages.append({
                "role": "assistant",
                "content": response,
                "details": details
            })
            with st.chat_message("assistant"):
                st.markdown(response)
                with st.expander("詳細情報"):
                    st.json(details) 