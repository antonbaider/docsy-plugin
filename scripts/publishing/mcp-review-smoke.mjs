// Reviewer-oriented public MCP contract verification. No credentials or writes.
const base=(process.env.DOCSY_PUBLIC_URL??"https://docsy.remcp.site").replace(/\/+$/,"");
const skipLegal=process.argv.includes("--skip-public-pages");
const headers={
  "content-type":"application/json",
  "accept":"application/json, text/event-stream",
  "MCP-Protocol-Version":"2025-11-25"
};
let calls=0;
const assert=(ok,message)=>{if(!ok)throw new Error(message);};
const timeout=ms=>AbortSignal.timeout(ms);
function parseRpc(body,id){
  const messages=body.split(/\r?\n/).filter(line=>line.startsWith("data: "))
    .map(line=>JSON.parse(line.slice(6)));
  const response=messages.find(m=>m?.id===id)??(messages.length?messages[0]:JSON.parse(body));
  if(response?.error)throw new Error("JSON-RPC failure "+JSON.stringify(response.error));
  assert(response?.result,"Missing JSON-RPC result for "+id);
  return response.result;
}
async function rpc(method,params={},ms=40_000){
  const id=++calls;
  const response=await fetch(base+"/mcp",{
    method:"POST",headers,
    body:JSON.stringify({jsonrpc:"2.0",id,method,params}),signal:timeout(ms)
  });
  assert(response.ok,"MCP "+method+" returned HTTP "+response.status);
  return parseRpc(await response.text(),id);
}
async function tool(name,args={},ms=40_000){
  const result=await rpc("tools/call",{name,arguments:args},ms);
  assert(!result.isError,"MCP "+name+" isError: "+JSON.stringify(result.content??[]).slice(0,250));
  return (result.content??[]).filter(c=>c.type==="text").map(c=>c.text).join("\n");
}
const init=await rpc("initialize",{
  protocolVersion:"2025-11-25",capabilities:{},
  clientInfo:{name:"docsy-directory-review-smoke",version:"1.0.0"}
});
assert(init.serverInfo?.name==="Docsy","MCP returned unexpected server name");
const listed=await rpc("tools/list");
const names=["resolve-library-id","query-docs","list-library-versions","search","fetch"];
assert((listed.tools??[]).length===5,"Public Docsy MCP tool count must stay exactly five");
for(const name of names){
  const def=listed.tools.find(t=>t.name===name);
  assert(def,"Missing MCP tool "+name);
  assert(def.annotations?.readOnlyHint===true,
    "MCP review requires correct readOnlyHint for "+name);
  assert(def.annotations?.destructiveHint===false,"MCP tool must not be destructive: "+name);
  // OpenAI's public MCP tool scan inspects all three safety hints. A public
  // documentation corpus reaches an open world of external sources even
  // though these advertised operations cannot mutate a user's account.
  assert(def.annotations?.openWorldHint===true,
    "MCP tool must disclose open-world public-documentation access: "+name);
  assert(def.annotations?.idempotentHint===true,
    "Public documentation retrieval should remain idempotent: "+name);
  assert(typeof def.description==="string"&&def.description.length>35,"Weak tool description: "+name);
  assert(def.inputSchema?.type==="object","Tool must define object input schema: "+name);
}
console.log("PASS initialize + 5 read-only annotated tools");
const resolved=await tool("resolve-library-id",{libraryName:"React",query:"useEffect cleanup"});
assert(resolved.includes("/reactjs/react.dev"),"React resolver did not return official ID");
console.log("PASS resolve-library-id");
const context=await tool("query-docs",{libraryId:"/reactjs/react.dev",query:"useEffect cleanup",limit:2},50_000);
assert(context.includes("Source: https://")&&context.includes("Version: ")&&context.length>80,
  "React documentation does not include source and version");
console.log("PASS query-docs");
const versions=await tool("list-library-versions",{libraryId:"/reactjs/react.dev"});
assert(versions.trim().length>0&&versions!=="No versions.","No known React documentation versions");
console.log("PASS list-library-versions");
const searchText=await tool("search",{query:"React useEffect cleanup"});
let results;
try{results=JSON.parse(searchText);}catch{throw new Error("Search must return JSON results");}
assert(Array.isArray(results)&&results.length>0,
  "Public cross-library search lacks a deterministic review result");
const candidate=results.find(x=>x.id&&x.url?.startsWith("https://"));
assert(candidate,"Search must provide a stable ID and original HTTPS source URL");
console.log("PASS search");
const fetched=await tool("fetch",{id:candidate.id});
assert(fetched.includes("Source: https://")&&fetched.length>70,"Fetch must return cited documentation");
console.log("PASS fetch");
const fastifyResolved=await tool("resolve-library-id",{libraryName:"Fastify",query:"request validation"});
assert(fastifyResolved.includes("/fastify/fastify"),"Fastify resolver missing official library ID");
const fastifyDocs=await tool("query-docs",{
  libraryId:"/fastify/fastify",query:"request validation JSON schema",limit:2
},50_000);
assert(fastifyDocs.includes("Source: https://")&&fastifyDocs.includes("Version: "),
  "Fastify review example lacks citations");
console.log("PASS Fastify review example");
const notFound=await tool("fetch",{id:"00000000-0000-4000-8000-000000000000"});
assert(notFound==="Document not found.","Unknown result IDs must not expose other user's content");
console.log("PASS safe missing-document fallback");
// Invalid tool names and missing required params must not be accepted as successful calls.
for(const invalid of [
  {name:"delete-every-library",args:{}},
  {name:"query-docs",args:{libraryId:"/reactjs/react.dev"}}
]){
  const id=++calls;
  const response=await fetch(base+"/mcp",{
    method:"POST",headers,
    body:JSON.stringify({jsonrpc:"2.0",id,method:"tools/call",params:{name:invalid.name,arguments:invalid.args}}),
    signal:timeout(15_000)
  });
  const body=await response.text();
  let refused=!response.ok;
  if(response.ok){
    try{
      const parsed=parseRpc(body,id);
      refused=Boolean(parsed.isError);
    }catch{refused=true;}
  }
  assert(refused,"Tool unexpectedly accepted an invalid operation: "+invalid.name);
}
console.log("PASS unknown/malformed tool refusals");
if(!skipLegal){
  for(const [path,needle] of [
    ["/privacy","Privacy policy"],["/terms","Terms of service"],
    ["/support","GitHub issue tracker"]
  ]){
    const res=await fetch(base+path,{signal:timeout(15_000),headers:{accept:"text/html"}});
    assert(res.ok&&res.headers.get("content-type")?.includes("text/html"),
      "Missing public directory legal page "+path+" (HTTP "+res.status+")");
    const html=await res.text();
    assert(html.toLowerCase().includes(needle.toLowerCase()),
      "Public directory page lacks expected title: "+path);
  }
  console.log("PASS privacy, terms and support HTTPS pages");
}
console.log("Docsy directory review smoke: PASS");
