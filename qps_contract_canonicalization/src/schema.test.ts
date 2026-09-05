import test from "node:test";import assert from "node:assert/strict";import { FederationContract } from "./schema.js";
const r={id:"A",canonicalId:"C",semanticGroupKey:"G",applicability:"APPLICABLE" as const,complianceStatus:"OPEN" as const,scoreEligible:true,reviewWeight:1,scopeTags:[],overrideEvidence:[]};
test("duplicate canonical is rejected",()=>assert.equal(FederationContract.safeParse({schemaVersion:"1.0.0",removedScopeTags:[],requirements:[r,{...r,id:"B"}]}).success,false));
test("removed scope resurrection is rejected",()=>assert.equal(FederationContract.safeParse({schemaVersion:"1.0.0",removedScopeTags:["QSN"],requirements:[{...r,scopeTags:["QSN"]}]}).success,false));
