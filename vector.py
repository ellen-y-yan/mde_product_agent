# vector.py
# Manually evaluate vector index performance using saved indexes and sample queries

import sys
from pathlib import Path
from llama_index.core import StorageContext, load_index_from_storage
from llama_index.core.settings import Settings
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

# ---- Azure OpenAI Setup ----
aoai_endpoint = "https://msechackathon-eastus2.openai.azure.com/"
model = "gpt-4o"
api_version = "2025-01-01-preview"
token_provider = get_bearer_token_provider(
    DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
)



# 🔍 Debug
from inspect import isfunction
print("✅ Token provider set:", token_provider is not None and isfunction(token_provider))


# ---- Set Global Settings ----
Settings.llm = AzureOpenAI(
    ##engine = "msechackathon-eastus2",
    deployment_name="gpt-4o",
    api_version=api_version,
    azure_endpoint=aoai_endpoint,
    azure_ad_token_provider=token_provider,
    use_azure_ad=True
)

Settings.embed_model = AzureOpenAIEmbedding(
    model="text-embedding-3-large",  # Use your Azure deployment name
    api_version=api_version,
    azure_endpoint=aoai_endpoint,
    azure_ad_token_provider=token_provider,
    use_azure_ad=True
)

# ---- Load Vector Index from Disk ----
def load_index(name):
    index_dir = Path("indexes") / name
    storage_context = StorageContext.from_defaults(persist_dir=str(index_dir))
    index = load_index_from_storage(storage_context)
    return index.as_query_engine(similarity_top_k=3)

# ---- Available Indexes ----
available_indexes = {
    "business": load_index("business"),
    "data": load_index("data"),
    "update_logs": load_index("update_logs")
}

# ---- Sample Queries ----
sample_queries = [
    "What does AvMode 0 mean?",
    "How frequently does Microsoft Defender update its signatures?",
    "What are the latest changes in Windows Defender platform?",
    "How is device health evaluated?",
    "What is AV Signature Ring 5?",
    "How is TvmInfoGathering used in KQL queries?"
]

# ---- Interactive CLI ----
def main():
    print("\nAvailable indexes: business, data, update_logs")
    target = input("Which index would you like to query? ").strip().lower()
    if target not in available_indexes:
        print("❌ Invalid index name. Choose from: business, data, update_logs")
        return

    engine = available_indexes[target]
    print(f"\n💬 Now querying the '{target}' index. Type 'exit' to quit.")
    print("Try one of these:")
    for q in sample_queries:
        print("-", q)

    while True:
        query = input("\nYou: ")
        if query.lower() in ["exit", "quit"]:
            break
        response = engine.query(query)
        print("\n--- Answer ---\n")
        print(response)

if __name__ == "__main__":
    main()
