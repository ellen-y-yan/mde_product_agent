import os
import sys
from llama_index.core import VectorStoreIndex, StorageContext, load_index_from_storage
from llama_index.core.settings import Settings
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

# --- Azure + LLM Setup ---
aoai_endpoint = "https://msechackathon-eastus2.openai.azure.com/"
api_version = "2025-01-01-preview"
deployment_llm = "gpt-4o"
deployment_embed = "text-embedding-3-large"

token_provider = get_bearer_token_provider(
    DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
)

Settings.llm = AzureOpenAI(
    deployment_name=deployment_llm,
    api_version=api_version,
    azure_endpoint=aoai_endpoint,
    azure_ad_token_provider=token_provider,
    use_azure_ad=True,
)

Settings.embed_model = AzureOpenAIEmbedding(
    deployment_name=deployment_embed,
    api_version=api_version,
    azure_endpoint=aoai_endpoint,
    azure_ad_token_provider=token_provider,
    use_azure_ad=True,
)

# --- Load Schema ---
with open("./data/DeviceTVMInfoGathering_Schema.md", "r", encoding="utf-8") as f:
    schema_context = f.read()

# --- Load Vector Indexes ---
print("[INFO] Loading vector indexes...")

data_index = load_index_from_storage(StorageContext.from_defaults(persist_dir="./indexes/data"))
business_index = load_index_from_storage(StorageContext.from_defaults(persist_dir="./indexes/business"))
updates_index = load_index_from_storage(StorageContext.from_defaults(persist_dir="./indexes/update_logs"))

data_retriever = data_index.as_retriever(similarity_top_k=3)
business_retriever = business_index.as_retriever(similarity_top_k=2)
updates_retriever = updates_index.as_retriever(similarity_top_k=2)

# --- Query Function ---
def generate_kql(nl_query: str):
    data_chunks = data_retriever.retrieve(nl_query)
    business_chunks = business_retriever.retrieve(nl_query)
    update_chunks = updates_retriever.retrieve(nl_query)

    context = "\n\n".join([
        "# From data index:\n" + "\n\n".join(n.node.get_content() for n in data_chunks),
        "# From business index:\n" + "\n\n".join(n.node.get_content() for n in business_chunks),
        "# From update logs index:\n" + "\n\n".join(n.node.get_content() for n in update_chunks),
    ])

    prompt = f"""
You are a Microsoft Defender for Endpoint expert writing Kusto Query Language (KQL).

Use the following table schema and the retrieved context to help answer the user question.

- The table schema is the source of truth for what fields are valid.
- If a concept is mentioned that exists in the business or update context (e.g., 'AvMode = Active'), but not directly in the schema, translate it into the schema-compliant equivalent (e.g., 'AvMode = \"0\"').
- Do not take labels like 'active', 'passive', or 'unknown' at face value—look them up in the context and map to actual schema-compatible values.
- If the mapping cannot be inferred or the schema does not support the concept, return:
  "-- ❌ This request references unsupported fields or concepts not found in the schema."
- When writing conditions, ensure the type matches:
    - Strings should be quoted.
    - Booleans should be written as true/false.
    - DateTimes must use proper datetime() KQL formatting.
    - Null fields should be checked using `== null` or `isnotnull()`.

### Table Schema:
{schema_context}

### User Question:
{nl_query}

### Retrieved Context:
{context}

### Task:
Write a complete KQL query to fulfill the user's request.
Return only the KQL query.
"""


    response = Settings.llm.complete(prompt)
    return response.text.strip()

# --- Run CLI ---
def main():
    print("\n🔎 Ask a question about Defender data (type 'exit' to quit):")
    while True:
        query = input("You: ").strip()
        if query.lower() in ("exit", "quit"): break
        print("\n[INFO] Generating KQL query...")
        try:
            kql = generate_kql(query)
            print("\n--- Generated KQL ---\n")
            print(kql)
        except Exception as e:
            print("[ERROR]", e)

if __name__ == "__main__":
    main()
