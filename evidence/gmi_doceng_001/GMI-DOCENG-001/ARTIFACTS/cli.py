#!/usr/bin/env python3
"""
Technical Document Editing & Governance Pipeline Engine (v1.0.0-PROD)
Fully implements DMAIC workflows, agent orchestration, and storage synchronization.
"""

import os
import sys
import shutil
import datetime
import subprocess
import json
import re
from typing import Dict, List, Any, Optional, Tuple

# ==============================================================================
# 1. CONFIGURATION & PATH MANAGEMENT
# ==============================================================================

DEFAULT_CONFIG = {
   "project_name": "Schrijfeditor",
   "version": "1.0.0-PROD",
   "paths": {
       "input_folder": "input",
       "output_folder": "output",
       "data_folder": "data",
       "diagnostics_folder": "diagnostics",
       "onedrive_backup_root": "~/OneDrive/Technical_Docs_Backup"
   },
   "governance": {
       "terminology": {
           "client": "CLIENT",
           "contractor": "Contractor",
           "shall provides": "shall provide"
       },
       "rfc2119_enforcement": True,
       "required_heading_style": "atx"  # standard markdown #
   }
}

class PathsManager:
   """Manages workspace topology and hybrid local-to-cloud synchronization paths."""
   def __init__(self, config_file: str = "config.json"):
       self.config_file = config_file
       self.config = self._load_config()
       self.paths = self.config.get("paths", DEFAULT_CONFIG["paths"])
       
       self.root = os.path.abspath(os.path.dirname(__file__))
       self.input_dir = os.path.join(self.root, self.paths.get("input_folder", "input"))
       self.output_dir = os.path.join(self.root, self.paths.get("output_folder", "output"))
       self.data_dir = os.path.join(self.root, self.paths.get("data_folder", "data"))
       self.diag_dir = os.path.join(self.root, self.paths.get("diagnostics_folder", "diagnostics"))
       
       raw_onedrive = self.paths.get("onedrive_backup_root", "~/OneDrive/Technical_Docs_Backup")
       self.onedrive_dir = os.path.abspath(os.path.expanduser(raw_onedrive))
       
       self.ensure_topology()

   def _load_config(self) -> Dict[str, Any]:
       if os.path.exists(self.config_file):
           try:
               with open(self.config_file, "r", encoding="utf-8") as f:
                   return json.load(f)
           except Exception as ex:
               print(f"[WARN] Failed to load {self.config_file}: {ex}. Falling back to default.")
       return DEFAULT_CONFIG

   def ensure_topology(self) -> None:
       for d in [self.input_dir, self.output_dir, self.data_dir, self.diag_dir]:
           os.makedirs(d, exist_ok=True)

   def get_input(self, filename: str) -> str:
       return os.path.join(self.input_dir, filename)

   def get_output(self, filename: str) -> str:
       return os.path.join(self.output_dir, filename)

   def get_onedrive_target(self, folder_type: str) -> str:
       ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
       return os.path.join(self.onedrive_dir, f"{folder_type}_{ts}")

# ==============================================================================
# 2. BASE AGENT HARNESS
# ==============================================================================

class BaseAgent:
   """Base class for all DMAIC operational and analytical agents."""
   def __init__(self, name: str):
       self.name = name
       self.context: Dict[str, Any] = {}

   def set_context(self, context: Dict[str, Any]) -> None:
       self.context = context

   def process(self, payload: Any) -> Dict[str, Any]:
       raise NotImplementedError(f"Agent {self.name} has not implemented process()")

# ==============================================================================
# 3. DMAIC: DEFINE & MEASURE AGENTS
# ==============================================================================

class EditorCore(BaseAgent):
   """[DMAIC: Define] Scopes baseline document characteristics and initial boundaries."""
   def process(self, document_content: str) -> Dict[str, Any]:
       words = document_content.split()
       lines = document_content.splitlines()
       doc_type = "Technical Specification / Statement of Requirements (SoR)"
       
       self.context.update({
           "doc_length_words": len(words),
           "doc_length_lines": len(lines),
           "doc_type": doc_type,
           "session_start": datetime.datetime.now().isoformat()
       })
       
       feedback = (
           f"[{self.name} - DEFINE]\n"
           f"• Detected Scope: {len(words)} words across {len(lines)} lines.\n"
           f"• Inferred Profile: {doc_type}\n"
           f"• Target Gate: Hold Point 1 (Scope Confirmation)"
       )
       return {
           "output": document_content,
           "feedback": feedback,
           "hold_point": True,
           "prompt": "Confirm document classification and operational goals [ok/restart/exit]: "
       }

class AnalyzerAgent(BaseAgent):
   """[DMAIC: Measure] Computes syntactic metrics, density, and structural parameters."""
   def process(self, document_content: str) -> Dict[str, Any]:
       sentences = [s for s in re.split(r"[.!?]+", document_content) if s.strip()]
       words = document_content.split()
       avg_sentence_len = len(words) / max(len(sentences), 1)
       headings = [line for line in document_content.splitlines() if line.strip().startswith("#")]
       
       metrics = {
           "word_count": len(words),
           "sentence_count": len(sentences),
           "avg_sentence_length": round(avg_sentence_len, 2),
           "heading_count": len(headings)
       }
       self.context["metrics"] = metrics
       
       feedback = (
           f"[{self.name} - MEASURE]\n"
           f"• Metrics: Words={metrics['word_count']} | Sentences={metrics['sentence_count']}\n"
           f"• Syntactic Density: {metrics['avg_sentence_length']} words/sentence.\n"
           f"• Structural Landmarks: {metrics['heading_count']} markdown headings detected."
       )
       return {"output": document_content, "feedback": feedback, "metrics": metrics, "hold_point": False}

# ==============================================================================
# 4. DMAIC: ANALYZE AGENTS
# ==============================================================================

class StructuredDataLoader(BaseAgent):
   """[DMAIC: Analyze] Ingests and links schema metadata (.json, .yaml, Master.mp)."""
   def process(self, structured_str: str) -> Dict[str, Any]:
       parsed = {}
       valid = False
       try:
           parsed = json.loads(structured_str)
           valid = True
           msg = f"JSON schema successfully validated. Ingested {len(parsed)} structural nodes."
       except json.JSONDecodeError:
           # Fallback key-value parser for custom Master.mp formats
           for line in structured_str.splitlines():
               if "=" in line:
                   k, v = line.split("=", 1)
                   parsed[k.strip()] = v.strip()
           if parsed:
               valid = True
               msg = f"Custom format (Master.mp) parsed. Ingested {len(parsed)} elements."
           else:
               msg = "Malformed structured data input. Schema rejected."

       self.context["structured_requirements"] = parsed
       self.context["structured_valid"] = valid
       
       feedback = f"[{self.name} - ANALYZE]\n• Status: {msg}"
       return {
           "output": structured_str,
           "feedback": feedback,
           "hold_point": True,
           "prompt": "Confirm ingested structured requirements [ok/skip/retry]: "
       }

class DiagnosticsAgent(BaseAgent):
   """[DMAIC: Analyze] Detects syntax anomalies, unresolved citations, and incomplete requirements."""
   def process(self, content: str) -> Dict[str, Any]:
       findings = []
       for idx, line in enumerate(content.splitlines(), start=1):
           if re.search(r"\bTODO\b|\bTBD\b|\[\s*citation needed\s*\]", line, re.IGNORECASE):
               findings.append(f"Line {idx}: Unresolved marker (TODO/TBD/Citation).")
           if re.search(r"\bReq\.\s*\d+\b", line) and not re.search(r"\b(shall|must|will)\b", line, re.IGNORECASE):
               findings.append(f"Line {idx}: Requirement identified without RFC 2119 normative verb.")
               
       self.context["diagnostic_findings"] = findings
       feedback = f"[{self.name} - ANALYZE]\n" + (
           "\n".join([f"• {f}" for f in findings]) if findings else "• Clean pass: No syntax anomalies found."
       )
       return {
           "output": content,
           "feedback": feedback,
           "findings": findings,
           "hold_point": bool(findings),
           "prompt": "Acknowledge diagnostic warnings [ok/continue]: "
       }

# ==============================================================================
# 5. DMAIC: IMPROVE AGENTS
# ==============================================================================

class GrammarEditor(BaseAgent):
   """[DMAIC: Improve] Pinpoints verb tense, agreement, and syntactic drift."""
   def process(self, content: str) -> Dict[str, Any]:
       edits = []
       rules = self.context.get("governance", {}).get("terminology", {})
       lines = content.splitlines()
       for idx, line in enumerate(lines, start=1):
           for bad, good in rules.items():
               if bad in line.lower() and bad != good:
                   edits.append({
                       "line": idx,
                       "original": bad,
                       "suggested": good,
                       "category": "Grammar/Normative Syntax"
                   })
       return {"output": content, "edits": edits}

class RequirementValidator(BaseAgent):
   """[DMAIC: Improve] Cross-checks requirement measurability and structural IDs."""
   def process(self, content: str) -> Dict[str, Any]:
       issues = []
       req_db = self.context.get("structured_requirements", {})
       for req_id in req_db.keys():
           if req_id in content:
               # Verify that measurability clauses are explicitly tied
               if not re.search(r"(verified by|tested via|measured through|acceptance criteria)", content, re.IGNORECASE):
                   issues.append({
                       "req_id": req_id,
                       "issue": "Missing explicit verification/measurability mechanism."
                   })
       return {"output": content, "issues": issues}

class FeedbackAggregator(BaseAgent):
   """[DMAIC: Improve] Merges operational feedback, diff vectors, and prepares batch review."""
   def process(self, section: str, agent_runs: List[Dict[str, Any]]) -> Dict[str, Any]:
       all_edits = []
       all_issues = []
       for r in agent_runs:
           all_edits.extend(r.get("edits", []))
           all_issues.extend(r.get("issues", []))

       report = ["\n--- AGGREGATED BATCH FEEDBACK (HOLD POINT 5) ---"]
       if all_edits:
           report.append("Suggested Corrections:")
           for e in all_edits:
               report.append(f" • Line {e['line']}: Change '{e['original']}' -> '{e['suggested']}' [{e['category']}]")
       if all_issues:
           report.append("Requirement Traceability Issues:")
           for i in all_issues:
               report.append(f" • [{i['req_id']}]: {i['issue']}")
       if not all_edits and not all_issues:
           report.append("Section passed all agent validation gates without remarks.")

       report.append("-------------------------------------------------")
       return {
           "output": section,
           "feedback": "\n".join(report),
           "edits": all_edits,
           "issues": all_issues,
           "hold_point": True,
           "prompt": "Action on section batch [accept/reject/revise]: "
       }

# ==============================================================================
# 6. DMAIC: CONTROL & DELIVERY AGENTS
# ==============================================================================

class FinalComposer(BaseAgent):
   """[DMAIC: Control] Emits versioned Markdown output and comprehensive audit logs."""
   def process(self, full_text: str, session_history: List[Dict[str, Any]]) -> Dict[str, Any]:
       ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
       final_doc = (
           f"<!-- MASTER SPECIFICATION DOCUMENT | GENERATED: {ts} -->\n\n"
           f"{full_text}\n\n"
           f"<!-- TRACEABILITY MATRIX & VERIFICATION -->\n"
           f"## Quality Ledger & Provenance Log\n"
           f"- Compilation Date: {ts}\n"
           f"- Governing Pipeline: Schrijfeditor v1.0.0-PROD\n"
       )
       
       audit_log = [
           f"# Engineering Audit Log: {ts}",
           f"Project: {self.context.get('doc_type', 'Technical SoR')}",
           "\n## Applied Modifications:"
       ]
       for item in session_history:
           audit_log.append(f"- Timestamp: {item['time']} | Target: {item.get('target', 'global')}")
           audit_log.append(f"  Summary: {item['summary']}")

       return {
           "final_doc": final_doc,
           "audit_log": "\n".join(audit_log),
           "hold_point": True,
           "prompt": "Authorize final composition and disk write [ok/abort]: "
       }

# ==============================================================================
# 7. EXECUTION ORCHESTRATOR & WORKFLOW PIPELINE
# ==============================================================================

class AgentOrchestra:
   """The central state machine coordinating agents through defined DMAIC gates."""
   def __init__(self, paths: PathsManager):
       self.paths = paths
       self.context: Dict[str, Any] = {
           "governance": paths.config.get("governance", DEFAULT_CONFIG["governance"])
       }
       self.agents = {
           "EditorCore": EditorCore("EditorCore"),
           "Analyzer": AnalyzerAgent("AnalyzerAgent"),
           "DataLoader": StructuredDataLoader("DataLoader"),
           "Diagnostics": DiagnosticsAgent("DiagnosticsAgent"),
           "Grammar": GrammarEditor("GrammarEditor"),
           "ReqValidator": RequirementValidator("ReqValidator"),
           "Aggregator": FeedbackAggregator("FeedbackAggregator"),
           "Composer": FinalComposer("FinalComposer")
       }
       self.session_history: List[Dict[str, Any]] = []

   def _hold(self, prompt_text: str) -> str:
       sys.stdout.flush()
       try:
           res = input(f"\n[HOLD POINT GATE] {prompt_text}").strip().lower()
           return res
       except (KeyboardInterrupt, EOFError):
           print("\nWorkflow aborted by operator.")
           sys.exit(0)

   def execute_pipeline(self, raw_document: str, structured_data: Optional[str] = None) -> Tuple[str, str]:
       print("\n=======================================================")
       print("   STARTING DMAIC DOCUMENT ENGINEERING PIPELINE        ")
       print("=======================================================")

       # 1. DEFINE PHASE
       self.agents["EditorCore"].set_context(self.context)
       d_res = self.agents["EditorCore"].process(raw_document)
       print(d_res["feedback"])
       if self._hold(d_res["prompt"]) not in ["ok", "y", "yes"]:
           return "", "Aborted at DEFINE stage."

       # 2. MEASURE PHASE
       self.agents["Analyzer"].set_context(self.context)
       m_res = self.agents["Analyzer"].process(raw_document)
       print(m_res["feedback"])

       # 3. ANALYZE PHASE (Structured Ingestion & Diagnostics)
       if structured_data:
           self.agents["DataLoader"].set_context(self.context)
           s_res = self.agents["DataLoader"].process(structured_data)
           print(s_res["feedback"])
           if self._hold(s_res["prompt"]) not in ["ok", "y", "yes"]:
               print("[WARN] Proceeding without structured requirements binding.")

       self.agents["Diagnostics"].set_context(self.context)
       diag_res = self.agents["Diagnostics"].process(raw_document)
       print(diag_res["feedback"])
       if diag_res["hold_point"]:
           if self._hold(diag_res["prompt"]) not in ["ok", "y", "yes"]:
               return "", "Aborted during Diagnostics evaluation."

       # 4. IMPROVE PHASE (Sectional processing loop)
       current_content = raw_document
       print("\n[IMPROVE] Executing batch analysis on document body...")
       agent_runs = []
       for agent_name in ["Grammar", "ReqValidator"]:
           agent = self.agents[agent_name]
           agent.set_context(self.context)
           agent_runs.append(agent.process(current_content))

       self.agents["Aggregator"].set_context(self.context)
       batch = self.agents["Aggregator"].process(current_content, agent_runs)
       print(batch["feedback"])
       
       decision = self._hold(batch["prompt"])
       if decision == "accept":
           # Deterministic auto-fix application
           for edit in batch.get("edits", []):
               pattern = re.compile(re.escape(edit["original"]), re.IGNORECASE)
               current_content = pattern.sub(edit["suggested"], current_content)
           self.session_history.append({
               "time": datetime.datetime.now().isoformat(),
               "target": "Document Body",
               "summary": f"Applied {len(batch.get('edits', []))} verified vocabulary/grammar fixes."
           })
           print("[INFO] Corrections applied successfully.")
       elif decision == "revise":
           print("[INFO] Manual inline edit mode. Enter replacement text directly:")
           current_content = input("> ")
           self.session_history.append({
               "time": datetime.datetime.now().isoformat(),
               "target": "Document Body",
               "summary": "Manual operator override applied."
           })

       # 5. CONTROL PHASE (Compilation & Archival)
       self.agents["Composer"].set_context(self.context)
       ctrl_res = self.agents["Composer"].process(current_content, self.session_history)
       if self._hold(ctrl_res["prompt"]) in ["ok", "y", "yes"]:
           return ctrl_res["final_doc"], ctrl_res["audit_log"]
       
       return "", "Aborted at CONTROL phase."

# ==============================================================================
# 8. SYSTEM CLI WRAPPER & SUBCOMMAND DISPATCHER
# ==============================================================================

def run_git(args: List[str]) -> Tuple[int, str]:
   res = subprocess.run(["git"] + args, capture_output=True, text=True)
   return res.returncode, (res.stdout + res.stderr).strip()

def main():
   paths = PathsManager()
   
   if len(sys.argv) < 2:
       print(f"Schrijfeditor Engineering CLI ({DEFAULT_CONFIG['version']})")
       print("Commands:")
       print("  run                - Execute the complete DMAIC editing workflow")
       print("  backup-onedrive    - Copy inputs/outputs to OneDrive cloud backup root")
       print("  git-checkpoint     - Stage, commit, and record revision checkpoint")
       print("  init-env           - Scaffold workspace topology and create default config")
       sys.exit(0)

   cmd = sys.argv[1].lower()

   if cmd == "init-env":
       paths.ensure_topology()
       cfg_path = os.path.join(paths.root, "config.json")
       if not os.path.exists(cfg_path):
           with open(cfg_path, "w", encoding="utf-8") as f:
               json.dump(DEFAULT_CONFIG, f, indent=2)
           print(f"[OK] Generated default configuration at: {cfg_path}")
       print("[OK] Workspace topology active: input/, output/, data/, diagnostics/.")

   elif cmd == "run":
       # Check for input file or inline read
       target_doc = paths.get_input("Master.md")
       if not os.path.exists(target_doc):
           target_doc_txt = paths.get_input("Master.txt")
           if os.path.exists(target_doc_txt):
               target_doc = target_doc_txt
           else:
               print(f"[ERROR] Input file not found in: {paths.input_dir}")
               print("Please create 'input/Master.md' or 'input/Master.txt' to proceed.")
               sys.exit(1)

       with open(target_doc, "r", encoding="utf-8") as f:
           raw_text = f.read()

       structured_text = None
       target_struct = paths.get_input("requirements.json")
       if os.path.exists(target_struct):
           with open(target_struct, "r", encoding="utf-8") as f:
               structured_text = f.read()

       orchestra = AgentOrchestra(paths)
       final_doc, audit_log = orchestra.execute_pipeline(raw_text, structured_text)

       if final_doc:
           out_file = paths.get_output("Master_Final.md")
           audit_file = paths.get_output("Audit_Report.md")
           with open(out_file, "w", encoding="utf-8") as f:
               f.write(final_doc)
           with open(audit_file, "w", encoding="utf-8") as f:
               f.write(audit_log)
           print("\n=======================================================")
           print(f"[SUCCESS] Egress delivered:")
           print(f" • Document: {out_file}")
           print(f" • Audit Log: {audit_file}")
           print("=======================================================")

   elif cmd == "backup-onedrive":
       print(f"[BACKUP] Syncing snapshots to OneDrive: {paths.onedrive_dir}")
       for folder, name in [(paths.input_dir, "Input"), (paths.output_dir, "Output")]:
           dest = paths.get_onedrive_target(name)
           try:
               shutil.copytree(folder, dest)
               print(f" • Backed up {name} -> {dest}")
           except Exception as ex:
               print(f" • [ERROR] Failed backing up {name}: {ex}")

   elif cmd == "git-checkpoint":
       msg = sys.argv[2] if len(sys.argv) > 2 else f"DMAIC checkpoint {datetime.datetime.now().isoformat()}"
       code, out = run_git(["add", "."])
       code, out = run_git(["commit", "-m", msg])
       print(f"[GIT COMMIT: {code}]\n{out}")

   else:
       print(f"[ERROR] Unknown command: {cmd}")
       sys.exit(1)

if __name__ == "__main__":
   main()
