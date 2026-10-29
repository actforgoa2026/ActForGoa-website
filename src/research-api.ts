const unavailable = 'The research service could not respond. Please try again.';

export async function researchApi<T>(url: string, init?: RequestInit): Promise<T> {
  const parent = init?.signal;
  if (parent?.aborted) throw new DOMException('Request cancelled', 'AbortError');
  const controller = new AbortController();
  const cancel = () => controller.abort();
  parent?.addEventListener('abort', cancel, { once: true });
  let timedOut = false;
  // Answers may need the provider's full 60-second window. Source requests
  // should recover sooner, including when the response body never finishes.
  const timer = setTimeout(() => {
    timedOut = true;
    controller.abort();
  }, url === '/api/chat' ? (import.meta.env?.VITE_LOCAL_AGENT==='1'?195_000:75_000) : 30_000);
  try {
    const response = await fetch(url, { ...init, signal: controller.signal });
    const data = await response.json().catch(error => {
      if (controller.signal.aborted) throw error;
      return null;
    });
    if (!response.ok) throw new Error(typeof data?.detail === 'string' ? data.detail : unavailable);
    if (data === null) throw new Error(unavailable);
    return data as T;
  } catch (error) {
    if (parent?.aborted) throw new DOMException('Request cancelled', 'AbortError');
    if (timedOut) throw new Error('This request is taking too long. Please try again shortly.');
    if (error instanceof TypeError) throw new Error('Could not connect to the research service. Check your connection and try again.');
    throw error;
  } finally {
    clearTimeout(timer);
    parent?.removeEventListener('abort', cancel);
  }
}
