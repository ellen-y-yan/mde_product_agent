# generate_index.py
# Save the vector index to disk so it can be reused in other scripts

from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext
from llama_index.core.settings import Settings
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from pathlib import Path

# ---- Azure OpenAI Setup ----
aoai_endpoint = "https://msechackathon-eastus2.openai.azure.com/"
model = "gpt-4o"
api_version = "2025-01-01-preview"
token_provider = get_bearer_token_provider(
    DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
)

# ---- LLM + Embedding Models ----
llm = AzureOpenAI(
    engine = "msechackathon-eastus2",
    model=model,
    api_version=api_version,
    azure_endpoint=aoai_endpoint,
    azure_ad_token_provider=token_provider
)

embed_model = AzureOpenAIEmbedding(
    model="text-embedding-3-large",
    api_version=api_version,
    azure_endpoint=aoai_endpoint,
    azure_ad_token_provider=token_provider
)
Settings.llm = llm
Settings.embed_model = embed_model

# # ---- Load Documents ----
# docs = SimpleDirectoryReader(input_dir="business_context").load_data()


# # ---- Build In-Memory Index ----
# print("Building in-memory vector index...")
# storage_context = StorageContext.from_defaults()
# index = VectorStoreIndex.from_documents(docs, storage_context=storage_context)

# # ---- Save Index to Disk ----
# persist_dir = Path("indexes/business")
# persist_dir.mkdir(parents=True, exist_ok=True)
# index.storage_context.persist(persist_dir=str(persist_dir))


# ---- Index a Folder and Persist It ----
def index_and_save(folder_name: str, persist_subdir: str):
    print(f"\n📦 Indexing: {folder_name}/")
    docs = SimpleDirectoryReader(input_dir=folder_name).load_data()
    storage_context = StorageContext.from_defaults()
    index = VectorStoreIndex.from_documents(docs, storage_context=storage_context)

    persist_dir = Path("indexes") / persist_subdir
    persist_dir.mkdir(parents=True, exist_ok=True)
    index.storage_context.persist(persist_dir=str(persist_dir))
    print(f"✅ Saved index to: {persist_dir}/")

# ---- Index both folders ----
index_and_save("data", "data")
index_and_save("business_context", "business_context")
