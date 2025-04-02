import streamlit as st
from src.services.pinecone_service import PineconeService

def render_chat(pinecone_service: PineconeService):
    """チャット機能のUIを表示"""
    st.title("チャット")
    st.write("アップロードしたドキュメントについて質問できます。")
    
    # チャット履歴の表示
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # ユーザー入力
    if prompt := st.chat_input("メッセージを入力してください"):
        # ユーザーメッセージを表示
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Pineconeで検索
        results = pinecone_service.query(prompt, top_k=st.session_state.get("top_k", 3))
        
        # 検索結果を基にアシスタントの応答を生成
        context = "\n".join([match.metadata["text"] for match in results.matches])
        response = st.session_state.response_template.format(context=context)
        
        # アシスタントの応答を表示
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response) 