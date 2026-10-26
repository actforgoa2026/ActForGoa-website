/** Keep an uncertain submission retryable even after visiting earlier steps. */
export function createSubmissionIdentity(uuid: () => string = () => crypto.randomUUID()) {
  let signature = '', key = '';
  return (payload: string) => {
    if (!key || signature !== payload) { signature = payload; key = uuid(); }
    return key;
  };
}
