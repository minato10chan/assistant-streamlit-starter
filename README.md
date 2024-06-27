# assistant-streamlit-starter

This is a template repository for creating a [Streamlit](https://streamlit.io/) app to interact with PDF and text files with natural language. Content is processed and queried against with [Pinecone Assistant](https://www.pinecone.io/blog/pinecone-assistant/).

## Configuration

### Install packages

1. For best results, create a [Python virtual environment](https://realpython.com/python-virtual-environments-a-primer/) with 3.10 or 3.11 and reuse it when running any file in this repo.
2. Run

```shell
pip install -r requirements.txt
```

### Environment Variables

Copy `.env.template` to `.env` and `.streamlit/secrets.toml.template` to `.streamlit/secrets.toml`. Fill in your Pinecone API key and the name you want to call your Assistant. The `.env` file will be used by the Jupyter notebook for processing the data and upserting it to Pinecone, whereas `secrets.toml` will be used by Streamlit when running locally.
