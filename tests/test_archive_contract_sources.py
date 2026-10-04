"""Explicit pin-bound descriptive archive views; no silent merge or execution proof."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock
from unittest.mock import patch
import zlib

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'MCP'))
from crystal_108d import registry_sources as sources, live_cell, hologram_reading as holo, inverse_seed as seed, inverse_octave as octave, inverse_complete as complete
from crystal_108d.qshrink_codec import QShrinkContainer

QUERIES=[(live_cell.query_live_cell,'live_cell_constitution.json','schemas','BoardStateRow'),
 (holo.query_hologram,'hologram_reading.json','faces','Perception'),
 (holo.query_hologram_rosetta,'hologram_rosetta.json','quaternary','Egypt'),
 (seed.query_4d_seed,'inverse_crystal_seed.json','cells','256'),
 (seed.query_3d_crystal,'inverse_crystal_seed.json','components','14'),
 (octave.query_octave_stage,'inverse_crystal_octave.json','S03','S03'),
 (octave.query_crown_transform,'inverse_crystal_octave.json','1','ZeroTunnel'),
 (complete.query_projection_stack,'inverse_crystal_complete.json','up','108'),
 (complete.query_weave_operator,'inverse_crystal_complete.json','W3','Su')]


class ArchiveContractTests(unittest.TestCase):
 def test_all_six_pinned_archives_verify_exact_source_identity(self):
  for filename,pin in sources.ARCHIVES.items():
   data,provenance=sources.load_archive(filename)
   self.assertEqual(data['meta']['title'],pin['title'])
   self.assertEqual(set(data),set(pin['roots']))
   self.assertIn(pin['sha256'],provenance); self.assertIn(pin['blob'],provenance)
   self.assertIn(sources.PINNED_COMMIT,provenance); self.assertIn(sources.PINNED_REPOSITORY,provenance)

 def test_nine_existing_descriptive_routes_require_explicit_archive(self):
  for query,filename,selector,expected in QUERIES:
   report=query('archive:'+selector)
   self.assertIn(expected,report,query.__name__)
   self.assertIn(sources.ARCHIVES[filename]['sha256'],report)
   self.assertIn('explicit archive',report)
   self.assertIn('No runtime certificate is issued',report)
   current=query(selector)
   self.assertNotIn('**Archive SHA256**',current)
   self.assertIn('HOLD',current)

 def test_missing_current_family_marker_never_selects_unknown_legacy_namespace(self):
  data,_=sources.load_archive('hologram_reading.json')
  data['meta']['title']='unknown namespace'
  with patch.object(holo,'_HOLOGRAM',Mock(load=Mock(return_value=data))):
   self.assertTrue(holo.query_hologram('all').startswith('HOLD:'))
  data,_=sources.load_archive('live_cell_constitution.json')
  data['meta']['title']='unknown namespace'
  with patch.object(live_cell,'_CELL',Mock(load=Mock(return_value=data))):
   self.assertTrue(live_cell.query_live_cell('schema:BoardStateRow').startswith('HOLD:'))

 def test_partial_or_malformed_untyped_legacy_live_source_holds(self):
  incomplete={'meta':{'title':sources.ARCHIVES['live_cell_constitution.json']['title']},'cell_schema':{}}
  with patch.object(live_cell,'_CELL',Mock(load=Mock(return_value=incomplete))):
   self.assertTrue(live_cell.query_live_cell('all').startswith('HOLD:'))
   self.assertTrue(live_cell.live_cell_status().startswith('HOLD:'))
  data,_=sources.load_archive('live_cell_constitution.json')
  data['metro_map']=None
  with patch.object(live_cell,'_CELL',Mock(load=Mock(return_value=data))):
   self.assertTrue(live_cell.query_live_cell('all').startswith('HOLD:'))
   self.assertTrue(live_cell.live_cell_status().startswith('HOLD:'))

 def test_current_catalogs_preserve_empty_measured_artifact_maps(self):
  for query in [holo.query_hologram,holo.query_hologram_rosetta,seed.query_4d_seed,seed.query_3d_crystal,
                octave.query_octave_stage,octave.query_crown_transform,complete.query_projection_stack,complete.query_weave_operator]:
   report=query('all')
   self.assertIn('current JSON',report)
   self.assertIn('Catalog Snapshot SHA256',report)
   self.assertIn('HOLD',report)
   self.assertNotIn('**Archive SHA256**',report)
  self.assertIn('**seeds**: {}',seed.query_4d_seed('all'))
  self.assertIn('**completions**: {}',complete.query_projection_stack('all'))
  self.assertIn('**readings**: {}',holo.query_hologram('all'))

 def test_missing_json_never_selects_existing_archive_implicitly(self):
  with tempfile.TemporaryDirectory() as directory:
   temp=Path(directory); blob=(ROOT/'MCP/data/hologram_reading.qshr').read_bytes()
   (temp/'hologram_reading.qshr').write_bytes(blob)
   with patch.object(sources,'DATA_DIR',temp):
    self.assertIn('archive selection must be explicit',holo.query_hologram('all'))
    self.assertIn('**Archive SHA256**',holo.query_hologram('archive:all'))

 def test_missing_changed_oversized_archives_hold_without_json_fallback(self):
  with tempfile.TemporaryDirectory() as directory:
   temp=Path(directory); target=temp/'hologram_reading.qshr'
   with patch.object(sources,'DATA_DIR',temp):
    self.assertTrue(holo.query_hologram('archive:all').startswith('HOLD:'))
    for blob in [b'QSHR',b'x'*(sources.MAX_ARCHIVE_BYTES+1), (ROOT/'MCP/data/hologram_reading.qshr').read_bytes()+b'trailing']:
     target.write_bytes(blob)
     self.assertTrue(holo.query_hologram('archive:all').startswith('HOLD:'))

 def test_decoder_independent_checks_reject_corrupt_chunks_and_expansion_bombs(self):
  original=(ROOT/'MCP/data/hologram_reading.qshr').read_bytes()
  with tempfile.TemporaryDirectory() as directory:
   temp=Path(directory)
   for kind in ['crc','bomb','wrongidentity','badcolumns','foreigncolumnfield']:
    container=QShrinkContainer.deserialize(original);chunk=container.domains[0].chunks[0]
    if kind=='crc': chunk.payload=bytes([chunk.payload[0]^1])+chunk.payload[1:]
    else:
     raw=b'x'*(sources.MAX_DECODED_BYTES+1) if kind=='bomb' else json.dumps({'meta':{'title':'wrong'}}).encode() if kind=='wrongidentity' else json.dumps({'__cols__':True,'keys':['a'],'rows':[[1]],'foreign':'must-not-disappear'}).encode() if kind=='foreigncolumnfield' else json.dumps({'__cols__':True,'keys':['a','a'],'rows':[[1,2]]}).encode()
     chunk.payload=zlib.compress(raw);chunk.header.payload_length=len(chunk.payload);chunk.header.checksum=zlib.crc32(chunk.payload)&0xffffffff
    blob=container.serialize();(temp/'hologram_reading.qshr').write_bytes(blob)
    pin=dict(sources.ARCHIVES['hologram_reading.json'],sha256=hashlib.sha256(blob).hexdigest())
    with patch.object(sources,'DATA_DIR',temp),patch.dict(sources.ARCHIVES,{'hologram_reading.json':pin}):
     self.assertTrue(holo.query_hologram('archive:all').startswith('HOLD:'),kind)

 def test_ambiguous_partial_dimension_and_crown_names_never_pick_first_route(self):
  self.assertIn('not found',octave.query_octave_stage('archive:D'))
  self.assertIn('not found',octave.query_crown_transform('archive:weave'))
  self.assertIn('not found',live_cell.query_live_cell('archive:schema:Board'))
  self.assertIn('not found',live_cell.query_live_cell('archive:schema:'))
  self.assertIn('S03',octave.query_octave_stage('archive:6D'))

 def test_invalid_source_selectors_and_unsupported_arbitrary_paths(self):
  for query,_,_,_ in QUERIES:
   for selector in [None,[],True,'','archive:','archive:archive:all']:
    self.assertIn('Invalid',query(selector))
  self.assertTrue(holo.query_hologram('archive:../../other').startswith('Unknown'))

 def test_cold_archive_read_imports_no_numpy_training_pipeline_or_server(self):
  program="""import builtins,sys
sys.path.insert(0,'MCP')
original=builtins.__import__
def guarded(name,*args,**kwargs):
 if name.startswith(('numpy','crystal_108d.qshrink_pipeline','mcp','athena_mcp_server')): raise AssertionError(name)
 return original(name,*args,**kwargs)
builtins.__import__=guarded
from crystal_108d.hologram_reading import query_hologram
assert '**Archive SHA256**' in query_hologram('archive:all')
assert 'crystal_108d.qshrink_pipeline' not in sys.modules
"""
  result=subprocess.run([sys.executable,'-c',program],cwd=ROOT,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'),capture_output=True,text=True,timeout=20)
  self.assertEqual(result.returncode,0,result.stderr)


if __name__=='__main__':unittest.main()
