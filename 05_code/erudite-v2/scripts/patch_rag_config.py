from google.cloud import aiplatform_v1
import os

PROJECT_ID = os.environ["PROJECT_ID"]
LOCATION = "us-central1"

print(f"Initializing VertexRagServiceClient for project {PROJECT_ID} in {LOCATION}...")
client = aiplatform_v1.VertexRagServiceClient(
    client_options={"api_endpoint": f"{LOCATION}-aiplatform.googleapis.com"}
)

config_name = f"projects/{PROJECT_ID}/locations/{LOCATION}/ragEngineConfig"

rag_engine_config = aiplatform_v1.RagEngineConfig(
    name=config_name,
    rag_managed_db_config=aiplatform_v1.RagManagedDbConfig()
)

print("Sending update request to switch RAG Engine to Serverless mode...")
operation = client.update_rag_engine_config(
    rag_engine_config=rag_engine_config,
    update_mask="rag_managed_db_config"
)

response = operation.result()
print(f"Successfully updated RAG Engine Config: {response.name}")
