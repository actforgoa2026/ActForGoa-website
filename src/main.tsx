import React from "react";
import { createRoot } from "react-dom/client";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import "@fontsource-variable/manrope";
import "./components/arc/foundation.css";
import "./styles.css";
import App from "./App";
import { publicCatalogue } from "./public-record";
import type { RecordItem } from "./types";

const router = createBrowserRouter([
  {
    path: "*",
    element: <App />,
    // Fetch once before rendering the route. Back/Forward restoration can now
    // measure the complete catalogue instead of an asynchronous loading shell.
    loader: async () => {
      try {
        const response = await fetch("/data/catalog.json");
        if (!response.ok) throw new Error("Catalogue unavailable");
        return { records: publicCatalogue((await response.json()) as RecordItem[]), error: false };
      } catch {
        return { records: [], error: true };
      }
    },
    shouldRevalidate: () => false,
    HydrateFallback: () => (
      <main className="loading-state shell" role="status">
        <p>Opening your field guide…</p>
      </main>
    ),
  },
]);
createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>,
);
