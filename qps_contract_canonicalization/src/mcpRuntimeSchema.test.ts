import test from 'node:test';
import assert from 'node:assert/strict';
import { MCPRuntimeFamilySchema } from './mcpRuntimeSchema.js';

const base={family:'MCP_SWEEP' as const,canonicalRuntime:'src/federation/mcp_sweep_engine.py' as const,canonicalRunner:'scripts/run_mcp_sweep.py' as const,authorityInvariant:'ONE_CANONICAL_RUNTIME' as const,engineeringAuthorityMutation:false as const,members:[
 {path:'src/federation/mcp_sweep_engine.py',role:'CANONICAL_RUNTIME' as const,disposition:'KEEP' as const,active:true,uniqueCapabilities:[]},
 {path:'scripts/run_mcp_sweep.py',role:'THIN_RUNNER' as const,disposition:'KEEP' as const,active:true,uniqueCapabilities:[]},
 {path:'src/mcp_sweep.py',role:'SERVICE_CONTRACT_DONOR' as const,disposition:'MIGRATE_CAPABILITY' as const,active:true,uniqueCapabilities:['token_scope_handshake']},
]};
test('accepts one canonical runtime and runner',()=>assert.equal(MCPRuntimeFamilySchema.safeParse(base).success,true));
test('rejects a second active canonical runtime',()=>{const bad={...base,members:[...base.members,{path:'src/mcp_sweep.py',role:'CANONICAL_RUNTIME' as const,disposition:'KEEP' as const,active:true,uniqueCapabilities:[]}]};assert.equal(MCPRuntimeFamilySchema.safeParse(bad).success,false);});
