import {installExternalLinks} from './external-links';
import React from "react";
import { createRoot } from "react-dom/client";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import "@fontsource-variable/figtree";
import "./components/arc/foundation.css";
import "./styles.css";
import App from "./App";
import { LanguageProvider } from "./language";
import { CurationProvider } from "./CurationProvider";
import {TeamAccessProvider} from './TeamAccess';
import { createCatalogueLoader } from "./catalogue-loader";

const loadCatalogue = createCatalogueLoader();

const router = createBrowserRouter([
  {
    path: "*",
    element: <App />,
    errorElement: <main className="empty-state shell"><h1>This page couldn’t open.</h1><p>Please reload to try again.</p><a className="text-link" href="/">Open the field guide</a><a className="text-link" href="/emergency">Emergency services</a></main>,
    // Fetch once before rendering the route. Back/Forward restoration can now
    // measure the complete catalogue instead of an asynchronous loading shell.
    loader: ({ request }) => loadCatalogue(new URL(request.url).pathname),
    shouldRevalidate: ({ currentUrl, nextUrl }) => currentUrl.pathname !== nextUrl.pathname,
    HydrateFallback: () => (
      <main className="loading-state shell" role="status">
        <p>Opening your field guide…</p>
        <a className="text-link" href="/emergency">Need emergency services?</a>
      </main>
    ),
  },
]);
createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <LanguageProvider><CurationProvider><TeamAccessProvider><RouterProvider router={router} /></TeamAccessProvider></CurationProvider></LanguageProvider>
  </React.StrictMode>,
);

const stopExternalLinks = installExternalLinks(document.getElementById('root')!);
if (import.meta.hot) import.meta.hot.dispose(stopExternalLinks);
