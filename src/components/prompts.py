import streamlit as st
import json
from typing import Dict, List
from datetime import datetime
import os

PROMPT_FILE = "prompts.json"
MAX_PROMPT_NAME_LENGTH = 50
MAX_PROMPT_TEXT_LENGTH = 1000

def load_prompts() -> Dict[str, str]:
    """保存されたプロンプトを読み込む"""
    # セッション状態とファイルの両方からプロンプトを管理
    if "prompts" not in st.session_state:
        default_prompt = {
            "default": "あなたは親切なアシスタントです。質問に対して、提供された文脈に基づいて回答してください。文脈に含まれていない情報については、推測せずに「その情報は提供された文脈に含まれていません」と回答してください。"
        }
        
        # ファイルが存在する場合は読み込む
        if os.path.exists(PROMPT_FILE):
            try:
                with open(PROMPT_FILE, 'r', encoding='utf-8') as f:
                    prompts = json.load(f)
                    # デフォルトプロンプトは常に存在することを保証
                    prompts.setdefault("default", default_prompt["default"])
            except Exception as e:
                st.error(f"プロンプトの読み込みに失敗しました: {str(e)}")
                prompts = default_prompt
        else:
            prompts = default_prompt
            
        st.session_state.prompts = prompts
    
    return st.session_state.prompts

def save_prompts(prompts: Dict[str, str]) -> None:
    """プロンプトを保存"""
    try:
        # セッション状態に保存
        st.session_state.prompts = prompts
        
        # ファイルに保存
        with open(PROMPT_FILE, 'w', encoding='utf-8') as f:
            json.dump(prompts, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"プロンプトの保存に失敗しました: {str(e)}")

def validate_prompt_name(name: str) -> tuple[bool, str]:
    """プロンプト名のバリデーション"""
    if not name:
        return False, "プロンプト名を入力してください"
    if len(name) > MAX_PROMPT_NAME_LENGTH:
        return False, f"プロンプト名は{MAX_PROMPT_NAME_LENGTH}文字以内にしてください"
    if name.isspace():
        return False, "プロンプト名に空白文字のみは使用できません"
    return True, ""

def validate_prompt_text(text: str) -> tuple[bool, str]:
    """プロンプト内容のバリデーション"""
    if not text:
        return False, "プロンプト内容を入力してください"
    if len(text) > MAX_PROMPT_TEXT_LENGTH:
        return False, f"プロンプト内容は{MAX_PROMPT_TEXT_LENGTH}文字以内にしてください"
    return True, ""

def render_prompt_management():
    """プロンプト管理のUIを表示"""
    st.title("プロンプト管理")
    
    # プロンプトの読み込み
    prompts = load_prompts()
    
    # 新しいプロンプトの追加
    with st.expander("新しいプロンプトを追加"):
        new_prompt_name = st.text_input(
            "プロンプト名",
            help=f"最大{MAX_PROMPT_NAME_LENGTH}文字まで"
        )
        new_prompt_text = st.text_area(
            "プロンプト内容",
            height=200,
            help=f"最大{MAX_PROMPT_TEXT_LENGTH}文字まで"
        )
        
        if st.button("追加"):
            # 入力値のバリデーション
            name_valid, name_error = validate_prompt_name(new_prompt_name)
            text_valid, text_error = validate_prompt_text(new_prompt_text)
            
            if not name_valid:
                st.error(name_error)
            elif not text_valid:
                st.error(text_error)
            elif new_prompt_name in prompts:
                st.error("同じ名前のプロンプトが既に存在します")
            else:
                prompts[new_prompt_name] = new_prompt_text
                save_prompts(prompts)
                st.success("プロンプトを追加しました")
                # フォームをクリア
                st.experimental_rerun()
    
    # 既存のプロンプトの表示と編集
    st.header("保存されたプロンプト")
    for name, text in prompts.items():
        with st.expander(f"プロンプト: {name}"):
            edited_text = st.text_area(
                "内容",
                value=text,
                height=200,
                key=f"edit_{name}",
                help=f"最大{MAX_PROMPT_TEXT_LENGTH}文字まで"
            )
            
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("更新", key=f"update_{name}"):
                    # 内容のバリデーション
                    text_valid, text_error = validate_prompt_text(edited_text)
                    if not text_valid:
                        st.error(text_error)
                    else:
                        prompts[name] = edited_text
                        save_prompts(prompts)
                        st.success("プロンプトを更新しました")
                        st.experimental_rerun()
            
            with col2:
                if st.button("削除", key=f"delete_{name}"):
                    if name != "default":
                        if st.session_state.get(f"confirm_delete_{name}", False):
                            del prompts[name]
                            save_prompts(prompts)
                            st.success("プロンプトを削除しました")
                            st.experimental_rerun()
                        else:
                            st.session_state[f"confirm_delete_{name}"] = True
                            st.warning("もう一度クリックすると削除されます")
                    else:
                        st.error("デフォルトプロンプトは削除できません") 