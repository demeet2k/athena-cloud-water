"""Source-bound selection and malformed-input guards; no corpus writes."""
import copy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'MCP'))
from crystal_108d import metro_lines


def source():
    return json.loads((ROOT/'MCP/data/metro_lines.json').read_text(encoding='utf-8'))


class MetroInputGuards(unittest.TestCase):
    def report(self,data,selector='Gold',index=0):
        with patch.object(metro_lines,'_metro',Mock(load=Mock(return_value=data))):
            return metro_lines.query_metro_line(selector,index)

    def test_all_source_ids_codes_names_and_declared_wreath_order(self):
        data=source()
        for line in data['lines']:
            for key in ('id','code','name'):
                with self.subTest(id=line['id'],key=key):
                    report=self.report(data,line[key])
                    self.assertIn(line['description'],report)
                    self.assertEqual(report.count('### '),1)
                    self.assertIn(str(line['stations']),report)
        wreaths=[line for line in data['lines'] if line['type']=='wreath']
        for i,line in enumerate(wreaths):self.assertIn(line['description'],self.report(data,'wreath',i))
        self.assertEqual(self.report(data,'overview').count('### '),len(data['lines']))

    def test_selectors_and_indices_are_strict(self):
        data=source()
        for selector in (None,3,{},[],True,'','   '):
            self.assertTrue(self.report(data,selector).startswith('HOLD'))
        for index in (True,False,0.0,1.0,'0',None,[],{},-1):
            for selector in ('Gold','all','wreath'):
                with self.subTest(selector=selector,index=index):self.assertTrue(self.report(data,selector,index).startswith('HOLD'))
        for selector in ('Gold','S','Gold Line (Square/Earth)','all','overview','Mobius'):
            self.assertTrue(self.report(data,selector,1).startswith('HOLD'))
        for selector in ('archetype_column','Gold','S','Mobius','overview'):
            report=self.report(data,selector,1)
            self.assertTrue(report.startswith('HOLD'))
            self.assertIn(selector.title(),report)
            self.assertIn('index 1',report)
            self.assertNotIn('### ',report)
            for line in data['lines']:
                self.assertNotIn(line['description'],report)
        self.assertTrue(self.report(data,'wreath',999).startswith('HOLD'))

    def test_duplicate_and_cross_field_aliases_fail_closed(self):
        for key in ('id','code','name'):
            data=source();data['lines'][1][key]=data['lines'][0][key]
            self.assertTrue(self.report(data).startswith('HOLD'))
            self.assertTrue(self.report(data,'all').startswith('HOLD'))
        for reserved in ('all','overview','wreath'):
            data=source();data['lines'][0]['code']=reserved
            self.assertTrue(self.report(data,reserved).startswith('HOLD'))
        data=source();data['lines'][1]['name']=' gold '
        self.assertTrue(self.report(data).startswith('HOLD'))
        data=source();wreaths=[line for line in data['lines'] if line['type']=='wreath'];wreaths[1]['wreath']=wreaths[0]['wreath']
        self.assertTrue(self.report(data,'wreath').startswith('HOLD'))

    def test_malformed_source_shapes_and_census_fail_closed(self):
        for data in (None,[],7,True,{}, {'lines':None}, {'lines':[]}):
            self.assertTrue(self.report(data).startswith('HOLD'))
        for meta in (None,[],{}, {'type':'wrong'}, {'type':'metro_lines','version':'3','total_lines':True}):
            data=source();data['meta']=meta
            self.assertTrue(self.report(data).startswith('HOLD'))
        data=source();data['meta']['total_lines']+=1
        self.assertTrue(self.report(data).startswith('HOLD'))
        for key in ('id','code','name','type','description','stations'):
            data=source();del data['lines'][0][key]
            self.assertTrue(self.report(data).startswith('HOLD'))
        for value in (None,{},'1',[True],[0],[1.0],[]):
            data=source();data['lines'][0]['stations']=value
            self.assertTrue(self.report(data).startswith('HOLD'))
        data=source();data['lines'][0]=None
        self.assertTrue(self.report(data).startswith('HOLD'))
        for key in ('shell_ascent','wreath_lines','archetype_columns','qo_pillars','arcs'):
            data=source();data[key]={}
            self.assertTrue(self.report(data).startswith('HOLD'))

    def test_missing_or_invalid_source_load_returns_hold(self):
        for error in (FileNotFoundError('missing fixture'),json.JSONDecodeError('bad fixture','{',0)):
            with patch.object(metro_lines,'_metro',Mock(load=Mock(side_effect=error))):
                self.assertTrue(metro_lines.query_metro_line('Gold').startswith('HOLD'))

    def test_no_legacy_mapping_is_inferred_from_declared_lines(self):
        for name in ('shell_ascent','archetype_column','qo_pillar','arc'):
            self.assertTrue(self.report(source(),name).startswith('HOLD'))
        self.assertIn('Mobius',self.report(source(),'mobius'))
        self.assertTrue(self.report(source(),'undeclared-line').startswith('HOLD'))

    def test_valid_legacy_reads_are_preserved(self):
        legacy={'shell_ascent':{'stations':36,'law':'declared law','direction':'up','return':'Z*'},
            'wreath_lines':[{'name':'Sulfur','code':'Su','superphase':'ignition','shells':[1,2], 'function':'seed','chapter_mapping':['Ch1']}],
            'archetype_columns':[{'index':i,'name':'column'+str(i),'shells':[i],'function':'identity'} for i in range(1,13)],
            'qo_pillars':{'Q_pillar':{'name':'Q','function':'query','spans':36},'O_pillar':{'name':'O','function':'observe','spans':36},'mobius_law':'mirror'},
            'arcs':[{'alpha':0,'rho':1,'chapters':['Ch1'],'lanes':['lane']}]}
        for selector,index,expected in [('all',0,'Shell Ascent: 36'),('shell_ascent',0,'declared law'),('wreath',0,'Sulfur'),('archetype_column',12,'column12'),('qo_pillar',0,'mirror'),('arc',0,'Ch1')]:
            with self.subTest(selector=selector):self.assertIn(expected,self.report(legacy,selector,index))
        for malformed in ({'shell_ascent':None}, {'wreath_lines':[]}):
            self.assertTrue(self.report(malformed,'all').startswith('HOLD'))


if __name__=='__main__':unittest.main()
