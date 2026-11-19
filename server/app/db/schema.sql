CREATE TABLE IF NOT EXISTS items (
  id TEXT PRIMARY KEY,
  source_type TEXT NOT NULL CHECK (source_type IN ('note', 'url')),
  title TEXT NOT NULL,
  source_url TEXT,
  raw_content TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS chunks (
  id TEXT PRIMARY KEY,
  item_id TEXT NOT NULL REFERENCES items (id) ON DELETE CASCADE,
  chunk_index INTEGER NOT NULL,
  content TEXT NOT NULL,
  embedding BLOB NOT NULL,
  UNIQUE (item_id, chunk_index)
);

CREATE INDEX IF NOT EXISTS idx_chunks_item_id ON chunks (item_id);
CREATE INDEX IF NOT EXISTS idx_items_created_at ON items (created_at);
