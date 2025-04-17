// const express = require('express');
// const axios = require('axios');
// const cors = require('cors');
// require('dotenv').config();

// const app = express();

// const openRouterApiKey = process.env.OPENROUTER_API_KEY;

// app.post('/api/chat', async (req, res) => {
//     const userMessage = req.body.message;

//     try {
//         if (userMessage.toLowerCase() === 'upcoming events') {
//             // Proxy to Python backend for events
//             const embeddingResponse = await axios.post('http://localhost:5000/embedding', {
//                 message: userMessage,
//             });
//             res.json(embeddingResponse.data);
//         } else {
//             // Send query to Python backend for other messages
//             const embeddingResponse = await axios.post('http://localhost:5000/embedding', {
//                 message: userMessage,
//             });

//             const context = embeddingResponse.data.context;
//             const prompt = `Context: ${context}\nQuestion: ${userMessage}\nAnswer:`;

//             const response = await axios.post(
//                 'https://openrouter.ai/api/v1/chat/completions',
//                 {
//                     model: 'mistral/ministral-8b',
//                     messages: [{ role: 'user', content: prompt }]
//                 },
//                 {
//                     headers: {
//                         'Authorization': `Bearer ${openRouterApiKey}`,
//                         'Content-Type': 'application/json'
//                     }
//                 }
//             );

//             let reply = response.data.choices[0].message.content;
//             reply = reply.replace(/```[a-z]*\n?/gi, '')
//                 .replace(/```/g, '')
//                 .replace(/#+\s?/g, '')
//                 .replace(/\*\*/g, '')
//                 .replace(/\\n/g, '\n');

//             res.json({ response: reply });
//         }
//     } catch (error) {
//         console.error('Error:', error.response ? error.response.data : error.message);
//         res.status(500).json({ error: 'Failed to process request' });
//     }
// });

// app.listen(3000, () => console.log('Server running on http://localhost:3000'));


// const express = require('express');
// const axios = require('axios');
// const cors = require('cors');
// const app = express();

// app.use(cors()); // Enable CORS
// app.use(express.json());

// app.post('/api/chat', async (req, res) => {
//     const userMessage = req.body.message;
//     const openRouterApiKey = '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';

//     try {
//         const response = await axios.post(
//             'https://openrouter.ai/api/v1/chat/completions',
//             {
//                 model: 'mistral/ministral-8b',
//                 messages: [{ role: 'user', content: userMessage }]
//             },
//             {
//                 headers: {
//                     'Authorization': `Bearer ${openRouterApiKey}`,
//                     'Content-Type': 'application/json'
//                 }
//             }
//         );

//         // res.json({ response: response.data.choices[0].message.content });
//         let reply = response.data.choices[0].message.content;

//         // Clean markdown and formatting
//         reply = reply
//             .replace(/```[a-z]*\n?/gi, '')  // remove ```python or ```js
//             .replace(/```/g, '')            // remove closing ```
//             .replace(/#+\s?/g, '')          // remove headings like ### or ##
//             .replace(/\*\*/g, '')           // remove bold
//             .replace(/\\n/g, '\n');         // replace escaped newlines

//         res.json({ response: reply });

//     } catch (error) {
//         console.error('Error:', error.response ? error.response.data : error.message);
//         res.status(500).json({ error: 'Failed to get response from OpenRouter API' });
//     }
// });

// app.listen(3000, () => {
//     console.log('Server running on http://localhost:3000');
// });
// import express from 'express';
// import axios from 'axios';
// import cors from 'cors';
// import 'dotenv/config';

// const app = express();
// app.use(cors());
// app.use(express.json());

// const openRouterApiKey = process.env.OPENROUTER_API_KEY;

// app.post('/api/chat', async (req, res) => {
//     const userMessage = req.body.message;

//     try {
//         // Send query to Python backend
//         const embeddingResponse = await axios.post('http://localhost:5000/embedding', {
//             message: userMessage,
//         });

//         const context = embeddingResponse.data.context;
//         const prompt = `Context: ${context}\nQuestion: ${userMessage}\nAnswer:`;

//         const response = await axios.post(
//             'https://openrouter.ai/api/v1/chat/completions',
//             {
//                 model: 'mistral/ministral-8b',
//                 messages: [{ role: 'user', content: prompt }]
//             },
//             {
//                 headers: {
//                     'Authorization': `Bearer ${openRouterApiKey}`,
//                     'Content-Type': 'application/json'
//                 }
//             }
//         );

//         let reply = response.data.choices[0].message.content;
//         reply = reply.replace(/```[a-z]*\n?/gi, '').replace(/```/g, '').replace(/#+\s?/g, '').replace(/\*\*/g, '').replace(/\\n/g, '\n');

//         res.json({ response: reply });
//     } catch (error) {
//         console.error('Error:', error.response ? error.response.data : error.message);
//         res.status(500).json({ error: 'Failed to process request' });
//     }
// });

// app.listen(3000, () => console.log('Server running on http://localhost:3000'));















import express from 'express';
import axios from 'axios';
import cors from 'cors';
import 'dotenv/config';

const app = express();

app.use(cors());
app.use(express.json());

const openRouterApiKey = process.env.OPENROUTER_API_KEY;

app.post('/api/chat', async (req, res) => {
  const userMessage = req.body.message;

  try {
    const embeddingResponse = await axios.post('http://localhost:5000/embedding', {
      message: userMessage,
    });

    if (userMessage.toLowerCase() === 'upcoming events') {
      res.json(embeddingResponse.data);
    } else {
      const context = embeddingResponse.data.context;
      const prompt = `Context: ${context}\nQuestion: ${userMessage}\nAnswer:`;

      const response = await axios.post(
        'https://openrouter.ai/api/v1/chat/completions',
        {
          model: 'mistral/ministral-8b',
          messages: [{ role: 'user', content: prompt }],
        },
        {
          headers: {
            Authorization: `Bearer ${openRouterApiKey}`,
            'Content-Type': 'application/json',
          },
        }
      );

      let reply = response.data.choices[0].message.content;
      reply = reply
        .replace(/```[a-z]*\n?/gi, '')
        .replace(/```/g, '')
        .replace(/#+\s?/g, '')
        .replace(/\*\*/g, '')
        .replace(/\\n/g, '\n');

      res.json({ response: reply });
    }
  } catch (error) {
    console.error('Error:', error.response ? error.response.data : error.message);
    res.status(500).json({ error: 'Failed to process request' });
  }
});

app.listen(3000, () => console.log('Server running on http://localhost:3000'));
