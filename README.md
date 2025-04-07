# assistant-streamlit-starter

This is a template repository for creating a [Streamlit](https://streamlit.io/) app to interact with PDF and text files with natural language. Content is processed and queried against with [Pinecone Assistant](https://www.pinecone.io/blog/pinecone-assistant/).

## ローカル環境でのセットアップ

### 1. 仮想環境の作成と有効化

```shell
# Windowsの場合
# PowerShellを開いて以下のコマンドを順番に実行
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
python -m venv .venv
.venv\Scripts\Activate.ps1

# macOS/Linuxの場合
# ターミナルを開いて以下のコマンドを順番に実行
python -m venv .venv
source .venv/bin/activate
```

### 2. 必要なパッケージのインストール

```shell
# 仮想環境が有効化されていることを確認（プロンプトの先頭に(.venv)が表示されているはず）
# 以下のコマンドを実行
pip install -r requirements.txt
```

### 3. 環境変数の設定

```shell
# Windowsの場合
copy .env.template .env

# macOS/Linuxの場合
cp .env.template .env
```

`.env`ファイルを開いて、以下の環境変数を設定してください：
```
PINECONE_API_KEY=your_api_key_here
PINECONE_ASSISTANT_NAME=your_assistant_name_here
```

### 4. アプリケーションの実行

```shell
# 以下のコマンドを実行
streamlit run streamlit_app.py
```

アプリケーションが起動したら、ブラウザで http://localhost:8501 にアクセスしてください。

## Configuration

### Install packages

1. For best results, create a [Python virtual environment](https://realpython.com/python-virtual-environments-a-primer/) with 3.10 or 3.11 and reuse it when running any file in this repo.
2. Run

```shell
pip install -r requirements.txt
```

### Environment Variables

Copy `.env.template` to `.env` and `.streamlit/secrets.toml.template` to `.streamlit/secrets.toml`. Fill in your [Pinecone API key](https://app.pinecone.io/organizations/-/projects/-/keys) and the name you want to call your Assistant. The `.env` file will be used by the Jupyter notebook for processing the data and upserting it to Pinecone, whereas `secrets.toml` will be used by Streamlit when running locally.

## Setup Assistant

1. In the [console](https://app.pinecone.io/organizations/-/projects/-/assistant), accept the Terms of Service for Pinecone Assistant.

2. Run all cells in the "assistant-starter" Jupyter notebook to create an assistant and upload files to it.
> [!NOTE]
> If you prefer to create an assistant and upload your files via the UI, skip the notebook and continue to the next section.

## Test the app locally

### [OPTIONAL] Configure the app

In the `streamlit_app.py` file:

- Set your preferred title on [line 18](https://github.com/pinecone-field/assistant-streamlit-starter/blob/f5091cbe5a9bb0fc31f327cda47830824d7a168b/streamlit_app.py#L18)
- Set your preferred prompt on [line 21](https://github.com/pinecone-field/assistant-streamlit-starter/blob/f5091cbe5a9bb0fc31f327cda47830824d7a168b/streamlit_app.py#L21)
- Set your preferred button label on [line 24](https://github.com/pinecone-field/assistant-streamlit-starter/blob/f5091cbe5a9bb0fc31f327cda47830824d7a168b/streamlit_app.py#L24)
- Set your preferred success message on [line 49](https://github.com/pinecone-field/assistant-streamlit-starter/blob/f5091cbe5a9bb0fc31f327cda47830824d7a168b/streamlit_app.py#L49)
- Set your preferred failure message on [line 53](https://github.com/pinecone-field/assistant-streamlit-starter/blob/f5091cbe5a9bb0fc31f327cda47830824d7a168b/streamlit_app.py#L53)

### Run the app

1. Validate that Streamlit is [installed](#install-packages) correctly by running

```shell
streamlit hello
```

You should see a welcome message and the demo should automatically open in your browser. If it doesn't open automatically, manually go to the **Local URL** listed in the terminal output.

2. If the demo ran correctly, run

```shell
streamlit run streamlit_app.py
```

3. Confirm that your app looks good and test queries return successful responses. If so, move on to deployment!

## Deploy the app

1. Create and login to a [Streamlit Community Cloud](https://share.streamlit.io) account.
2. Link your Github account in Workspace settings.
3. On the dashboard, click "New app".
4. Select your Github repo and branch, then enter the filename `streamlit_app.py`.
5. [OPTIONAL] Set your preferred app URL.
6. In "Advanced settings...":
   - Change the Python version to match the one you tested locally
   - Copy the contents of your `secrets.toml` file into "Secrets"
   - Click "Save"
7. Click "Deploy"
