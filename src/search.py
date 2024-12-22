from vespa.application import Vespa
from utils.display import display_hits_as_df

def create_vespa_app(port=8080):
    return Vespa(f"http://localhost:{port}")

def perform_searches(query_text):
    app = create_vespa_app()
    
    # 1. BM25 (Keyword) Search
    print("\n=== BM25 Keyword Search Results ===")
    with app.syncio(connections=1) as session:
        response = session.query(
            yql="select * from sources * where userQuery() limit 5",
            query=query_text,
            ranking="bm25",
        )
        print(display_hits_as_df(response, ["id", "title"]))

    # 2. Semantic Search
    print("\n=== Semantic Search Results ===")
    with app.syncio(connections=1) as session:
        response = session.query(
            yql="select * from sources * where ({targetHits:1000}nearestNeighbor(embedding,q)) limit 5",
            query=query_text,
            ranking="semantic",
            body={"input.query(q)": f"embed({query_text})"},
        )
        print(display_hits_as_df(response, ["id", "title"]))

    # 3. Hybrid Search
    print("\n=== Hybrid Search Results ===")
    with app.syncio(connections=1) as session:
        response = session.query(
            yql="select * from sources * where rank({targetHits:1000}nearestNeighbor(embedding,q), userQuery()) limit 5",
            query=query_text,
            ranking="fusion",
            body={"input.query(q)": f"embed({query_text})"},
        )
        print(display_hits_as_df(response, ["id", "title", "body"]))

if __name__ == "__main__":
    query = input("Enter your search query: ")
    perform_searches(query)