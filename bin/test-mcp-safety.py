#!/usr/bin/env python3
"""Contract/client compatibility and optional real saved-file recovery regression."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from jsonschema import Draft202012Validator, ValidationError

ROOT = Path(__file__).resolve().parents[1]
TOOLS = {t['name']:t for t in json.loads((ROOT/'config/mcp-contract.json').read_text())['tools']}
spec = importlib.util.spec_from_file_location('client', ROOT/'bin/mcp-client.py')
module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
DRY = ['flatten_layers','quantize_palette','apply_auto_shading']

class Contracts(unittest.TestCase):
    def test_preview_and_legacy(self):
        state = dict(width=8,height=8,color_mode='rgb',frame_count=1,layer_count=1,palette_size=2)
        legacy = {'flatten_layers':{'success':True},'quantize_palette':dict(success=True,original_colors=3,quantized_colors=2,color_mode='rgb',palette=['#000000','#FFFFFF'],algorithm_used='kmeans'),'apply_auto_shading':dict(success=True,colors_added=2,palette=['#000000','#FFFFFF'],regions_shaded=1)}
        c = module.Client.__new__(module.Client)
        for name in DRY:
            self.assertNotIn('dry_run',TOOLS[name]['inputSchema']['required'])
            for value in [True,False]: Draft202012Validator(TOOLS[name]['inputSchema']['properties']['dry_run']).validate(value)
            with self.assertRaises(ValidationError): Draft202012Validator(TOOLS[name]['inputSchema']['properties']['dry_run']).validate(None)
            preview = dict(legacy[name],dry_run=True,preview=dict(before=state,after=state,would_change_file=False))
            for response in [legacy[name],preview]:
                Draft202012Validator(TOOLS[name]['outputSchema']).validate(response)
                for structured in [False,True]:
                    wire={'content':[{'type':'text','text':json.dumps(response)}]}
                    if structured:wire['structuredContent']=response
                    with patch.object(c,'request',return_value=wire) as request:
                        self.assertEqual(c.call(name,{}),response);request.assert_called_once()
        self.assertNotIn('dry_run',TOOLS['scale_sprite']['inputSchema']['properties'])
        with patch.object(c,'request',return_value={'isError':True,'structuredContent':preview}):
            with self.assertRaises(RuntimeError):c.call('flatten_layers',{})
    def test_recovery_required_fields(self):
        for name in ['restore_snapshot','undo_last_operation']:
            with self.assertRaises(ValidationError):Draft202012Validator(TOOLS[name]['inputSchema']).validate({'sprite_path':'/sprite.aseprite'})
        Draft202012Validator(TOOLS['list_operation_history']['outputSchema']).validate({'operations':[],'recording_enabled':False})
        Draft202012Validator(TOOLS['list_snapshots']['outputSchema']).validate({'snapshots':[]})

def live(aseprite,output):
    with tempfile.TemporaryDirectory(prefix='pixel-safety-') as temp:
        out=output.resolve() if output else Path(temp)/'out';out.mkdir(parents=True,exist_ok=True)
        config=Path(temp)/'config.json';calls=[];c=None
        def connect(enabled):
            nonlocal c
            if c:c.close()
            config.write_text(json.dumps(dict(aseprite_path=str(aseprite.resolve(strict=True)),temp_dir=str(out/'sprites'),snapshot_dir=str(out/'store'),enable_history=enabled,log_level='error')))
            env=dict(os.environ,PIXEL_MCP_CONFIG=str(config));env.pop('PIXEL_MCP_BINARY',None)
            c=module.Client([str(ROOT/'bin/pixel-mcp')],env)
        def call(name,**args):
            Draft202012Validator(TOOLS[name]['inputSchema']).validate(args)
            wire=c.request('tools/call',{'name':name,'arguments':args});assert not wire.get('isError'),wire
            value=wire['structuredContent'];assert value==json.loads('\n'.join(x['text'] for x in wire['content'] if x['type']=='text'))
            Draft202012Validator(TOOLS[name]['outputSchema']).validate(value);calls.append(dict(name=name,arguments=args,result=value));return value
        def unchanged(path):
            p=Path(path);s=p.stat();return (p.read_bytes(),s.st_ino,s.st_mode,s.st_mtime_ns)
        def reject(name,path,**args):
            before=unchanged(path)
            try:wire=c.request('tools/call',{'name':name,'arguments':args})
            except RuntimeError as e:
                assert "'code': -32602" in str(e);wire={'invalid_params':str(e)}
            else:assert wire.get('isError'),wire
            calls.append(dict(name=name,arguments=args,error=wire));assert unchanged(path)==before
        def fixture():
            p=call('create_canvas',width=8,height=8,color_mode='rgb')['file_path']
            call('draw_pixels',sprite_path=p,layer_name='Layer 1',frame_number=1,pixels=[dict(x=x,y=y,color=['#FF0000','#00FF00','#0000FF'][x%3]) for y in range(8) for x in range(8)])
            call('add_layer',sprite_path=p,layer_name='Extra');return p
        try:
            connect(False);assert c.tools()==sorted(TOOLS.values(),key=lambda t:t['name'])
            for name,args in [('flatten_layers',{}),('quantize_palette',dict(target_colors=2,algorithm='kmeans',dither=True)),('apply_auto_shading',dict(layer_name='Layer 1',frame_number=1,light_direction='top_left',intensity=.6,style='cell',hue_shift=True))]:
                p=fixture();before=unchanged(p)
                a=call(name,sprite_path=p,dry_run=True,**args);b=call(name,sprite_path=p,dry_run=True,**args)
                assert a==b and a['dry_run'] and unchanged(p)==before
                assert a['preview']['would_change_file']
                if name!='apply_auto_shading':assert a['warnings']
                reject('scale_sprite',p,sprite_path=p,scale_x=2,scale_y=2,algorithm='nearest',dry_run=True)
                actual=call(name,sprite_path=p,**args)
                assert 'dry_run' not in actual and 'preview' not in actual
                assert {k:v for k,v in a.items() if k not in ['dry_run','preview']}==actual
                info=call('get_sprite_info',sprite_path=p);after=a['preview']['after']
                for k in ['width','height','color_mode','frame_count','layer_count']:assert info[k]==after[k]
                assert not call('list_operation_history',sprite_path=p)['operations']
            print('PASS: 3 repeated previews preserve bytes/inode/mode/mtime, match real apply and retain warnings; unsupported dry_run rejected',flush=True)
            p=fixture();original=Path(p).read_bytes();snap=call('create_snapshot',sprite_path=p,label='baseline')['snapshot'];sid=snap['snapshot_id']
            call('flatten_layers',sprite_path=p);edited=Path(p).read_bytes();assert edited!=original
            connect(False);assert sid in [x['snapshot_id'] for x in call('list_snapshots',sprite_path=p)['snapshots']]
            other=fixture();reject('restore_snapshot',other,sprite_path=other,snapshot_id=sid)
            restored=call('restore_snapshot',sprite_path=p,snapshot_id=sid);assert Path(p).read_bytes()==original
            assert call('get_sprite_info',sprite_path=p)['layer_count']==2
            call('restore_snapshot',sprite_path=p,snapshot_id=restored['backup_snapshot']['snapshot_id']);assert Path(p).read_bytes()==edited
            call('delete_snapshot',snapshot_id=sid);reject('restore_snapshot',p,sprite_path=p,snapshot_id=sid)
            print('PASS: snapshot restart discovery, byte-exact restore/pre-restore backup, source mismatch and deleted-ID rejection',flush=True)
            p=fixture();original=Path(p).read_bytes();connect(True)
            assert call('list_operation_history',sprite_path=p)==dict(operations=[],recording_enabled=True)
            call('flatten_layers',sprite_path=p,dry_run=True);assert not call('list_operation_history',sprite_path=p)['operations']
            reject('quantize_palette',p,sprite_path=p,target_colors=1,algorithm='kmeans',dither=False)
            assert not call('list_operation_history',sprite_path=p)['operations']
            call('flatten_layers',sprite_path=p);after1=Path(p).read_bytes()
            layer=call('get_sprite_info',sprite_path=p)['layers'][0]
            first=call('list_operation_history',sprite_path=p)['operations'][0]
            call('draw_pixels',sprite_path=p,layer_name=layer,frame_number=1,pixels=[dict(x=0,y=0,color='#FFFFFF')]);after2=Path(p).read_bytes()
            entries=call('list_operation_history',sprite_path=p)['operations'];assert len(entries)==2 and entries[0]['sequence']>entries[1]['sequence'];second=entries[0]
            reject('undo_last_operation',p,sprite_path=p,expected_operation_id=first['operation_id'])
            # Export/read/manual snapshot do not become edits.
            call('export_sprite',sprite_path=p,output_path=str(out/'history.png'),format='png',frame_number=1)
            call('create_snapshot',sprite_path=p,label='manual');assert len(call('list_operation_history',sprite_path=p)['operations'])==2
            connect(False);assert not call('list_operation_history',sprite_path=p)['recording_enabled']
            undone=call('undo_last_operation',sprite_path=p,expected_operation_id=second['operation_id']);assert undone['operation']['state']=='undone' and Path(p).read_bytes()==after1
            reject('undo_last_operation',p,sprite_path=p,expected_operation_id=second['operation_id'])
            call('undo_last_operation',sprite_path=p,expected_operation_id=first['operation_id']);assert Path(p).read_bytes()==original
            assert call('get_sprite_info',sprite_path=p)['layer_count']==2
            # A non-recording edit is an external change relative to a recorded after hash.
            connect(True);call('flatten_layers',sprite_path=p);entry=call('list_operation_history',sprite_path=p)['operations'][0]
            connect(False);call('draw_pixels',sprite_path=p,layer_name=call('get_sprite_info',sprite_path=p)['layers'][0],frame_number=1,pixels=[dict(x=0,y=0,color='#123456')])
            reject('undo_last_operation',p,sprite_path=p,expected_operation_id=entry['operation_id'])
            print('PASS: opt-in recording, exclusions, reverse two-edit undo after restart/disable, stale/retry/external-change guards',flush=True)
        finally:
            if c:c.close()
            (out/'calls.json').write_text(json.dumps(calls,indent=2))
        print(f'PASS: {len(calls)} calls ({sum("error" in x for x in calls)} expected rejections)',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--aseprite',type=Path);p.add_argument('--output',type=Path);a=p.parse_args()
    t=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Contracts))
    if not t.wasSuccessful():raise SystemExit(1)
    if a.aseprite:live(a.aseprite,a.output)
