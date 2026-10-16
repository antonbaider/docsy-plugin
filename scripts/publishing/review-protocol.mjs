/** Strict JSON-RPC response parsing for public MCP publication checks. */
export function decodeRpc(body,id){
  const events=body.split(/\r?\n/)
    .filter(line=>line.startsWith("data:"))
    .map(line=>JSON.parse(line.slice(5).trim()));
  const messages=events.length?events:[JSON.parse(body)];
  const response=messages.find(value=>value?.jsonrpc==="2.0"&&value.id===id);
  if(!response)throw new Error("Missing matching JSON-RPC response for request "+id);
  return response;
}

export function requireToolRefusal(status,body,id,kind){
  // Rate limits, CDN failures, auth errors and HTML challenges are not refusals.
  if(status!==200)throw new Error("Unexpected HTTP status "+status);
  const response=decodeRpc(body,id);
  if(kind==="unknown-tool"){
    if(response.error?.code===-32602&&/not found|unknown tool/i.test(response.error.message??"")){
      return response.error.message;
    }
    throw new Error("Unknown tool did not return a JSON-RPC not-found error");
  }
  if(kind==="invalid-input"){
    const message=(response.result?.content??[]).filter(item=>item.type==="text")
      .map(item=>item.text).join("\n");
    if(response.result?.isError===true&&/invalid arguments|input validation/i.test(message)){
      return message;
    }
    throw new Error("Malformed tool arguments did not yield validation feedback");
  }
  throw new Error("Unknown negative test kind "+kind);
}
