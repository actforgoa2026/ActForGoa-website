/** Append only recognized final text, preserving what the visitor has already typed. */
export function appendDictation(value: string, transcript: string, limit: number) {
 const spoken = transcript.trim();
 return spoken ? `${value}${value && !/\s$/.test(value) ? ' ' : ''}${spoken}`.slice(0, limit) : value;
}
