# # from flask import Flask, request, jsonify
# # from sentence_transformers import SentenceTransformer
# # import faiss
# # import numpy as np
# # import json
# # from flask_cors import CORS

# # # Initialize app and CORS
# # app = Flask(__name__)
# # CORS(app)

# # # Load FAISS index and metadata (for clubs)
# # index = faiss.read_index('faiss_index.index')
# # with open("metadata.json", "r", encoding='utf-8') as f:
# #     club_metadata = json.load(f)

# # # Load full scraped data (events, KMIT info, etc.)
# # with open("scraped_data.json", "r", encoding="utf-8") as f:
# #     scraped_data = json.load(f)

# # # Load embedding model
# # model = SentenceTransformer('all-MiniLM-L6-v2')


# # @app.route('/')
# # def index_route():
# #     return "✅ KMIT Chatbot Backend is running!"


# # @app.route('/chat', methods=['POST'])
# # def chat():
# #     user_query = request.json.get('message', '')
# #     if not user_query:
# #         return jsonify({'response': 'Please enter a valid message.'}), 400

# #     # Check for KMIT general info
# #     if any(keyword in user_query.lower() for keyword in ["about kmit", "kmit info", "college", "kmit location", "when established", "fest", "fests", "campus"]):
# #         kmit_info = scraped_data.get("kmit_info", {}).get("kmit", [])
# #         return jsonify({
# #             'response': "🏫 **KMIT Information**\n\n" + "\n".join(f"• {line}" for line in kmit_info)
# #         })

# #     # Check for event-related query
# #     if any(keyword in user_query.lower() for keyword in ["event", "fest", "celebration", "utsav", "kmit eve", "navraas", "date"]):
# #         events = scraped_data.get("events", [])
# #         event_response = "📅 **Upcoming Events at KMIT**\n\n"
# #         for event in events:
# #             event_response += f"• {event['name']} — {event['date']}\n"
# #         return jsonify({'response': event_response.strip()})

# #     # Otherwise, check FAISS for club match
# #     query_embedding = model.encode([user_query])
# #     k = 1
# #     distances, indices = index.search(np.array(query_embedding), k)
# #     idx = indices[0][0]
# #     matched_club = club_metadata[idx]
# #     response = f"📌 **{matched_club['name']}**\n\n{matched_club['description']}"

# #     return jsonify({'response': response})


# # if __name__ == '__main__':
# #     app.run(debug=True)







# # app.py
# from flask import Flask, request, jsonify
# import faiss
# import json
# import numpy as np
# from sentence_transformers import SentenceTransformer
# from flask_cors import CORS



# app = Flask(__name__)
# CORS(app)  # Add this

# # Load model
# model = SentenceTransformer('all-MiniLM-L6-v2')

# # Load FAISS index
# index = faiss.read_index('faiss_index.index')

# # Load metadata
# with open('faiss_metadata.json', 'r') as f:
#     metadata = json.load(f)

# @app.route('/query', methods=['POST'])
# def query_vector_db():
#     user_input = request.json['query']
    
#     # Embed query
#     query_embedding = model.encode([user_input]).astype('float32')
    
#     # Search FAISS
#     D, I = index.search(query_embedding, k=3)

#     # Fetch top matches
#     results = []
#     for idx in I[0]:
#         results.append(metadata[idx])
    
#     return jsonify({'results': results})

# if __name__ == '__main__':
#     app.run(debug=True)





# from flask import Flask, request, jsonify
# from sentence_transformers import SentenceTransformer
# import json
# import numpy as np
# from sklearn.metrics.pairwise import cosine_similarity
# import re
# import os
# from waitress import serve
# from flask_cors import CORS

# # Initialize Flask app
# app = Flask(__name__)
# CORS(app)  # Enable CORS

# # Load embedding model
# model = SentenceTransformer('all-MiniLM-L6-v2')

# # Load data once with error handling
# def load_data():
#     if not os.path.exists('scraped_data.json'):
#         raise FileNotFoundError("The scraped_data.json file is missing.")
    
#     with open('scraped_data.json') as f:
#         try:
#             data = json.load(f)
#         except json.JSONDecodeError:
#             raise ValueError("The scraped_data.json file is not properly formatted.")
#     return data

# try:
#     data = load_data()
# except (FileNotFoundError, ValueError) as e:
#     print(f"Error loading data: {e}")
#     data = []

# # Prepare document texts for embedding
# def prepare_docs(data):
#     if not data:
#         return []
    
#     docs = [
#         f"{item['purpose']}\n" +
#         "\n".join(f"{e['name']}: {e.get('theme') or e.get('details', '')} ({e.get('date', '')})" for e in item.get('pastEvents', [])) +
#         "\n" + "\n".join(item.get('futurePlans', []))
#         for item in data
#     ]
#     return docs

# # Generate embeddings
# docs = prepare_docs(data)
# embeddings = model.encode(docs) if docs else []

# # Extract title and date from future plans
# def parse_future_event(event_str):
#     event_str = event_str.strip()
#     date_match = re.search(r'(\d{1,2}(?:st|nd|rd|th)?\s+[A-Za-z]+\s*,\s*\d{4}|\d{1,2}/\d{1,2}/\d{4}|\w+\s+\d{4})', event_str)
#     date = date_match.group(0) if date_match else 'Date TBD'
#     title = event_str.replace(date, '').strip() or event_str
#     return {'title': title, 'date': date}

# # POST endpoint for query embedding
# @app.route("/embedding", methods=["POST"])
# def embedding():
#     try:
#         user_message = request.json['message'].lower()
#     except (KeyError, TypeError):
#         return jsonify({'error': 'Invalid input format. Please provide a message.'}), 400
    
#     if user_message == 'upcoming events':
#         # Return parsed upcoming events
#         future_events = []
#         for item in data:
#             if 'futurePlans' in item:
#                 for plan in item['futurePlans']:
#                     parsed_event = parse_future_event(plan)
#                     future_events.append(parsed_event)
        
#         return jsonify({
#             'response': 'Here are the upcoming events:',
#             'events': future_events if future_events else [{'title': 'No upcoming events available', 'date': ''}]
#         })

#     # General embedding response
#     if embeddings:
#         query_embedding = model.encode([user_message])[0]
#         scores = cosine_similarity([query_embedding], embeddings)[0]
#         top_indices = np.argsort(scores)[-3:][::-1]
#         top_docs = [docs[i] for i in top_indices]

#         return jsonify({'context': "\n".join(top_docs)})
#     else:
#         return jsonify({'error': 'No embeddings available. Please check the data loading process.'}), 500

# # Start server with Waitress
# if __name__ == "__main__":
#     serve(app, host='0.0.0.0', port=5000)






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

# Prepare documents for embedding
docs = [
    f"{item['purpose']}\n" +
    "\n".join(f"{e['name']}: {e.get('theme') or e.get('details', '')} ({e.get('date', '')})" for e in item['pastEvents']) +
    "\n" + "\n".join(item.get('futurePlans', []))
    for item in data
]
embeddings = model.encode(docs)

def parse_future_event(event_str):
    # Basic parsing to extract title and date
    event_str = event_str.strip()
    date_match = re.search(r'(\d{1,2}(?:st|nd|rd|th)?\s+[A-Za-z]+\s*,\s*\d{4}|\d{1,2}/\d{1,2}/\d{4}|\w+\s+\d{4})', event_str)
    date = date_match.group(0) if date_match else 'Date TBD'
    title = event_str.replace(date, '').strip() or event_str
    return {'title': title, 'date': date}

@app.route("/embedding", methods=["POST"])
def embedding():
    user_message = request.json['message'].lower()
    
    if user_message == 'upcoming events':
        # Extract and parse future events from data
        future_events = []
        for item in data:
            if 'futurePlans' in item:
                for plan in item['futurePlans']:
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
