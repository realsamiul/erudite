from google.cloud import discoveryengine_v1beta as discoveryengine
import os
import sys

PROJECT_ID = os.environ.get("PROJECT_ID", "project-a1f62154-a7ad-4b37-93b")
parent = f"projects/{PROJECT_ID}/locations/global/collections/default_collection"

client = discoveryengine.DataStoreServiceClient()

stores = {
    "statutes-search-store": "Sovereign Constitutional Statutes Search",
    "it-security-search-store": "IT Security and Cybersecurity Compliance Search",
    "clinical-safety-search-store": "Clinical Safety and Healthcare Protocols Search"
}

for ds_id, display_name in stores.items():
    print(f"Creating Data Store '{ds_id}' ({display_name})...")
    
    data_store = discoveryengine.DataStore(
        display_name=display_name,
        industry_vertical="GENERIC",
        solution_types=["SOLUTION_TYPE_SEARCH"],
        content_config="CONTENT_REQUIRED"
    )
    
    try:
        operation = client.create_data_store(
            parent=parent,
            data_store=data_store,
            data_store_id=ds_id
        )
        print(f"  Operation started for {ds_id}...")
        response = operation.result()
        print(f"  SUCCESS: Created {ds_id}: {response.name}")
    except Exception as e:
        if "already exists" in str(e):
            print(f"  INFO: Data Store '{ds_id}' already exists.")
        else:
            print(f"  FAILED to create {ds_id}: {e}")
            sys.exit(1)

print("\nAll premium Discovery Engine Search Data Stores are fully ready!")
