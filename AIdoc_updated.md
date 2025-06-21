# RAG Implementation with Gemini

## Overview

This document outlines a Retrieval-Augmented Generation (RAG) pipeline implementation using the Gemini AI model. The RAG system enhances traditional AI responses by retrieving and incorporating relevant information from a knowledge base before generating answers.

## QA Bot Implementation

Below is an example RAG implementation for a Question-Answering (QA) bot:

```python
#!/usr/bin/env python3
"""
QA Bot - A simple question answering bot using RAG (Retrieval-Augmented Generation)
This script creates a command-line interface for a QA bot that can answer questions
about documents loaded from files.
"""

import os
import argparse
from typing import List, Dict, Any

# Import LangChain components
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_community.document_loaders.base import BaseLoader
from langchain_community.vectorstores import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document

# Set API key - replace with your own or set environment variable
os.environ.setdefault('GOOGLE_API_KEY', 'YOUR_API_KEY')

def load_documents(file_path: str) -> List[Document]:
    """Load documents from a file or directory."""
    print(f"Loading documents from: {file_path}")
    
    if os.path.isfile(file_path):
        loader = TextLoader(file_path)
        documents = loader.load()
    elif os.path.isdir(file_path):
        loader = DirectoryLoader(file_path, glob="**/*.txt")
        documents = loader.load()
    else:
        raise ValueError(f"Path {file_path} is neither a file nor a directory.")
    
    print(f"Loaded {len(documents)} document(s)")
    return documents

def process_documents(documents: List[Document], chunk_size: int = 500, chunk_overlap: int = 50) -> List[Document]:
    """Process documents by splitting them into manageable chunks."""
    print("Processing documents...")
    
    # Split the documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    splits = text_splitter.split_documents(documents)
    
    print(f"Split into {len(splits)} chunks")
    return splits

def create_vectorstore(splits: List[Document]) -> Any:
    """Create a vector store from document chunks."""
    print("Creating vector store...")
    
    # Create vector store
    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    )
    
    print("Vector store created successfully")
    return vectorstore

def create_rag_chain(vectorstore: Any) -> Any:
    """Create a RAG chain for answering questions."""
    print("Creating RAG chain...")
    
    # Create retriever
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    
    # Format retrieved documents into context
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)
    
    # Create a prompt template
    prompt = ChatPromptTemplate.from_template(
        """Answer the question based only on the following context:
        {context}
        
        Question: {question}
        
        If the question cannot be answered using the context, indicate that you don't have enough information.
        """
    )
    
    # Set up the LLM
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
    
    # Create the RAG chain
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    print("RAG chain created successfully")
    return rag_chain

def run_interactive_qa(rag_chain: Any):
    """Run an interactive Q&A session using the provided RAG chain."""
    print("\n==== QA Bot Interactive Mode ====")
    print("Type 'exit', 'quit', or 'q' to end the session.")
    
    while True:
        question = input("\nYour question: ")
        
        # Check for exit command
        if question.lower() in ['exit', 'quit', 'q']:
            print("Exiting QA Bot. Goodbye!")
            break
        
        # Answer the question
        print("\nThinking...")
        try:
            answer = rag_chain.invoke(question)
            print(f"\nAnswer: {answer}")
        except Exception as e:
            print(f"Error generating answer: {str(e)}")

def main():
    """Main function to run the QA Bot."""
    parser = argparse.ArgumentParser(description='QA Bot - Answer questions about your documents')
    parser.add_argument('--file', '-f', type=str, required=True, 
                        help='Path to a file or directory containing documents to analyze')
    parser.add_argument('--chunk-size', '-c', type=int, default=500,
                        help='Size of document chunks (default: 500)')
    parser.add_argument('--overlap', '-o', type=int, default=50, 
                        help='Overlap between document chunks (default: 50)')
    
    args = parser.parse_args()
    
    # Load and process documents
    documents = load_documents(args.file)
    splits = process_documents(documents, args.chunk_size, args.overlap)
    
    # Create vector store and RAG chain
    vectorstore = create_vectorstore(splits)
    rag_chain = create_rag_chain(vectorstore)
    
    # Run the interactive QA session
    run_interactive_qa(rag_chain)

if __name__ == "__main__":
    main()
```

## Gemini API Usage

### Basic Text Generation

Here's a basic example that takes a single text input:

```python
from google import genai

client = genai.Client(api_key="GEMINI_API_KEY")

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="How does AI work?"
)
print(response.text)
```

### Thinking with Gemini 2.5

2.5 Flash and Pro models have "thinking" enabled by default to enhance quality, which may take longer to run and increase token usage.

When using 2.5 Flash, you can disable thinking by setting the thinking budget to zero:

```python
from google import genai
from google.genai import types

client = genai.Client(api_key="GEMINI_API_KEY")

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="How does AI work?",
    config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_budget=0) # Disables thinking
    ),
)
print(response.text)
```

### System Instructions and Configurations

You can guide the behavior of Gemini models with system instructions:

```python
from google import genai
from google.genai import types

client = genai.Client(api_key="GEMINI_API_KEY")

response = client.models.generate_content(
    model="gemini-2.5-flash",
    config=types.GenerateContentConfig(
        system_instruction="You are a cat. Your name is Neko."),
    contents="Hello there"
)

print(response.text)
```

The `GenerateContentConfig` object also lets you override default generation parameters, such as temperature:

```python
from google import genai
from google.genai import types

client = genai.Client(api_key="GEMINI_API_KEY")

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=["Explain how AI works"],
    config=types.GenerateContentConfig(
        temperature=0.1
    )
)
print(response.text)
```

### Multimodal Inputs

The Gemini API supports multimodal inputs, allowing you to combine text with media files:

```python
from PIL import Image
from google import genai

client = genai.Client(api_key="GEMINI_API_KEY")

image = Image.open("/path/to/organ.png")
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[image, "Tell me about this instrument"]
)
print(response.text)
```

### Streaming Responses

For more fluid interactions, use streaming to receive responses incrementally:

```python
from google import genai

client = genai.Client(api_key="GEMINI_API_KEY")

response = client.models.generate_content_stream(
    model="gemini-2.5-flash",
    contents=["Explain how AI works"]
)
for chunk in response:
    print(chunk.text, end="")
```

### Multi-turn Conversations (Chat)

Gemini provides functionality to manage conversation history:

```python
from google import genai

client = genai.Client(api_key="GEMINI_API_KEY")
chat = client.chats.create(model="gemini-2.5-flash")

response = chat.send_message("I have 2 dogs in my house.")
print(response.text)

response = chat.send_message("How many paws are in my house?")
print(response.text)

for message in chat.get_history():
    print(f'role - {message.role}',end=": ")
    print(message.parts[0].text)
```

Streaming can also be used for multi-turn conversations:

```python
from google import genai

client = genai.Client(api_key="GEMINI_API_KEY")
chat = client.chats.create(model="gemini-2.5-flash")

response = chat.send_message_stream("I have 2 dogs in my house.")
for chunk in response:
    print(chunk.text, end="")

response = chat.send_message_stream("How many paws are in my house?")
for chunk in response:
    print(chunk.text, end="")

for message in chat.get_history():
    print(f'role - {message.role}', end=": ")
    print(message.parts[0].text)
```

## Best Practices

### Prompting Tips

- For basic text generation, a zero-shot prompt often suffices without needing examples or system instructions
- For more tailored outputs:
  - Use System instructions to guide the model
  - Provide few example inputs and outputs (few-shot prompting)
  - Consult the prompt engineering guide for more tips

## Structured Output

You can configure Gemini for structured output instead of unstructured text, allowing precise extraction and standardization of information.

### Generating JSON

There are two ways to generate JSON using the Gemini API:

1. Configure a schema on the model
2. Provide a schema in a text prompt

#### Configuring a Schema (recommended)

```python
from google import genai
from pydantic import BaseModel

class Recipe(BaseModel):
    recipe_name: str
    ingredients: list[str]

client = genai.Client(api_key="GOOGLE_API_KEY")
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="List a few popular cookie recipes, and include the amounts of ingredients.",
    config={
        "response_mime_type": "application/json",
        "response_schema": list[Recipe],
    },
)
# Use the response as a JSON string.
print(response.text)

# Use instantiated objects.
my_recipes: list[Recipe] = response.parsed
```

## Implementation Components for RAG System

A complete RAG system typically includes the following components:

1. **Document Loaders**: Import documents from various sources
2. **Text Splitters**: Chunk documents into manageable pieces
3. **Embeddings**: Convert text into vector representations
4. **Vector Stores**: Store and retrieve document embeddings
5. **Retrievers**: Find relevant document chunks based on queries
6. **Language Models**: Generate responses using retrieved context
7. **Prompt Templates**: Structure the input for the language model
8. **Output Parsers**: Format the model's response

## Potential AI Agents or Tools

To extend the RAG system, consider implementing:

1. **Document Processor Agent**: Automatically process and update the knowledge base
2. **Query Analyzer Agent**: Refine user questions for better retrieval
3. **Citation Tool**: Track sources of information used in responses
4. **Feedback Loop Tool**: Improve system based on user interactions
5. **Summarization Tool**: Create concise summaries of retrieved documents

## Improvement Areas

To upgrade the existing implementation, consider:

1. Supporting more document formats (PDF, HTML, etc.)
2. Adding metadata filtering for more targeted retrieval
3. Implementing hybrid search (combining keyword and semantic search)
4. Adding result reranking for better relevance
5. Implementing conversational memory for context-aware responses
6. Adding visualization tools for retrieved documents
