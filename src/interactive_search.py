from vespa.application import Vespa
from utils.display import display_hits_as_df

def create_vespa_app(port=8080):
    return Vespa(f"http://localhost:{port}")

def perform_searches(app, query_text):    
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


def perform_single_search(app, query_text, search_type="hybrid"):
    with app.syncio(connections=1) as session:
        if search_type == "bm25":
            response = session.query(
                yql="select * from sources * where userQuery() limit 5",
                query=query_text,
                ranking="bm25",
            )
        elif search_type == "semantic":
            response = session.query(
                yql="select * from sources * where ({targetHits:1000}nearestNeighbor(embedding,q)) limit 5",
                query=query_text,
                ranking="semantic",
                body={"input.query(q)": f"embed({query_text})"},
            )
        else:  # hybrid
            response = session.query(
                yql="select * from sources * where rank({targetHits:1000}nearestNeighbor(embedding,q), userQuery()) limit 5",
                query=query_text,
                ranking="fusion",
                body={"input.query(q)": f"embed({query_text})"},
            )
        
        return display_hits_as_df(response, ["id", "title", "body"])

def interactive_search():
    app = create_vespa_app()
    
    while True:
        print("\n=== Vespa Search Interface ===")
        print("1. BM25 Search")
        print("2. Semantic Search")
        print("3. Hybrid Search")
        print("4. All Searchs")
        print("5. Exit")
        
        choice = input("\nSelect search type (1-5): ")
        
        if choice == "5":
            break
            
        query = input("Enter your search query: ")
        
        if choice == "1":
            print("\n=== BM25 Search Results ===")
            print(perform_single_search(app, query, "bm25"))
        elif choice == "2":
            print("\n=== Semantic Search Results ===")
            print(perform_single_search(app, query, "semantic"))
        elif choice == "3":
            print("\n=== Hybrid Search Results ===")
            print(perform_single_search(app, query, "hybrid"))
        elif choice == "4":
            perform_searches(app, query)
        else:
            print("Invalid choice!")
            continue
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    interactive_search()