import streamlit as st
from pinecone import Pinecone
from pinecone_plugins.assistant.models.chat import Message

# configure
pinecone_api_key = st.secrets["pinecone_key"]
assistant_name = st.secrets["assistant_name"]

# connect to Pinecone
pc = Pinecone(api_key=pinecone_api_key)
pinecone_assistant = assistant = pc.assistant.Assistant(
    assistant_name=assistant_name,
)


# streamlit app
def main():
    st.title("Pinecone Assistant")

    # Input for user query
    query = st.text_input("Ask a question:")

    # Button to send query
    if st.button("Submit"):
        if query:
            # Send query to Pinecone index
            answer = query_assistant(query)

            # Display results
            display_answer(answer)


# send a query to Pinecone assistant
def query_assistant(query):
    try:
        chat_context = [Message(content=query)]
        response = assistant.chat_completions(messages=chat_context)
        answer = response["choices"][0]["message"]["content"]
        return answer

    except Exception as e:
        st.error(f"Error querying Pinecone assistant: {e}")
        return None


# display query results
def display_answer(answer):
    if answer:
        st.success("Query successful!")

        st.write(answer)
    else:
        st.warning("No results found.")


if __name__ == "__main__":
    main()
