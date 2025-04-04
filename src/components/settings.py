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
        value=st.session_state.get("chunk_size", CHUNK_SIZE),
        help="テキストを分割する際の1チャンクあたりの文字数"
    )
    
    batch_size = st.number_input(
        "バッチサイズ",
        min_value=10,
        max_value=500,
        value=st.session_state.get("batch_size", BATCH_SIZE),
        help="Pineconeへのアップロード時のバッチサイズ"
    )

    # 検索設定
    st.header("検索設定")
    top_k = st.number_input(
        "検索結果数",
        min_value=1,
        max_value=10,
        value=st.session_state.get("top_k", DEFAULT_TOP_K),
        help="検索時に返す結果の数"
    )

    # データベース設定
    st.header("データベース設定")
    if st.button("データベースの状態を確認"):
        try:
            stats = pinecone_service.get_index_stats()
            
            # 構造化された表示
            col1, col2 = st.columns(2)
            with col1:
                st.metric("保存されているベクトル数", stats["total_vector_count"])
                st.metric("ベクトルの次元数", stats["dimension"])
            with col2:
                st.metric("インデックス名", stats["index_name"])
                st.metric("類似度計算方式", stats["metric"])
            
            # 詳細情報の表示
            with st.expander("詳細情報"):
                st.json(stats)
                
        except ConnectionError as e:
            st.error("データベースへの接続に失敗しました。接続設定を確認してください。")
        except Exception as e:
            st.error(f"データベースの状態取得に失敗しました: {str(e)}")

    # 設定の保存
    if st.button("設定を保存"):
        # 設定値の変更による影響の警告
        if (st.session_state.get("chunk_size") != chunk_size and 
            st.session_state.get("chunk_size") is not None):
            st.warning("チャンクサイズの変更は、新しくアップロードするファイルにのみ適用されます。")
        
        # 設定の保存
        st.session_state.update({
            "chunk_size": chunk_size,
            "batch_size": batch_size,
            "top_k": top_k
        })
        
        # サービスの設定を更新
        try:
            # ここでサービスの設定を更新するメソッドを呼び出す
            st.success("設定を保存しました。")
        except Exception as e:
            st.error(f"設定の保存に失敗しました: {str(e)}") 