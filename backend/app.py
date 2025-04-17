from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer
import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import re
import os

app = Flask(__name__)
model = SentenceTransformer('all-MiniLM-L6-v2')

# Load data with error handling
def load_data():
    if not os.path.exists('scraped_data.json'):
        raise FileNotFoundError("The scraped_data.json file is missing.")
    
    with open('scraped_data.json') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            raise ValueError("The scraped_data.json file is not properly formatted.")

try:
    data = load_data()
except (FileNotFoundError, ValueError) as e:
    print(f"Error loading data: {e}")
    data = []

# Prepare documents
def prepare_docs(data):
    docs = []
    for item in data:
        purpose = item.get('purpose', '')
        past_events = "\n".join(
            f"{e.get('name', '')}: {e.get('theme') or e.get('details', '')} ({e.get('date', '')})"
            for e in item.get('pastEvents', [])
        )
        future_plans = "\n".join(item.get('futurePlans', []))
        full_doc = f"{purpose}\n{past_events}\n{future_plans}".strip()
        docs.append(full_doc)
    return docs

docs = prepare_docs(data)
embeddings = model.encode(docs).tolist() if docs else []  # Convert to list for safe truthiness check

# Parse future event strings
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
    try:
        user_message = request.json['message'].lower()
    except (KeyError, TypeError):
        return jsonify({'error': 'Invalid input format. Please provide a message.'}), 400
    
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
    
    # Similarity search logic
    if embeddings and len(embeddings) > 0:
        query_embedding = model.encode([user_message])[0]
        scores = cosine_similarity([query_embedding], embeddings)[0]
        top_indices = np.argsort(scores)[-3:][::-1]
        top_docs = [docs[i] for i in top_indices]

        return jsonify({'context': "\n\n".join(top_docs)})
    else:
        return jsonify({'error': 'No embeddings available. Please check your data.'}), 500

if __name__ == "__main__":
    app.run(port=5000)
