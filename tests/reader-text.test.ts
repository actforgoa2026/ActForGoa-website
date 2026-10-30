import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readerBlocks} from '../src/reader-text';

test('reader joins print lines while preserving paragraphs and mixed-case headings', () => {
 assert.deepEqual(readerBlocks('Rain falls in the post-monsoon\nmonths. Winters are dry.\n\nGeographical Features that influence climate in Goa\nGoa has a peculiar geographic orientation with the Arabian Sea on the West\nand the Western Ghats on its eastern boundary.'), [
  {kind:'paragraph',text:'Rain falls in the post-monsoon months. Winters are dry.'},
  {kind:'heading',text:'Geographical Features that influence climate in Goa'},
  {kind:'paragraph',text:'Goa has a peculiar geographic orientation with the Arabian Sea on the West and the Western Ghats on its eastern boundary.'},
 ]);
});

test('reader preserves table columns, captions and list boundaries', () => {
 assert.deepEqual(readerBlocks('Figure 13: Annual rainfall\nPlace\t\tRain\nGoa\t\t200\n\n• First item\n• Second item'), [
  {kind:'paragraph',text:'Figure 13: Annual rainfall'},
  {kind:'table',text:'Place\t\tRain\nGoa\t\t200'},
  {kind:'paragraph',text:'• First item'},
  {kind:'paragraph',text:'• Second item'},
 ]);
});
