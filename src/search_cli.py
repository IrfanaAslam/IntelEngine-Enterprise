from src.search import ResearchSearchEngine

# Load the engine
engine = ResearchSearchEngine("data/processed/final_research_data.json")

while True:
    query = input("\n🔎 Enter keyword to search (or 'exit'): ")
    if query.lower() == 'exit': break
    
    results = engine.search(query)
    
    if isinstance(results, str):
        print(results)
    else:
        print(f"🎯 Found in {len(results)} documents:")
        for r in results:
            print(f"\n📄 {r['file']}")
            print(f"   Context: {r['context']}")
            if r['entities'].get('project_ids'):
                print(f"   IDs: {r['entities']['project_ids']}")