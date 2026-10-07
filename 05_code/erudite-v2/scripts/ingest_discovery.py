from google.cloud import discoveryengine_v1beta as discoveryengine
import os
import sys

PROJECT_ID = os.environ.get("PROJECT_ID", "project-a1f62154-a7ad-4b37-93b")
client = discoveryengine.DocumentServiceClient()

mappings = {
    "statutes-search-store": "statutes",
    "it-security-search-store": "it_security",
    "clinical-safety-search-store": "clinical_safety"
}

for ds_id, gcs_prefix in mappings.items():
    print(f"Triggering ingestion for '{ds_id}' from 'gs://{PROJECT_ID}-docs/{gcs_prefix}/*'...")
    
    parent = f"projects/{PROJECT_ID}/locations/global/collections/default_collection/dataStores/{ds_id}/branches/0"
    
    gcs_source = discoveryengine.GcsSource(
        input_uris=[f"gs://{PROJECT_ID}-docs/{gcs_prefix}/*"],
        data_schema="content"
    )
    
    request = discoveryengine.ImportDocumentsRequest(
        parent=parent,
        gcs_source=gcs_source,
        reconciliation_mode="INCREMENTAL"
    )
    
    try:
        operation = client.import_documents(request=request)
        print(f"  Ingestion started (Operation: {operation.operation.name})")
    except Exception as e:
        print(f"  FAILED to start ingestion for {ds_id}: {e}")
        sys.exit(1)

print("\nAll Discovery Engine ingestion operations have been successfully initiated!")
