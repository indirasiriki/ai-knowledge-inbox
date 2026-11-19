// Display helpers. They do not talk to the API.
export function formatWhen(iso) {
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return '';
  return new Intl.DateTimeFormat(undefined, {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  }).format(date);
}

export function matchPercent(score) {
  const value = Math.round(Math.max(0, Math.min(1, Number(score) || 0)) * 100);
  return `${value}%`;
}

export function sourceLabel(sourceType) {
  return sourceType === 'url' ? 'Link' : 'Note';
}

// Only http(s) links are rendered. A stored value cannot become a javascript: link.
export function safeHttpUrl(value) {
  if (typeof value !== 'string') return '';
  try {
    const url = new URL(value);
    if (url.protocol === 'http:' || url.protocol === 'https:') return url.href;
  } catch {
    return '';
  }
  return '';
}
