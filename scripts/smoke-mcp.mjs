import { execFileSync } from 'node:child_process';

/** Verify a protected immutable Vercel deployment before promoting its alias. */
export function smokeMcp(deploymentUrl) {
  function request(id, method, params) {
    const body = JSON.stringify({ jsonrpc: '2.0', id, method, params });
    const raw = execFileSync('vercel', ['curl', '/api/mcp', '--deployment', deploymentUrl, '--', '--fail', '--silent', '--show-error', '--max-time', '30', '-X', 'POST', '-H', 'Content-Type: application/json', '-H', 'Accept: application/json, text/event-stream', '--data', body], {encoding: 'utf8', timeout: 35000});
    const message = JSON.parse(raw);
    if (message.jsonrpc !== '2.0' || message.id !== id || message.error || !message.result) throw new Error(`MCP ${method} failed: ${JSON.stringify(message.error || message)}`);
    return message.result;
  }
  const init = request(1, 'initialize', {protocolVersion:'2025-03-26', capabilities:{}, clientInfo:{name:'actforgoa-release',version:'1'}});
  if (!init.serverInfo || !init.protocolVersion) throw new Error('MCP initialization is invalid.');
  const listed = request(2, 'tools/list', {});
  for (const [name, query] of [['search_site','wildlife'],['search_directory','waste'],['search_research','khazan wetlands']]) {
    if (!Array.isArray(listed.tools) || !listed.tools.some(tool => tool.name === name)) throw new Error(`MCP tool ${name} missing.`);
    const result = request(3, 'tools/call', {name, arguments:{query,limit:2}});
    if (result.isError || !Array.isArray(result.content)) throw new Error(`MCP tool ${name} failed.`);
    const text = result.content.find(item => item.type === 'text')?.text;
    const payload = JSON.parse(text);
    if (!Array.isArray(payload.results) || payload.results.length === 0) throw new Error(`MCP tool ${name} returned no results.`);
  }
}
