"""Explicit descriptive archive routes remain distinct from canonical JSON and proof."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'MCP'))
from crystal_108d import registry_sources as sources, overlays, mobius_lenses as mobius, angel, angel_geometry as geometry

FAMILIES=('overlay_registries','mobius_lenses','angel_object','angel_geometry','angel_conservation')
QUERIES=((overlays.query_overlay,'overlay_registries','all','Four Lens Registry'),
 (mobius.query_mobius_lens,'mobius_lenses','kernel','Carrier'),
 (mobius.query_sfcr_station,'mobius_lenses','SFCR','Complete local aether'),
 (angel.query_angel,'angel_object','all','Canonical Object'),
 (geometry.query_angel_geometry,'angel_geometry','metric','Metric'),
 (geometry.query_angel_conservation,'angel_conservation','exact','Normalization'))

class ExtendedArchiveTests(unittest.TestCase):
 def test_all_thirteen_additional_pins_bind_exact_bytes_metadata_and_roots(self):
  self.assertEqual(len(sources.ADDITIONAL_ARCHIVES),13)
  for filename,pin in sources.ADDITIONAL_ARCHIVES.items():
   with self.subTest(filename=filename):
    blob=(ROOT/'MCP/data'/filename.replace('.json','.qshr')).read_bytes()
    self.assertEqual(hashlib.sha256(blob).hexdigest(),pin['sha256'])
    self.assertEqual(hashlib.sha1(b'blob '+str(len(blob)).encode()+b'\0'+blob).hexdigest(),pin['blob'])
    data,provenance=sources.load_archive(filename)
    self.assertEqual(data['meta'],pin['metadata']);self.assertEqual(set(data),set(pin['roots']))
    for identity in (pin['sha256'],pin['blob'],sources.PINNED_REPOSITORY,sources.PINNED_COMMIT):self.assertIn(identity,provenance)

 def test_six_routes_and_integer_sigma_read_only_explicit_pinned_archives(self):
  for query,family,component,expected in QUERIES:
   report=query('archive:'+component)
   self.assertIn(expected,report,query.__name__)
   self.assertIn(sources.ADDITIONAL_ARCHIVES[family+'.json']['sha256'],report)
   self.assertIn('No runtime certificate is issued',report)
   current=query(component)
   self.assertIn('HOLD',current);self.assertNotIn('**Archive SHA256**',current)
  report=overlays.query_sigma15(15,source='archive')
  self.assertIn('Mask**: 15 (binary: 1111)',report)
  self.assertIn('No runtime certificate is issued',report)
  self.assertNotIn('**Archive SHA256**',overlays.query_sigma15(15))

 def test_current_catalogs_report_every_actual_source_record_without_archive(self):
  routes=((overlays.query_overlay,'overlay_registries','overlays',8),
          (mobius.query_mobius_lens,'mobius_lenses','pairs',18),
          (angel.query_angel,'angel_object','pieces',12),
          (geometry.query_angel_geometry,'angel_geometry','element_groupings',4),
          (geometry.query_angel_conservation,'angel_conservation','conservation_rules',4))
  for query,family,field,count in routes:
   data=json.loads((ROOT/'MCP/data'/f'{family}.json').read_text(encoding='utf-8'))
   self.assertEqual(len(data[field]),count)
   report=query('all')
   self.assertIn(json.dumps(data[field],ensure_ascii=False,sort_keys=True),report)
   self.assertIn('current JSON',report);self.assertIn('HOLD',report)
   self.assertNotIn('**Archive SHA256**',report)
  self.assertIn('Current Source Catalog',geometry.angel_geometry_status())
  self.assertNotIn('**State Manifold**: 6 charts',geometry.angel_geometry_status())

 def test_overlay_index_rejects_boolean_negative_and_conflicting_overview(self):
  for index in (True,-1,1.0,'1',None):self.assertIn('Invalid',overlays.query_overlay('archive:lens',index))
  self.assertIn('requires a specific',overlays.query_overlay('archive:all',1))
  self.assertIn('Index 5 out of range',overlays.query_overlay('archive:lens',5))
  self.assertIn('Entry 2',overlays.query_overlay('archive:lens',2))
  self.assertIn('Flower',overlays.query_overlay('archive:lens',2))
  self.assertIn('no legacy registry-entry',overlays.query_overlay('all',1))

 def test_sigma_typed_source_and_all_fifteen_exact_masks(self):
  for sigma in (True,0,16,-1,1.0,'1',None):self.assertIn('Invalid',overlays.query_sigma15(sigma,'archive'))
  for source in (None,True,[],{},'archive:all','ARCHIVE'):self.assertIn('Invalid',overlays.query_sigma15(1,source))
  for mask in range(1,16):
   report=overlays.query_sigma15(mask,'archive');self.assertIn(f'Mask**: {mask} (binary: {mask:04b})',report)

 def test_dimension_filters_never_fall_back_or_get_ignored(self):
  for dim in (True,-1,1.0,'6',None):self.assertIn('Invalid',mobius.query_mobius_lens('archive:square',dim))
  self.assertIn('no source lens mapping',mobius.query_mobius_lens('archive:square',999))
  self.assertIn('does not support',mobius.query_mobius_lens('archive:kernel',6))
  self.assertIn('HOLD',mobius.query_mobius_lens('all',6))
  self.assertIn('Unknown lens selector',mobius.query_mobius_lens('archive:typo',6))
  for dim in (4,6,8,10,12):
   self.assertIn(f'Lens at {dim}D',mobius.query_mobius_lens('archive:square',dim))
   self.assertIn(f'All Lenses at {dim}D',mobius.query_mobius_lens('archive:all',dim))

 def test_station_masks_are_bounded_exact_and_codes_not_substrings(self):
  report=mobius.query_sfcr_station('archive:'+'0'*5000+'15')
  self.assertIn('Station [15]: SFCR',report)
  for station in ('0','16','9'*5000):self.assertIn('Invalid station mask',mobius.query_sfcr_station('archive:'+station))
  self.assertIn('not found',mobius.query_sfcr_station('archive:SFCR-extra').lower())
  for mask in range(1,16):self.assertIn(f'Station [{mask}]',mobius.query_sfcr_station('archive:'+str(mask)))

 def test_corrupt_or_missing_new_archive_never_falls_back_to_current_json(self):
  with tempfile.TemporaryDirectory() as directory:
   temp=Path(directory)
   with patch.object(sources,'DATA_DIR',temp):
    for query,_,component,_ in QUERIES:self.assertTrue(query('archive:'+component).startswith('HOLD:'))
    for family in FAMILIES:
     (temp/(family+'.qshr')).write_bytes(b'QSHR-invalid')
    for query,_,component,_ in QUERIES:self.assertTrue(query('archive:'+component).startswith('HOLD:'))

 def test_current_nested_source_conflicts_hold_and_do_not_mutate_shared_records(self):
  cases=((overlays,'_overlays','overlay_registries',overlays.query_overlay,'overlays'),
         (mobius,'_mobius','mobius_lenses',mobius.query_mobius_lens,'pairs'),
         (angel,'_angel','angel_object',angel.query_angel,'pieces'),
         (geometry,'_CONSERVATION','angel_conservation',geometry.query_angel_conservation,'conservation_rules'))
  for module,cache,family,query,field in cases:
   original=json.loads((ROOT/'MCP/data'/f'{family}.json').read_text(encoding='utf-8'))
   before=copy.deepcopy(original)
   with patch.object(module,cache,Mock(load=Mock(return_value=original))):self.assertIn('current JSON',query('all'))
   self.assertEqual(original,before)
   for value in (None,{},[None],[{}]):
    data=copy.deepcopy(original);data[field]=value
    with patch.object(module,cache,Mock(load=Mock(return_value=data))):self.assertTrue(query('all').startswith('HOLD:'))
  data=json.loads((ROOT/'MCP/data/angel_object.json').read_text(encoding='utf-8'));data['formal_self_model']['pieces']=11
  with patch.object(angel,'_angel',Mock(load=Mock(return_value=data))):self.assertTrue(angel.query_angel('all').startswith('HOLD:'))
  data=json.loads((ROOT/'MCP/data/angel_geometry.json').read_text(encoding='utf-8'));data['element_groupings']['S']=None
  with patch.object(geometry,'_GEOMETRY',Mock(load=Mock(return_value=data))):self.assertTrue(geometry.query_angel_geometry('all').startswith('HOLD:'))

 def test_angel_exact_pieces_modes_and_actual_dynamics_field(self):
  data,_=sources.load_archive('angel_object.json')
  for piece in data['structural_pieces']:
   report=angel.query_angel('archive:piece_'+str(piece['index']))
   self.assertIn(piece['name'],report);self.assertIn(piece['definition'],report)
  for selector in ('piecepiece1','piece_1_extra','piece_-1','piece_0','piece_13'):
   self.assertIn('Invalid piece selector',angel.query_angel('archive:'+selector))
  self.assertIn('Piece 1:',angel.query_angel('archive:piece_'+'0'*5000+'1'))
  modes=angel.query_angel('archive:modes')
  for mode in data['fixed_points_and_attractors']['operational_modes']:self.assertIn(mode,modes)
  report=angel.query_angel('archive:dynamics');self.assertIn('state_evolution_dynamics',report)
  for law in data['state_evolution_dynamics'].values():self.assertIn(json.dumps(law,ensure_ascii=False,sort_keys=True),report)
  self.assertIn('No runtime certificate is issued',report)

 def test_untyped_archived_overlay_identity_uses_real_metadata_not_invented_title(self):
  data,_=sources.load_archive('overlay_registries.json')
  self.assertNotIn('title',data['meta'])
  with patch.object(overlays,'_overlays',Mock(load=Mock(return_value=data))):self.assertIn('Four Lens Registry',overlays.query_overlay('all'))
  data['meta']['total_registries']=99
  with patch.object(overlays,'_overlays',Mock(load=Mock(return_value=data))):self.assertTrue(overlays.query_overlay('all').startswith('HOLD:'))

if __name__=='__main__':unittest.main()
