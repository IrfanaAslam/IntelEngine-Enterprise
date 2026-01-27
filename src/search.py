import json
import re
from collections import defaultdict

class ResearchSearchEngine:
    def __init__(self, data_list):
        self.index = defaultdict(set)
        self.docs = data_list
        self._build_index()

    def _build_index(self):
        for idx, doc in enumerate(self.docs):
            words = set(re.findall(r'\w+', doc.get('text', '').lower()))
            for word in words:
                self.index[word].add(idx)

    def search(self, query):
        query = query.lower()
        indices = self.index.get(query, [])
        if not indices: return []
        
        results = []
        for i in indices:
            d = self.docs[i]
            text = d.get('text', "")
            start = max(0, text.lower().find(query) - 50)
            results.append({
                "file": d['metadata']['filename'],
                "snippet": "..." + text[start:start+150].replace("\n", " ") + "...",
                "entities": d.get('entities', {})
            })
        return results