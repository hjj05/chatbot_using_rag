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
