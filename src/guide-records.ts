import records from './content/guide-records.json';
import type { RecordItem } from './types';

// Searchable guide text is separate from the much larger source/review registers.
export const practicalGuideRecords = records as RecordItem[];
