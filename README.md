# mde_product_agent


# 💼 Frankly: Microsoft Defender Text-to-KQL with RAG

This project builds a Retrieval-Augmented Generation (RAG) system that translates natural language questions into Kusto Query Language (KQL) for the `DeviceTvmInfoGathering` table in Microsoft Defender.

Powered by Azure OpenAI and LlamaIndex, it allows IT admin and security engineer personas to query Defender insights using plain English.



## 🚀 Features

- 🔎 **Natural language to KQL** conversion
- 📚 **Context-aware reasoning** using business logic and update logs
- 🧠 **Semantic retrieval** from:
  - Data schema
  - Business context
  - Update documentation
- 🧼 Intelligent field mapping
- ❌ Fallback protection when the query is not supported by schema



## 📁 Project Structure

```
mde_product_agent/
├── data/
│   └── Your_database_Schema.md        # Main table schema
│   └── Your_sample_query_and_answer.json        # Sample of 5-10 queries curated questions and answers, ranging from easy to difficult
├── business_context/                           # Business logic markdowns - public documentation markdowns, please remove personal identifiable info from any additional documents you include
├── indexes/
│   ├── business/                               # Persisted vector index 
│   ├── data/
├── generate_index.py                           # Builds vector stores
├── query_with_context.py                                # Main CLI for text-to-KQL
├── vector.py                                   # CLI for exploring context indexes, you can ask business questions here to evaluate the quality of business context here
├── .gitignore                                  # hide necessary files
└── requirements.txt                            # Dependencies
```



## 🛠 Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Authenticate with Azure
```bash
az login
```
Ensure your identity can access Azure OpenAI with Microsoft Entra credentials.

### 3. Generate vector indexes
```bash
python generate_index.py
```
This indexes `business_context`, `update_logs`, and `data` using `text-embedding-3-large`.



## 💬 Run Query CLI
```bash
python query_with_context.py
```
Example prompts:
- `list all devices with passive AV mode`
- `show devices with outdated engine`
- `get devices missing AV signature refresh`

If the query references unsupported fields or only exists in business context, you’ll get:
```
-- ❌ This request references unsupported fields or concepts not found in the schema.
```



## 🧠 How It Works

- 🧾 **Schema-aware prompt**: schema is passed to guide valid fields
- 🧩 **Retriever-enhanced examples**: relevant documents from all 3 indexes
- 🗣️ **LLM synthesis**: LLM generates clean, safe KQL code
- 🧱 **Guardrails**: block invalid fields or hallucinated logic



## 🧪 Evaluate Context Index

You can explore index answers using:
```bash
python vector.py
```





## Note
author: Ellen Yan
collaborator: One MDE
