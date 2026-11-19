// Question box and the answer beneath it. The question text stays after a reply.
import { useState } from 'react';
import { Button } from './Button.jsx';
import { Notice } from './Notice.jsx';
import { SourceList } from './SourceList.jsx';

export function AskPanel({ asking, error, answer, sources, onAsk }) {
  const [question, setQuestion] = useState('');
  const [localError, setLocalError] = useState('');

  async function submit(event) {
    event.preventDefault();
    const value = question.trim();
    if (!value) {
      setLocalError('Write a question first.');
      return;
    }
    setLocalError('');
    await onAsk(value);
  }

  function onKeyDown(event) {
    if (event.key === 'Enter' && (event.metaKey || event.ctrlKey)) {
      event.currentTarget.form?.requestSubmit();
    }
  }

  const shownError = localError || error;

  return (
    <section className="min-h-[28rem] rounded-lg border border-stone-200 bg-white">
      <form onSubmit={submit} className="border-b border-stone-200 p-4">
        <label className="block text-sm font-medium text-stone-800" htmlFor="question">
          Question
          <textarea
            id="question"
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            onKeyDown={onKeyDown}
            rows={3}
            disabled={asking}
            placeholder="What did I save about the deploy window?"
            className="mt-1 w-full resize-y rounded-md border border-stone-300 px-3 py-2 text-sm font-normal text-stone-900 placeholder:text-stone-400 focus:border-blue-900 focus:outline-none focus:ring-2 focus:ring-blue-900/20"
          />
        </label>
        <div className="mt-3 flex items-center justify-between gap-3">
          <p className="text-xs text-stone-500">Ctrl+Enter asks</p>
          <Button type="submit" disabled={asking}>
            {asking ? 'Asking...' : 'Ask'}
          </Button>
        </div>
        {shownError ? <div className="mt-3"><Notice>{shownError}</Notice></div> : null}
      </form>

      <div className="p-4" aria-live="polite">
        {asking ? <p className="text-sm text-stone-500">Searching saved notes...</p> : null}
        {answer ? (
          <p className="whitespace-pre-wrap text-[15px] leading-7 text-stone-900">{answer}</p>
        ) : !asking ? (
          <p className="text-sm text-stone-500">The answer will show up here, with the notes it came from.</p>
        ) : null}
        <SourceList sources={sources} />
      </div>
    </section>
  );
}
