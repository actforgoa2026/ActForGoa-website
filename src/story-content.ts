import type { RecordItem } from "./types";

type ReadingBlock = RecordItem["blocks"][number] & { href?: string };
const readMore = /^read\s+(?:more|(?:the\s+)?full\s+(?:article|story))(?:\s+here)?[\s:.!]*$/i;

export function storyContent(record: RecordItem) {
  const blocks: ReadingBlock[] = [];
  const inlineUrls = new Set<string>();
  const storyUrl = (text: string) => {
    if (!/^https?:\/\/\S+$/i.test(text)) return undefined;
    try {
      const url = new URL(text);
      // Downloads and media keep their existing presentation.
      if (/\.(?:pdf|docx?|xlsx?|pptx?|jpe?g|png|gif|webp|mp4|mp3|wav|zip)$/i.test(url.pathname)
        || record.documents.some(document => document.url === text)) return undefined;
      return text;
    } catch {
      return undefined;
    }
  };
  const appendLink = (href: string) => {
    if (inlineUrls.has(href)) return;
    inlineUrls.add(href);
    blocks.push({ type: "paragraph", text: "Read the full story here.", href });
  };

  for (let i = 0; i < record.blocks.length; i++) {
    const block = record.blocks[i];
    const text = block.text.trim();
    if (record.kind === "story") {
      const href = storyUrl(text);
      if (href) {
        appendLink(href);
        continue;
      }
      if (readMore.test(text)) {
        const nextUrl = storyUrl(record.blocks[i + 1]?.text.trim() ?? "");
        if (nextUrl) {
          appendLink(nextUrl);
          i++;
          continue;
        }
        const matches = record.links.filter(link =>
          (link.label.trim().toLowerCase() === text.toLowerCase() || /^here$/i.test(link.label.trim()))
          && storyUrl(link.url),
        );
        if (matches.length === 1) {
          appendLink(matches[0].url);
          continue;
        }
      }
    }
    blocks.push(block);
  }

  return {
    blocks,
    links: record.links.filter(link => !inlineUrls.has(link.url)),
  };
}
