export type {AdminUser, AdminSession, CuratedStar, BlogPost, PublicBlogPost, BlogPostSummary, PublicBlogPostSummary} from '../shared/admin';
export type {BlogInput as PostInput} from '../shared/admin';

export class AdminApiError extends Error {
  status: number;
  constructor(message: string, status: number) { super(message); this.name = 'AdminApiError'; this.status = status; }
}

/** Credentials stay in an HttpOnly cookie. Never persist passwords or CSRF tokens. */
export async function adminApi<T>(path: string, options: {method?: string; body?: unknown; csrfToken?: string; signal?: AbortSignal} = {}): Promise<T> {
  const controller = new AbortController();
  const cancel = () => controller.abort();
  options.signal?.addEventListener('abort', cancel, {once: true});
  if (options.signal?.aborted) controller.abort();
  const timer = setTimeout(cancel, 20000);
  try {
    const response = await fetch(path, {
      method: options.method || 'GET', credentials: 'same-origin', signal: controller.signal,
      headers: {...(options.body !== undefined ? {'Content-Type': 'application/json'} : {}), ...(options.csrfToken ? {'X-CSRF-Token': options.csrfToken} : {})},
      ...(options.body !== undefined ? {body: JSON.stringify(options.body)} : {}),
    });
    const data = response.status === 204 ? null : await response.json().catch(() => null);
    if (controller.signal.aborted) throw new DOMException('Request cancelled', 'AbortError');
    if (!response.ok) throw new AdminApiError(typeof data?.error === 'string' ? data.error : response.status === 401 ? 'Your sign-in has expired. Sign in again to save your changes.' : 'The service could not complete that request. Please try again.', response.status);
    if (data === null && response.status !== 204) throw new AdminApiError('The service returned an unreadable response. Please try again.', 502);
    return data as T;
  } catch (error) {
    if (options.signal?.aborted) throw new DOMException('Request cancelled', 'AbortError');
    if (error instanceof AdminApiError) throw error;
    throw new AdminApiError(controller.signal.aborted ? 'The request timed out. Check the saved result before trying again.' : 'Could not reach the team workspace. Check your connection and try again.', 0);
  } finally {
    clearTimeout(timer); options.signal?.removeEventListener('abort', cancel);
  }
}
