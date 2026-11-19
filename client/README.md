# Client

React screen for the inbox. Vite proxies `/api` to the FastAPI process on http://localhost:3001, so the browser talks to one origin during development.

## Run this package alone

Start the server first, then:

```powershell
npm.cmd install
npm.cmd run dev
```

From the repo root, `npm.cmd run dev:client` does the same thing. `npm.cmd run build` writes `client/dist`. The server serves that folder when it is present.

## Screen

- `Composer` saves a note or a link. Switching between the two clears the form error. An empty field is rejected before a request is sent.
- `SavedList` lists what is stored. Remove asks for a second click.
- `AskPanel` sends a question and shows the answer as plain text.
- `SourceList` shows the numbered chunks the answer was written from, with a match score and a snippet.
- A banner from `useServerStatus` appears when `OPENAI_API_KEY` is empty, and an error banner appears when port 3001 is not responding.

State sits in three hooks: `useItems`, `useQuestion`, and `useServerStatus`. `api/client.js` is the only place that calls `fetch`.
