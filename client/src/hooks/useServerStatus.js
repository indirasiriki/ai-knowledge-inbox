import { useEffect, useState } from 'react';
import { fetchHealth } from '../api/client.js';

// One health check on load. It tells the page whether a key is configured.
export function useServerStatus() {
  const [state, setState] = useState({ tone: 'info', message: '' });

  useEffect(() => {
    let active = true;
    fetchHealth()
      .then((health) => {
        if (!active) return;
        if (health.mode === 'local') {
          setState({
            tone: 'info',
            message: 'Running in Local Mode (offline RAG enabled). You can save notes and ask questions!',
          });
          return;
        }
        setState({ tone: 'info', message: '' });
      })
      .catch(() => {
        if (!active) return;
        setState({
          tone: 'error',
          message: 'The server is not responding on port 3001.',
        });
      });
    return () => {
      active = false;
    };
  }, []);

  return state;
}
