import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';
import bundle from './data/simulation_snapshot.json';
import { assertBundle } from './types/simulation_contract';

// JSON imports are inferred with widened values and heterogeneous partial upserts.
// Validate the runtime contract before passing it to the typed application.
const rawBundle: unknown = bundle;
assertBundle(rawBundle);

createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App bundle={rawBundle} />
  </React.StrictMode>
);
