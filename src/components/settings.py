import streamlit as st
from src.services.pinecone_service import PineconeService
from src.config.settings import (
    CHUNK_SIZE,
    BATCH_SIZE,
    EMBEDDING_MODEL,
    DEFAULT_TOP_K
)

def render_settings(pinecone_service: PineconeService):
    """設定画面のUIを表示"""
    st.title("設定")
    
    # テキスト処理設定
    st.header("テキスト処理設定")
    chunk_size = st.number_input(
        "チャンクサイズ（文字数）",
        min_value=100,
        max_value=2000,
        value=CHUNK_SIZE,
        help="テキストを分割する際の1チャンクあたりの文字数"
    )
    
    batch_size = st.number_input(
        "バッチサイズ",
        min_value=10,
        max_value=500,
        value=BATCH_SIZE,
        help="Pineconeへのアップロード時のバッチサイズ"
    )

    # 検索設定
    st.header("検索設定")
    top_k = st.number_input(
        "検索結果数",
        min_value=1,
        max_value=10,
        value=DEFAULT_TOP_K,
        help="検索時に返す結果の数"
    )

    # プロンプト設定
    st.header("プロンプト設定")
    system_prompt = st.text_area(
        "システムプロンプト",
        value=st.session_state.get("system_prompt", "あなたは親切なアシスタントです。質問に対して、提供された文脈に基づいて回答してください。"),
        help="アシスタントの基本的な振る舞いを定義するプロンプト"
    )
    
    response_template = st.text_area(
        "応答テンプレート",
        value=st.session_state.get("response_template", "検索結果に基づいて回答します：\n\n{context}"),
        help="検索結果を表示する際のテンプレート。{context}は検索結果に置換されます。"
    )

    # データベース設定
    st.header("データベース設定")
    if st.button("データベースの状態を確認"):
        try:
            stats = pinecone_service.get_index_stats()
            st.json(stats)
        except Exception as e:
            st.error(f"データベースの状態取得に失敗しました: {str(e)}")

    if st.button("データベースをクリア"):
        if st.warning("本当にデータベースをクリアしますか？この操作は取り消せません。"):
            try:
                pinecone_service.clear_index()
                st.success("データベースをクリアしました。")
            except Exception as e:
                st.error(f"データベースのクリアに失敗しました: {str(e)}")

    # 設定の保存
    if st.button("設定を保存"):
        st.session_state.update({
            "chunk_size": chunk_size,
            "batch_size": batch_size,
            "top_k": top_k,
            "system_prompt": system_prompt,
            "response_template": response_template
        })
        st.success("設定を保存しました。") 