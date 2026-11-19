import { useState } from 'react';
import { askQuestion } from '../api/client.js';

// Holds the latest answer. A failed ask keeps the previous answer on screen.
export function useQuestion() {
  const [asking, setAsking] = useState(false);
  const [error, setError] = useState('');
  const [answer, setAnswer] = useState('');
  const [sources, setSources] = useState([]);

  async function ask(question) {
    setAsking(true);
    setError('');
    try {
      const result = await askQuestion(question);
      setAnswer(result.answer);
      setSources(result.sources || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setAsking(false);
    }
  }

  return { asking, error, answer, sources, ask };
}
