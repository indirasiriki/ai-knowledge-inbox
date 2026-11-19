// Numbered chunks the answer was written from. The numbers match the [1] marks in the reply.
import { matchPercent, safeHttpUrl, sourceLabel } from '../format.js';

export function SourceList({ sources }) {
  if (!sources?.length) return null;

  return (
    <div className="mt-6 border-t border-stone-200 pt-4">
      <h2 className="text-sm font-semibold text-stone-950">Sources</h2>
      <ol className="mt-3 flex flex-col gap-3">
        {sources.map((source) => {
          const href = safeHttpUrl(source.sourceUrl);
          return (
            <li key={`${source.itemId}-${source.label}`} className="rounded-md border border-stone-200 bg-stone-50 px-3 py-3">
              <div className="flex items-baseline justify-between gap-3">
                <p className="min-w-0 text-sm font-medium text-stone-950">
                  [{source.label}] {source.title}
                </p>
                <p className="shrink-0 text-xs text-stone-500">{matchPercent(source.score)} match</p>
              </div>
              <p className="mt-0.5 text-xs text-stone-500">{sourceLabel(source.sourceType)}</p>
              {href ? (
                <a href={href} target="_blank" rel="noreferrer" className="mt-1 block truncate text-xs text-blue-950 hover:underline">
                  {href}
                </a>
              ) : null}
              {source.snippet ? <p className="mt-2 text-sm leading-6 text-stone-700">{source.snippet}</p> : null}
            </li>
          );
        })}
      </ol>
    </div>
  );
}
