import { useCallback, useEffect, useState } from 'react';
import { createItem, fetchItems, removeItem } from '../api/client.js';

// Saved rows live here. Create prepends the server response instead of refetching the list.
export function useItems() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const refresh = useCallback(async () => {
    try {
      const data = await fetchItems();
      setItems(data.items);
      setError('');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  async function create(payload) {
    const item = await createItem(payload);
    setItems((current) => [item, ...current]);
    setError('');
    return item;
  }

  async function remove(id) {
    await removeItem(id);
    setItems((current) => current.filter((item) => item.id !== id));
  }

  return { items, loading, error, create, remove };
}
