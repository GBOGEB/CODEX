import { z } from 'zod';

export const RuntimeRoleSchema = z.enum(['CANONICAL_RUNTIME','THIN_RUNNER','SERVICE_CONTRACT_DONOR','COMPATIBILITY_WRAPPER','TEST','SCHEMA','REGISTRY','CONFIG','DOCUMENTATION']);
export const RuntimeDispositionSchema = z.enum(['KEEP','MIGRATE_CAPABILITY','REQUALIFY_BEFORE_FOLD','WRAP','PRUNE_AFTER_PARITY','NON_RUNTIME']);
export const RuntimeMemberSchema = z.object({path:z.string().min(1),role:RuntimeRoleSchema,disposition:RuntimeDispositionSchema,active:z.boolean(),uniqueCapabilities:z.array(z.string()).default([])});
export const MCPRuntimeFamilySchema = z.object({
  family:z.literal('MCP_SWEEP'),
  canonicalRuntime:z.literal('src/federation/mcp_sweep_engine.py'),
  canonicalRunner:z.literal('scripts/run_mcp_sweep.py'),
  authorityInvariant:z.literal('ONE_CANONICAL_RUNTIME'),
  engineeringAuthorityMutation:z.literal(false),
  members:z.array(RuntimeMemberSchema).min(1),
}).superRefine((v,ctx)=>{
  const runtimes=v.members.filter(m=>m.role==='CANONICAL_RUNTIME'&&m.active);
  if(runtimes.length!==1||runtimes[0]?.path!==v.canonicalRuntime) ctx.addIssue({code:z.ZodIssueCode.custom,message:'exactly one canonical MCP runtime required'});
  const runners=v.members.filter(m=>m.role==='THIN_RUNNER'&&m.active);
  if(runners.length!==1||runners[0]?.path!==v.canonicalRunner) ctx.addIssue({code:z.ZodIssueCode.custom,message:'exactly one canonical MCP runner required'});
});
export type MCPRuntimeFamily=z.infer<typeof MCPRuntimeFamilySchema>;
