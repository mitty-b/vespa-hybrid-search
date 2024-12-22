from vespa.package import ApplicationPackage, Component, Parameter
from vespa.deployment import VespaDocker
from datasets import load_dataset
from vespa.io import VespaResponse

from schema import create_document_schema
from utils.display import display_hits_as_df

def create_application_package():
    return ApplicationPackage(
        name="hybridsearch",
        schema=[create_document_schema()],
        components=[
            Component(
                id="e5",
                type="hugging-face-embedder",
                parameters=[
                    Parameter(
                        "transformer-model",
                        {
                            "url": "https://github.com/vespa-engine/sample-apps/raw/master/simple-semantic-search/model/e5-small-v2-int8.onnx"
                        },
                    ),
                    Parameter(
                        "tokenizer-model",
                        {
                            "url": "https://raw.githubusercontent.com/vespa-engine/sample-apps/master/simple-semantic-search/model/tokenizer.json"
                        },
                    ),
                ],
            )
        ],
    )

def feed_callback(response: VespaResponse, id: str):
    if not response.is_successful():
        print(f"Error when feeding document {id}: {response.get_json()}")

def main():
    # Create and deploy application
    package = create_application_package()
    vespa_docker = VespaDocker()
    app = vespa_docker.deploy(application_package=package)

    # Load and feed data
    dataset = load_dataset("BeIR/nfcorpus", "corpus", split="corpus", streaming=True)
    vespa_feed = dataset.map(
        lambda x: {
            "id": x["_id"],
            "fields": {"title": x["title"], "body": x["text"], "id": x["_id"]},
        }
    )
    app.feed_iterable(vespa_feed, schema="doc", namespace="tutorial", callback=feed_callback)

    return app

if __name__ == "__main__":
    main()