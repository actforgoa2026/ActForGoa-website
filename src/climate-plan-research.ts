// Verified against the hosted document metadata and the retained government PDF.
// Pin the immutable generation so later index rebuilds cannot change this edition.
export const climatePlanResearch = {
  documentId: 'd1b64d562f93c9cbabc39e1d-dc16e9345778',
  generation: '20261030-sapcc-native-v2',
  sha256: 'd1b64d562f93c9cbabc39e1d4be65f0515a06734792cfa5ea4eebf9544ff3cc6',
  starters: [
    'What does the SAPCC say about flooding, and what can residents do?',
    'What does Goa’s SAPCC propose for rainwater harvesting?',
    'What does Goa’s SAPCC propose for heat and health?',
    'What does Goa’s SAPCC propose for rooftop solar?',
  ],
} as const;

export const climatePlanResearchPath = '/ask/ecology?' + new URLSearchParams({
  document: climatePlanResearch.documentId, generation: climatePlanResearch.generation,
});
export const climatePlanReaderPath = `/documents/${climatePlanResearch.documentId}?` + new URLSearchParams({
  generation: climatePlanResearch.generation,
});

export function isClimatePlanResearch(documentId?: string, generation?: string): boolean {
  return documentId === climatePlanResearch.documentId && generation === climatePlanResearch.generation;
}
