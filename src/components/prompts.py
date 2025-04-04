import streamlit as st
import json
from typing import Dict, List

def load_prompts() -> Dict[str, str]:
    """保存されたプロンプトを読み込む"""
    if "prompts" not in st.session_state:
        st.session_state.prompts = {
            "default": "あなたは親切なアシスタントです。質問に対して、提供された文脈に基づいて回答してください。文脈に含まれていない情報については、推測せずに「その情報は提供された文脈に含まれていません」と回答してください。"
        }
    return st.session_state.prompts

def save_prompts(prompts: Dict[str, str]) -> None:
    """プロンプトを保存"""
    st.session_state.prompts = prompts

def render_prompt_management():
    """プロンプト管理のUIを表示"""
    st.title("プロンプト管理")
    
    # プロンプトの読み込み
    prompts = load_prompts()
    
    # 新しいプロンプトの追加
    with st.expander("新しいプロンプトを追加"):
        new_prompt_name = st.text_input("プロンプト名")
        new_prompt_text = st.text_area("プロンプト内容", height=200)
        if st.button("追加"):
            if new_prompt_name and new_prompt_text:
                prompts[new_prompt_name] = new_prompt_text
                save_prompts(prompts)
                st.success("プロンプトを追加しました")
            else:
                st.error("プロンプト名と内容を入力してください")
    
    # 既存のプロンプトの表示と編集
    st.header("保存されたプロンプト")
    for name, text in prompts.items():
        with st.expander(f"プロンプト: {name}"):
            edited_text = st.text_area("内容", value=text, height=200, key=f"edit_{name}")
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("更新", key=f"update_{name}"):
                    prompts[name] = edited_text
                    save_prompts(prompts)
                    st.success("プロンプトを更新しました")
            with col2:
                if st.button("削除", key=f"delete_{name}"):
                    if name != "default":  # デフォルトプロンプトは削除不可
                        del prompts[name]
                        save_prompts(prompts)
                        st.success("プロンプトを削除しました")
                    else:
                        st.error("デフォルトプロンプトは削除できません")
    
    # プロンプトのエクスポート
    st.header("プロンプトのエクスポート/インポート")
    col1, col2 = st.columns([1, 1])
    with col1:
        # エクスポート
        json_data = json.dumps(prompts, ensure_ascii=False, indent=2)
        st.download_button(
            label="プロンプトをエクスポート",
            data=json_data,
            file_name="prompts.json",
            mime="application/json"
        )
    with col2:
        # インポート
        uploaded_file = st.file_uploader("プロンプトをインポート", type=['json'])
        if uploaded_file is not None:
            try:
                imported_prompts = json.load(uploaded_file)
                # デフォルトプロンプトは保持
                default_prompt = prompts.get("default", "")
                prompts.update(imported_prompts)
                if "default" not in prompts:
                    prompts["default"] = default_prompt
                save_prompts(prompts)
                st.success("プロンプトをインポートしました")
            except Exception as e:
                st.error(f"プロンプトのインポートに失敗しました: {str(e)}") 