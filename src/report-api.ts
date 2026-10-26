// The production API has persistent storage and accepts only this site's origin.
// Local development uses the Vite proxy.
const origin = (import.meta.env.VITE_REPORT_API_ORIGIN ?? '').replace(/\/$/, '');
export const reportApi = (path: string) => origin + path;
