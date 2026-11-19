// Note or link form. It checks for an empty field before calling the API.
import { useState } from 'react';
import { Button } from './Button.jsx';
import { Notice } from './Notice.jsx';

export function Composer({ onCreate }) {
  const [kind, setKind] = useState('note');
  const [text, setText] = useState('');
  const [url, setUrl] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  async function submit(event) {
    event.preventDefault();
    setError('');

    const payload = kind === 'note'
      ? { sourceType: 'note', text: text.trim() }
      : { sourceType: 'url', url: url.trim() };

    if (kind === 'note' && !payload.text) {
      setError('Write a note before saving.');
      return;
    }
    if (kind === 'url' && !payload.url) {
      setError('Enter a URL before saving.');
      return;
    }

    setBusy(true);
    try {
      await onCreate(payload);
      setText('');
      setUrl('');
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  function chooseKind(next) {
    setKind(next);
    // A note error should not stay on screen after switching to a link.
    setError('');
  }

  function onKeyDown(event) {
    if (event.key === 'Enter' && (event.metaKey || event.ctrlKey)) {
      event.currentTarget.form?.requestSubmit();
    }
  }

  return (
    <form onSubmit={submit} className="rounded-lg border border-stone-200 bg-white p-4">
      <div role="tablist" aria-label="What to save" className="grid grid-cols-2 rounded-md bg-stone-100 p-1">
        <TabButton selected={kind === 'note'} onClick={() => chooseKind('note')}>Note</TabButton>
        <TabButton selected={kind === 'url'} onClick={() => chooseKind('url')}>Link</TabButton>
      </div>

      {kind === 'note' ? (
        <label className="mt-4 block text-sm font-medium text-stone-800" htmlFor="note-text">
          Note
          <textarea
            id="note-text"
            value={text}
            onChange={(event) => setText(event.target.value)}
            onKeyDown={onKeyDown}
            rows={6}
            disabled={busy}
            placeholder="Paste a meeting note, a definition, a list..."
            className="mt-1 w-full resize-y rounded-md border border-stone-300 px-3 py-2 text-sm font-normal text-stone-900 placeholder:text-stone-400 focus:border-blue-900 focus:outline-none focus:ring-2 focus:ring-blue-900/20"
          />
        </label>
      ) : (
        <label className="mt-4 block text-sm font-medium text-stone-800" htmlFor="page-url">
          Link
          <input
            id="page-url"
            type="url"
            value={url}
            onChange={(event) => setUrl(event.target.value)}
            onKeyDown={onKeyDown}
            disabled={busy}
            placeholder="https://example.com/article"
            className="mt-1 w-full rounded-md border border-stone-300 px-3 py-2 text-sm font-normal text-stone-900 placeholder:text-stone-400 focus:border-blue-900 focus:outline-none focus:ring-2 focus:ring-blue-900/20"
          />
        </label>
      )}

      <div className="mt-3 flex items-center justify-between gap-3">
        <p className="text-xs text-stone-500">Ctrl+Enter saves</p>
        <Button type="submit" disabled={busy}>
          {busy ? 'Saving...' : kind === 'note' ? 'Save note' : 'Save link'}
        </Button>
      </div>
      {error ? <div className="mt-3"><Notice>{error}</Notice></div> : null}
    </form>
  );
}

function TabButton({ selected, onClick, children }) {
  return (
    <button
      type="button"
      role="tab"
      aria-selected={selected}
      onClick={onClick}
      className={`rounded px-3 py-1.5 text-sm font-medium ${selected ? 'bg-white text-stone-950 shadow-sm' : 'text-stone-600'}`}
    >
      {children}
    </button>
  );
}
