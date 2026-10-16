import test from "node:test";
import assert from "node:assert/strict";
import {decodeRpc,requireToolRefusal} from "./review-protocol.mjs";

test("decodes only matching JSON-RPC response IDs",()=>{
  const s='event: message\ndata: {"jsonrpc":"2.0","id":5,"result":{"ok":true}}\n\n';
  assert.equal(decodeRpc(s,5).result.ok,true);
  assert.throws(()=>decodeRpc(s,6),/Missing matching/);
  assert.throws(()=>decodeRpc('{"jsonrpc":"2.0","id":3,"result":{}}',5),/Missing matching/);
});
test("recognizes real unknown-tool and input-schema refusals",()=>{
  const err='data: {"jsonrpc":"2.0","id":8,"error":{"code":-32602,"message":"Tool unknown not found"}}\n';
  assert.match(requireToolRefusal(200,err,8,"unknown-tool"),/not found/);
  const invalid='data: {"jsonrpc":"2.0","id":9,"result":{"isError":true,"content":[{"type":"text","text":"Invalid arguments"}]}}\n';
  assert.match(requireToolRefusal(200,invalid,9,"invalid-input"),/Invalid arguments/);
});
test("does not accept outages, malformed responses, unrelated IDs or successes",()=>{
  const refused='{"jsonrpc":"2.0","id":2,"error":{"code":-32602,"message":"Tool not found"}}';
  assert.throws(()=>requireToolRefusal(503,refused,2,"unknown-tool"),/Unexpected HTTP/);
  assert.throws(()=>requireToolRefusal(429,refused,2,"unknown-tool"),/Unexpected HTTP/);
  assert.throws(()=>requireToolRefusal(200,"<html>blocked</html>",2,"unknown-tool"));
  assert.throws(()=>requireToolRefusal(200,'{"jsonrpc":"2.0","id":9,"error":{"code":-32602,"message":"not found"}}',2,"unknown-tool"),/Missing matching/);
  assert.throws(()=>requireToolRefusal(200,'{"jsonrpc":"2.0","id":2,"result":{"isError":false}}',2,"invalid-input"),/validation feedback/);
  assert.throws(()=>requireToolRefusal(200,'{"jsonrpc":"2.0","id":2,"error":{"code":-32603,"message":"Database unavailable"}}',2,"unknown-tool"),/not-found error/);
});
