import copy, importlib.util, json, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'mission_control'/'mycelium'/'five_axis'
spec=importlib.util.spec_from_file_location('growth',P/'five_axis.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
class FiveAxisTests(unittest.TestCase):
 def setUp(self): self.d=json.loads((P/'W0_FIELD_OBSERVATIONS.json').read_text())
 def test_graph(self):
  self.assertEqual((len(self.d['nodes']),len(self.d['edges'])),(21,22));mod.validate(self.d)
 def test_axes(self): self.assertEqual([x['id'] for x in self.d['axes']],list(mod.AXES))
 def test_unknown(self): self.assertIsNone(mod.project(self.d)['axes'][0]['percent'])
 def test_pressure(self): self.assertGreater(mod.exposure(self.d,'issue:ab1860')['downstream_unique_nodes'],0)
 def test_cycle(self):
  d=copy.deepcopy(self.d);d['edges'].append({'from':'gate:ab_admission','to':'issue:ab1860','kind':'REQUIRES','source_ref':'https://github.com/GBOGEB/ABACUS/issues/1860','evidence_level':'DECLARED_DEPENDENCY'})
  with self.assertRaisesRegex(ValueError,'EXECUTABLE_DAG_CYCLE'):mod.validate(d)
 def test_denominator(self):
  d=copy.deepcopy(self.d);d['axes'][0]['primary']['numerator']=0
  with self.assertRaisesRegex(ValueError,'PARTIAL_DENOMINATOR'):mod.validate(d)
 def test_false_success(self):
  d=copy.deepcopy(self.d);d['axes'][1]['signals'][1]['numerator']=5
  with self.assertRaisesRegex(ValueError,'FORGED_OR_INVALID_DENOMINATOR'):mod.validate(d)
 def test_authority(self):
  d=copy.deepcopy(self.d);d['authority']['merge_admission']='PASS'
  with self.assertRaisesRegex(ValueError,'UNAUTHORIZED_PROMOTION'):mod.validate(d)
 def test_missing_origin(self):
  d=copy.deepcopy(self.d);d['edges']=[e for e in d['edges'] if e['to']!='finding:w12_skipped_marker']
  with self.assertRaisesRegex(ValueError,'FINDING_WITHOUT_SOURCE_ORIGIN'):mod.validate(d)
 def test_dangling(self):
  d=copy.deepcopy(self.d);d['edges'][0]['to']='invalid'
  with self.assertRaisesRegex(ValueError,'DANGLING_OR_SELF_EDGE'):mod.validate(d)
 def test_digest(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t);mod.write_bundle(self.d,p,candidate_head='c'*40,run_id=42,attempt=1);mod.verify_bundle(p,'c'*40)
   (p/'FIVE_AXIS_SIPOC.json').write_text('{}')
   with self.assertRaisesRegex(ValueError,'HASH_DRIFT'):mod.verify_bundle(p,'c'*40)
 def test_replay(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t);mod.write_bundle(self.d,p,candidate_head='c'*40)
   with self.assertRaisesRegex(ValueError,'RECEIPT_IDENTITY_OR_AUTHORITY'):mod.verify_bundle(p,'d'*40)
if __name__=='__main__':unittest.main()
