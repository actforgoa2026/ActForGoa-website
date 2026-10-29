/** Only web destinations outside this running site open a separate tab. */
export function isExternalWebsite(href: string, origin: string): boolean {
  if (!href.trim()) return false;
  try {
    const url = new URL(href, origin);
    return (url.protocol === 'https:' || url.protocol === 'http:') && url.origin !== new URL(origin).origin;
  } catch { return false; }
}

/** Covers static links, rendered Markdown, lazy routes and third-party map attribution. */
export function installExternalLinks(root: HTMLElement, origin = window.location.origin) {
  const changed = new WeakMap<HTMLAnchorElement, {target: string | null; rel: string | null}>();
  function update(link: HTMLAnchorElement) {
    const external = !link.hasAttribute('download') && isExternalWebsite(link.getAttribute('href') || '', origin);
    if (external) {
      if (!changed.has(link)) changed.set(link, {target: link.getAttribute('target'), rel: link.getAttribute('rel')});
      link.target = '_blank';
      const rel = new Set((link.getAttribute('rel') || '').split(/\s+/).filter(Boolean));
      rel.delete('opener'); rel.add('noopener'); rel.add('noreferrer');
      link.rel = [...rel].join(' ');
    } else if (changed.has(link)) {
      const original = changed.get(link)!;
      for (const attribute of ['target', 'rel'] as const) {
        if (original[attribute] === null) link.removeAttribute(attribute);
        else link.setAttribute(attribute, original[attribute]!);
      }
      changed.delete(link);
    }
  }
  function scan(node: Node) {
    if (!(node instanceof Element)) return;
    if (node instanceof HTMLAnchorElement) update(node);
    node.querySelectorAll<HTMLAnchorElement>('a[href]').forEach(update);
  }
  scan(root);
  const observer = new MutationObserver(records => {
    for (const record of records) {
      if (record.type === 'attributes' && record.target instanceof HTMLAnchorElement) update(record.target);
      else record.addedNodes.forEach(scan);
    }
  });
  observer.observe(root, {subtree: true, childList: true, attributes: true, attributeFilter: ['href', 'download']});
  return () => observer.disconnect();
}
