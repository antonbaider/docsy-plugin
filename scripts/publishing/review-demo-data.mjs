#!/usr/bin/env node
// Capture only public documentation metadata from the live MCP; no credentials.
import {writeFile} from 'node:fs/promises';

const base=process.env.DOCSY_PUBLIC_URL??'https://docsy.remcp.site';
const output=process.argv[2]??'/tmp/docsy-review-live-data.json';
let id=0;
const scenes=[];
const headers={'Content-Type':'application/json','Accept':'application/json, text/event-stream','MCP-Protocol-Version':'2025-11-25'};
const assert=(ok,message)=>{if(!ok)throw Error(message)};
async function rpc(method,params={},allowError=false){
  const callId=++id;
  const response=await fetch(base+'/mcp/registry',{method:'POST',headers,
    body:JSON.stringify({jsonrpc:'2.0',id:callId,method,params}),
    signal:AbortSignal.timeout(45000)});
  const raw=await response.text();
  const events=raw.split(/\r?\n/).filter(l=>l.startsWith('data: ')).map(l=>JSON.parse(l.slice(6)));
  const result=events.find(m=>m.id===callId)??(events.length?events[0]:JSON.parse(raw));
  if(!allowError){
    assert(response.ok && result.result && !result.error,method+' failed');
  }
  return result;
}
async function call(name,args={}){
  const result=(await rpc('tools/call',{name,arguments:args})).result;
  assert(!result.isError,name+' tool error');
  return (result.content??[]).filter(c=>c.type==='text').map(c=>c.text).join('\n');
}
function sourceUrls(s){
  return [...new Set([...s.matchAll(/Source:\s+(https:\/\/[^\s]+)/g)].map(x=>x[1]))].slice(0,3);
}
function add(tag,title,command,outputLines,caption){
  scenes.push({tag,title,command,outputLines:outputLines.slice(0,7),caption});
}
const init=(await rpc('initialize',{protocolVersion:'2025-11-25',capabilities:{},
  clientInfo:{name:'docsy-plugin-review-demo',version:'1.0.0'}})).result;
const defs=(await rpc('tools/list')).result.tools;
assert(init.serverInfo?.name==='Docsy' && defs.length===5,'unexpected MCP contract');
assert(defs.every(t=>t.annotations?.readOnlyHint===true),'tools must be read-only');
add('01 / CONNECTION','Remote MCP verified','POST '+base+'/mcp/registry',
  ['Streamable HTTP · protocol '+init.protocolVersion,
   'Server: '+init.serverInfo.name,
   'Five tools available / five read-only',
   ...defs.map(t=>'  '+t.name)],'Public endpoint · anonymous · HTTPS');

const react=await call('resolve-library-id',{libraryName:'React',query:'useEffect cleanup'});
assert(react.includes('/reactjs/react.dev'),'React library not found');
add('02 / RESOLVE','Find the official library',
  'resolve-library-id  { libraryName: "React" }',
  ['Library: React','Resolved ID: /reactjs/react.dev',
   'Source: public documentation index'],'No guessed repositories · stable library IDs');
const reactDocs=await call('query-docs',{libraryId:'/reactjs/react.dev',query:'useEffect cleanup',limit:2});
const reactUrls=sourceUrls(reactDocs);
assert(reactUrls.length>0,'React docs source missing');
add('03 / RETRIEVE','Focused documentation',
  'query-docs  { libraryId: "/reactjs/react.dev", query: "useEffect cleanup" }',
  ['Retrieved real source-linked excerpts',
   'Indexed version: '+(reactDocs.match(/Version:\s*([^\n]+)/)?.[1]??'available'),
   ...reactUrls.map(u=>'Source: '+u),
   'Content length: '+reactDocs.length+' chars'],'Excerpt bodies omitted here; source URLs are genuine');

const versions=await call('list-library-versions',{libraryId:'/reactjs/react.dev'});
assert(versions.length>0,'version list missing');
add('04 / VERSIONS','Version-aware context','list-library-versions  { libraryId: "/reactjs/react.dev" }',
  ['Indexed version information retrieved',
   ...versions.split('\n').map(x=>x.trim()).filter(Boolean).slice(0,4).map(x=>x.slice(0,125))],
  'Use an indexed version when available');

const query=await call('search',{query:'React useEffect cleanup'});
const hits=JSON.parse(query);
assert(Array.isArray(hits)&&hits.length>0,'search has no results');
const hit=hits.find(x=>x.id && x.url?.startsWith('https://'));
assert(hit,'search result missing source');
add('05 / SEARCH','Search all public docs','search  { query: "React useEffect cleanup" }',
  ['Search returned '+hits.length+' public results',
   'First result ID: '+hit.id,
   'Original source: '+hit.url,
   'Read-only retrieval'],'Document IDs resolve via fetch');

const doc=await call('fetch',{id:hit.id});
assert(doc.includes('Source: https://'),'fetch missing source');
add('06 / FETCH','Fetch exact document','fetch  { id: "'+hit.id+'" }',
  ['Fetched referenced documentation chunk',
   'Source: '+(sourceUrls(doc)[0]??'https://docsy.remcp.site'),
   'Result size: '+doc.length+' chars',
   'Original source attribution preserved'],'No user data, mutations or credentials');
const fastify=await call('resolve-library-id',{libraryName:'Fastify',query:'request validation'});
assert(fastify.includes('/fastify/fastify'),'Fastify library missing');
const fastifyDocs=await call('query-docs',{libraryId:'/fastify/fastify',query:'request validation JSON schema',limit:2});
const fastifySources=sourceUrls(fastifyDocs);
assert(fastifySources.length>0,'Fastify docs missing citations');
add('07 / EXAMPLE','Second real-world question',
  'query-docs  { libraryId: "/fastify/fastify", query: "request validation" }',
  ['Official Fastify docs resolved',
   'Found '+fastifySources.length+' cited excerpts',
   ...fastifySources.map(x=>'Source: '+x)],'Independent libraries · version-aware source references');

const forbidden=await rpc('tools/call',{name:'delete-every-library',arguments:{}},true);
assert(Boolean(forbidden.error||forbidden.result?.isError),'unknown tool not rejected');
const malformed=await rpc('tools/call',{name:'query-docs',arguments:{libraryId:'/reactjs/react.dev'}},true);
assert(Boolean(malformed.error||malformed.result?.isError),'malformed input not rejected');
const missing=await call('fetch',{id:'00000000-0000-4000-8000-000000000000'});
assert(missing.trim()==='Document not found.','missing fetch disclosure');
add('08 / SAFETY','Read-only and fail-closed',
  'Negative tests: delete library · invalid parameters · nonexistent ID',
  ['Unknown mutation tool: rejected',
   'Missing required query argument: rejected',
   'Nonexistent document ID: Document not found',
   'All five tools: readOnlyHint=true'],'No private repositories or credentials exposed');

const statuses=[];
for(const route of ['/privacy','/terms','/support']){
  const r=await fetch(base+route,{signal:AbortSignal.timeout(12000)});
  assert(r.ok,route+' returned '+r.status);
  statuses.push(route+' HTTP '+r.status);
}
add('09 / READY','Ready for directory review',
  'HTTPS  ·  Source-linked docs  ·  Public support',
  [...statuses, 'Plugin source: github.com/getremcp/docsy-plugin',
   'Approved listings: pending marketplace review'],
  'Official listing only after review and publishing');

await writeFile(output,JSON.stringify({
  title:'Docsy MCP · real live-review walkthrough',capturedAt:new Date().toISOString(),
  endpoint:base+'/mcp/registry',scenes
},null,2)+'\n',{mode:0o600});
console.log('Captured '+scenes.length+' scenes of real public MCP output to '+output);
