// The screen is three areas: save something, see what is saved, ask about it.
import { AskPanel } from './components/AskPanel.jsx';
import { Composer } from './components/Composer.jsx';
import { Notice } from './components/Notice.jsx';
import { SavedList } from './components/SavedList.jsx';
import { useItems } from './hooks/useItems.js';
import { useQuestion } from './hooks/useQuestion.js';
import { useServerStatus } from './hooks/useServerStatus.js';

export function App() {
  // Each hook owns one concern so a failed save does not clear the last answer.
  const status = useServerStatus();
  const items = useItems();
  const question = useQuestion();

  return (
    <div className="min-h-screen">
      <header className="border-b border-stone-200 bg-white">
        <div className="mx-auto flex max-w-6xl flex-col gap-1 px-5 py-5">
          <h1 className="text-lg font-semibold tracking-tight text-stone-950">Knowledge Inbox</h1>
          <p className="text-sm text-stone-600">Save a note or a link. Ask questions against what you have saved.</p>
        </div>
      </header>
      <main className="mx-auto grid max-w-6xl gap-6 px-5 py-6 lg:grid-cols-[22rem_minmax(0,1fr)]">
        {status.message ? (
          <div className="lg:col-span-2">
            <Notice tone={status.tone}>{status.message}</Notice>
          </div>
        ) : null}
        <div className="flex flex-col gap-4">
          <Composer onCreate={items.create} />
          <SavedList
            items={items.items}
            loading={items.loading}
            error={items.error}
            onRemove={items.remove}
          />
        </div>
        <AskPanel
          asking={question.asking}
          error={question.error}
          answer={question.answer}
          sources={question.sources}
          onAsk={question.ask}
        />
      </main>
    </div>
  );
}
