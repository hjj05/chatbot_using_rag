from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer
import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import re

app = Flask(__name__)
model = SentenceTransformer('all-MiniLM-L6-v2')

# Load data once
with open('scraped_data.json') as f:
    data = json.load(f)

# Prepare documents safely for embedding
docs = []
for item in data:
    purpose = item.get('purpose', '')
    past_events = "\n".join(
        f"{e.get('name', '')}: {e.get('theme') or e.get('details', '')} ({e.get('date', '')})"
        for e in item.get('pastEvents', [])
    )
    future_plans = "\n".join(item.get('futurePlans', []))
    doc_text = f"{purpose}\n{past_events}\n{future_plans}".strip()
    docs.append(doc_text)

# Precompute embeddings
embeddings = model.encode(docs)

def parse_future_event(event_str):
    event_str = event_str.strip()
    date_match = re.search(
        r'(\d{1,2}(?:st|nd|rd|th)?\s+[A-Za-z]+\s*,\s*\d{4}|\d{1,2}/\d{1,2}/\d{4}|\w+\s+\d{4})',
        event_str
    )
    date = date_match.group(0) if date_match else 'Date TBD'
    title = event_str.replace(date, '').strip() or event_str
    return {'title': title, 'date': date}

@app.route("/embedding", methods=["POST"])
def embedding():
    user_message = request.json.get('message', '').lower()
    
    if user_message == 'upcoming events':
        future_events = []
        for item in data:
            for plan in item.get('futurePlans', []):
                parsed_event = parse_future_event(plan)
                future_events.append(parsed_event)
        
        return jsonify({
            'response': 'Here are the upcoming events:',
            'events': future_events if future_events else [{'title': 'No upcoming events available', 'date': ''}]
        })
    
    # Default embedding logic for other queries
    query_embedding = model.encode([user_message])[0]
    scores = cosine_similarity([query_embedding], embeddings)[0]
    top_indices = np.argsort(scores)[-3:][::-1]
    top_docs = [docs[i] for i in top_indices]

    return jsonify({'context': "\n".join(top_docs)})

if __name__ == "__main__":
    app.run(port=5000)
