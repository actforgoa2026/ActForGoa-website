type ReaderBlock = {kind: 'paragraph' | 'heading' | 'table'; text: string};

/** Reflow extracted print lines for display only; saved source and citations stay intact. */
export function readerBlocks(text: string): ReaderBlock[] {
 const blocks: ReaderBlock[] = [];
 let paragraph = '';
 const flush = () => { if (paragraph) blocks.push({kind:'paragraph', text:paragraph}); paragraph = ''; };
 for (const raw of text.replace(/\r\n?/g, '\n').split('\n')) {
  const line = raw.trim();
  if (!line) { flush(); continue; }
  if (raw.includes('\t')) {
   flush();
   const previous = blocks.at(-1);
   if (previous?.kind === 'table') previous.text += '\n' + raw;
   else blocks.push({kind:'table', text:raw});
   continue;
  }
  const words = line.split(/\s+/);
  const titleWords = words.filter(word => !/^(?:a|an|the|of|in|on|for|to|and|or|that|with|by|from)$/i.test(word));
  const heading = line.length < 85 && words.length >= 3 && !/[.!?;,]$/.test(line)
   && !/^(Figure|Table)\s+\d/i.test(line)
   && titleWords.filter(word => /^[A-Z][a-z]/.test(word)).length / titleWords.length >= .6;
  if (heading || /^(?:Figure|Table)\s+\d+[.:]/i.test(line) || /^\d+$/.test(line) || /^[•●▪]|^\d+[.)]\s/.test(line)) {
   flush(); blocks.push({kind:heading?'heading':'paragraph', text:line});
  } else {
   paragraph += (paragraph ? ' ' : '') + line;
  }
 }
 flush();
 return blocks;
}
