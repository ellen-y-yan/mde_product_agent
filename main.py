# main.py (Azure OpenAI version)

from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, ServiceContext
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
from llama_index.llms.azure_openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from pathlib import Path
import os

# ---- Azure OpenAI Config ----
aoai_endpoint = "https://msechackathon-eastus2.openai.azure.com/"
model = "gpt-4o"
api_version = "2025-01-01-preview"
token_provider = get_bearer_token_provider(DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default")

# ---- LLM and Embedding Setup ----
llm = AzureOpenAI(
    model=model,
    api_version=api_version,
    azure_endpoint=aoai_endpoint,
    azure_ad_token_provider=token_provider
)

embed_model = AzureOpenAIEmbedding(
    model="text-embedding-ada-002",  # or whatever model you've deployed
    api_version=api_version,
    azure_endpoint=aoai_endpoint,
    azure_ad_token_provider=token_provider
)

service_context = ServiceContext.from_defaults(llm=llm, embed_model=embed_model)

# ---- Directories ----
data_dir = Path("data")
business_dir = Path("business_context")
updates_dir = Path("update_logs")

# ---- Load Data ----
kql_docs = SimpleDirectoryReader(input_files=[data_dir / "kql_combined.json"]).load_data()
schema_docs = SimpleDirectoryReader(input_files=[data_dir / "DeviceTVMInfoGathering_Schema.md"]).load_data()
business_docs = SimpleDirectoryReader(input_dir=business_dir).load_data()
update_docs = SimpleDirectoryReader(input_dir=updates_dir).load_data()

# ---- Indexing ----
kql_index = VectorStoreIndex.from_documents(kql_docs, service_context=service_context)
schema_index = VectorStoreIndex.from_documents(schema_docs, service_context=service_context)
business_index = VectorStoreIndex.from_documents(business_docs, service_context=service_context)
updates_index = VectorStoreIndex.from_documents(update_docs, service_context=service_context)

# ---- Query Engines ----
kql_engine = kql_index.as_query_engine(similarity_top_k=3)
schema_engine = schema_index.as_query_engine(similarity_top_k=2)
business_engine = business_index.as_query_engine(similarity_top_k=2)
updates_engine = updates_index.as_query_engine(similarity_top_k=2)

# ---- Demo CLI ----
def chat():
    print("\n💬 Ask a question about Defender data, schema, or updates.")
    while True:
        query = input("\nYou: ")
        if query.lower() in ["exit", "quit"]:
            break

        print("\n--- KQL Answer ---")
        print(kql_engine.query(query))

        print("\n--- Schema Context ---")
        print(schema_engine.query(query))

        print("\n--- Business Context ---")
        print(business_engine.query(query))

        print("\n--- Update Logs ---")
        print(updates_engine.query(query))

if __name__ == "__main__":
    chat()
