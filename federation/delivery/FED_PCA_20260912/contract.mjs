import {z} from 'zod';
import fs from 'node:fs';
import crypto from 'node:crypto';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
export const Action=z.object({id:z.string().regex(/^A\d{2}$/),repo:z.enum(['mesh','CODEX','ABACUS','cryoplant-project','DOCX_RTM_Automation']),title:z.string().min(1),status:z.enum(['PASS','VERIFY','REPAIR','BLOCKED','PLANNED']),bt_rank:z.number().int().positive(),depends_on:z.array(z.string()),next_gate:z.string().min(1),evidence_urls:z.array(z.string().url()),sha:z.string().regex(/^[a-f0-9]{40}$/).nullable(),evidence_class:z.enum(['SOURCE-SUPPORTED','POSTULATED'])}).strict();
export const Register=z.object({schema_version:z.literal('1.0.0'),release:z.string(),document_reference:z.string(),observed_at:z.string().datetime(),scope:z.string(),global_dov:z.literal('WITHHELD'),ranking_basis:z.string(),actions:z.array(Action).min(1),federation:z.array(z.object({repo:z.string(),role:z.string(),consumes:z.string(),emits:z.string()}).strict()),expansion:z.array(z.object({horizon:z.string(),target:z.string(),resources:z.string(),exit:z.string()}).strict()),boundaries:z.array(z.string())}).strict().superRefine((r,ctx)=>{
 const ids=new Set();for(const a of r.actions){if(ids.has(a.id))ctx.addIssue({code:'custom',message:'Duplicate action '+a.id});ids.add(a.id);if(a.status==='PASS'&&!a.evidence_urls.length)ctx.addIssue({code:'custom',message:'PASS requires evidence '+a.id});}
 const byId=new Map(r.actions.map(a=>[a.id,a]));const active=new Set(),done=new Set();
 function visit(id){if(active.has(id)){ctx.addIssue({code:'custom',message:'Dependency cycle'});return;}if(done.has(id))return;const a=byId.get(id);if(!a){ctx.addIssue({code:'custom',message:'Missing dependency '+id});return;}active.add(id);for(const dep of a.depends_on){visit(dep);if(a.status==='PASS'&&byId.get(dep)?.status!=='PASS')ctx.addIssue({code:'custom',message:'Unsatisfied PASS dependency'});}active.delete(id);done.add(id);}for(const a of r.actions)visit(a.id);
});
const dir=path.dirname(fileURLToPath(import.meta.url));
if(process.argv[1]===fileURLToPath(import.meta.url)){
 const input=fs.readFileSync(path.join(dir,'delivery_ssot.json'));const data=Register.parse(JSON.parse(input));
 const mutants=[r=>r.actions.push({...r.actions[0]}),r=>r.actions[0].depends_on=['MISSING'],r=>r.actions[0].depends_on=['A02'],r=>r.actions[0].evidence_urls=[],r=>r.global_dov='ACHIEVED'];
 for(const mutate of mutants){const copy=structuredClone(data);mutate(copy);if(Register.safeParse(copy).success)throw Error('Negative control was accepted');}
 const receipt={release:data.release,ssot_sha256:crypto.createHash('sha256').update(input).digest('hex'),contract:'Zod',status:'PASS',valid_records:data.actions.length,negative_controls_rejected:mutants.length,scope:'Delivery structure, evidence presence and acyclic dependencies; not engineering acceptance'};
 fs.writeFileSync(path.join(dir,'contract_receipt.json'),JSON.stringify(receipt,null,2));console.log(JSON.stringify(receipt));
}
