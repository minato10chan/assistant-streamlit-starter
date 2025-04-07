import streamlit as st
from src.utils.text_processing import process_text_file
from src.services.pinecone_service import PineconeService

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

def render_file_upload(pinecone_service: PineconeService):
    """ファイルアップロード機能のUIを表示"""
    st.title("ファイルアップロード")
    st.write("テキストファイルをアップロードして、Pineconeデータベースに保存します。")
    
    uploaded_file = st.file_uploader("テキストファイルをアップロード", type=['txt'])
    
    if uploaded_file is not None:
        if st.button("データベースに保存"):
            try:
                with st.spinner("ファイルを処理中..."):
                    file_content = read_file_content(uploaded_file)
                    chunks = process_text_file(file_content, uploaded_file.name)
                    st.write(f"ファイルを{len(chunks)}個のチャンクに分割しました")
                    
                    with st.spinner("Pineconeにアップロード中..."):
                        pinecone_service.upload_chunks(chunks)
                        st.success("アップロードが完了しました！")
            except ValueError as e:
                st.error(str(e))
            except Exception as e:
                st.error(f"エラーが発生しました: {str(e)}") 