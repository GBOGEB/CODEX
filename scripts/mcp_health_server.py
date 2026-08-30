#!/usr/bin/env python3
import json, os, time
from http.server import BaseHTTPRequestHandler,HTTPServer
START=time.time(); PORT=int(os.getenv('MCP_HEALTH_PORT','8765')); HOST=os.getenv('MCP_HEALTH_HOST','127.0.0.1'); WORKER=os.getenv('MCP_WORKER_ID','codex-mcp'); STATE=os.getenv('MCP_STATE_FILE','')
def state():
 s={'schema':'ops-kpi-v1','authority':'operational_non_evidence','worker_id':WORKER,'uptime_s':round(time.time()-START,1),'ready':True,'port':PORT}
 if STATE and os.path.exists(STATE):
  try:
   with open(STATE,encoding='utf-8') as f:s.update(json.load(f))
  except Exception as e:s['state_error']=type(e).__name__
 return s
class H(BaseHTTPRequestHandler):
 def log_message(self,*a):pass
 def out(self,o,c=200):
  b=json.dumps(o,sort_keys=True).encode();self.send_response(c);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b)
 def do_GET(self):
  if self.path in ('/health','/ready','/metrics'):self.out(state())
  elif self.path.startswith('/debug/') and os.getenv('MCP_DEBUG')=='1':self.out(state())
  else:self.out({'error':'not_found'},404)
if __name__=='__main__':HTTPServer((HOST,PORT),H).serve_forever()
