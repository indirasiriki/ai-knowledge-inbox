// Short status line. Errors use an alert so a screen reader announces them.
const tones = {
  error: 'border-red-200 bg-red-50 text-red-900',
  info: 'border-amber-200 bg-amber-50 text-amber-950',
};

export function Notice({ tone = 'error', children }) {
  return (
    <p className={`rounded-md border px-3 py-2 text-sm ${tones[tone]}`} role={tone === 'error' ? 'alert' : 'status'}>
      {children}
    </p>
  );
}
