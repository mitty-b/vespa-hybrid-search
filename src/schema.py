from vespa.package import (
    Field,
    Schema,
    Document,
    HNSW,
    FieldSet,
)
from ranking import create_rank_profiles

def create_document_schema():
    return Schema(
        name="doc",
        document=Document(
            fields=[
                Field(name="id", type="string", indexing=["summary"]),
                Field(
                    name="title",
                    type="string",
                    indexing=["index", "summary"],
                    index="enable-bm25",
                ),
                Field(
                    name="body",
                    type="string",
                    indexing=["index", "summary"],
                    index="enable-bm25",
                    bolding=True,
                ),
                Field(
                    name="embedding",
                    type="tensor<float>(x[384])",
                    indexing=[
                        'input title . " " . input body',
                        "embed",
                        "index",
                        "attribute",
                    ],
                    ann=HNSW(distance_metric="angular"),
                    is_document_field=False,
                ),
            ]
        ),
        fieldsets=[FieldSet(name="default", fields=["title", "body"])],
        rank_profiles=create_rank_profiles(),
    )