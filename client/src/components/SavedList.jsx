// Saved rows. Remove asks for a second click so a miss does not delete the note.
import { useState } from 'react';
import { formatWhen, safeHttpUrl, sourceLabel } from '../format.js';
import { Button } from './Button.jsx';
import { Notice } from './Notice.jsx';

export function SavedList({ items, loading, error, onRemove }) {
  const [pendingId, setPendingId] = useState('');
  const [busyId, setBusyId] = useState('');
  const [localError, setLocalError] = useState('');

  async function confirmRemove(id) {
    setBusyId(id);
    setLocalError('');
    try {
      await onRemove(id);
      setPendingId('');
    } catch (err) {
      setLocalError(err.message);
    } finally {
      setBusyId('');
    }
  }

  return (
    <section className="rounded-lg border border-stone-200 bg-white">
      <div className="flex items-baseline justify-between border-b border-stone-200 px-4 py-3">
        <h2 className="text-sm font-semibold text-stone-950">Saved</h2>
        <p className="text-xs text-stone-500">{loading ? 'Loading...' : items.length}</p>
      </div>

      {error ? <div className="px-4 pt-3"><Notice>{error}</Notice></div> : null}
      {localError ? <div className="px-4 pt-3"><Notice>{localError}</Notice></div> : null}

      {loading ? null : items.length === 0 ? (
        <p className="px-4 py-6 text-sm text-stone-500">Nothing saved yet.</p>
      ) : (
        <ul className="max-h-[28rem] divide-y divide-stone-100 overflow-y-auto">
          {items.map((item) => {
            const href = safeHttpUrl(item.sourceUrl);
            return (
              <li key={item.id} className="px-4 py-3">
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <p className="truncate text-sm font-medium text-stone-950">{item.title}</p>
                    <p className="mt-0.5 text-xs text-stone-500">
                      <span>{sourceLabel(item.sourceType)}</span>
                      {item.createdAt ? <time dateTime={item.createdAt}> · {formatWhen(item.createdAt)}</time> : null}
                      {item.chunkCount > 1 ? <span> · Split into {item.chunkCount} parts</span> : null}
                    </p>
                  </div>
                  {pendingId === item.id ? (
                    <span className="flex shrink-0 gap-2">
                      <Button variant="danger" disabled={busyId === item.id} onClick={() => confirmRemove(item.id)}>
                        {busyId === item.id ? 'Removing...' : 'Confirm'}
                      </Button>
                      <Button variant="quiet" onClick={() => setPendingId('')}>Cancel</Button>
                    </span>
                  ) : (
                    <Button variant="quiet" className="shrink-0" onClick={() => setPendingId(item.id)} aria-label={`Remove ${item.title}`}>
                      Remove
                    </Button>
                  )}
                </div>
                {href ? (
                  <a href={href} target="_blank" rel="noreferrer" className="mt-1 block truncate text-xs text-blue-950 hover:underline">
                    {href}
                  </a>
                ) : null}
                {item.excerpt ? <p className="mt-2 text-sm leading-6 text-stone-700">{item.excerpt}</p> : null}
              </li>
            );
          })}
        </ul>
      )}
    </section>
  );
}
