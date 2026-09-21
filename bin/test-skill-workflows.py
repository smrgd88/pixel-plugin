#!/usr/bin/env python3
"""Execute restored skill recipes and verify their artwork, animation and exports."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('contract',ROOT/'bin/validate-mcp-contract.py')
contract=importlib.util.module_from_spec(spec);spec.loader.exec_module(contract)


def resolve(value, context):
    if isinstance(value,dict): return {k:resolve(v,context) for k,v in value.items()}
    if isinstance(value,list): return [resolve(v,context) for v in value]
    if not isinstance(value,str): return value
    def substitute(match):
        node=context
        for part in match.group(1).split('.'): node=node[part]
        if not isinstance(node,str): raise ValueError('Recipe path reference is not a string')
        return node
    return re.sub(r'\{([a-z_.]+)\}',substitute,value)


def recipes():
    for file in sorted((ROOT/'skills').glob('*/workflows.json')):
        owner=(file.parent/'SKILL.md').read_text().split('---')[1]
        allowed=set(re.findall(r'mcp__aseprite__(\w+)',owner))
        for recipe in json.loads(file.read_text()):
            for step in recipe['steps']:
                if step['name'] not in allowed: raise ValueError(f'{recipe["id"]}: tool outside owning skill allowlist: {step["name"]}')
            yield recipe


def validate_recipes(tools):
    count=0
    for recipe in recipes():
        context={'source':'/fixtures/source.aseprite','output':'/fixtures/output'}
        for step in recipe['steps']:
            arguments=resolve(step['arguments'],context)
            contract.validate_call(tools,{'name':step['name'],'arguments':arguments})
            if step.get('save'):
                # References must name actual output fields, not guessed return values.
                context[step['save']]={k:'/fixtures/result' for k,p in tools[step['name']]['outputSchema']['properties'].items() if p.get('type')=='string'}
        count+=1
    return count


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--aseprite',type=Path,required=True);parser.add_argument('--output',type=Path)
    args=parser.parse_args();aseprite=args.aseprite.resolve(strict=True)
    out=args.output.resolve() if args.output else ROOT/'test-outputs/skill-workflows'
    out.mkdir(parents=True,exist_ok=True)
    tools={t['name']:t for t in json.loads((ROOT/'config/mcp-contract.json').read_text())['tools']}
    validate_recipes(tools)
    with tempfile.TemporaryDirectory(prefix='pixel-skill-workflows-') as tmp:
        config=Path(tmp)/'config.json';config.write_text(json.dumps({'aseprite_path':str(aseprite),'temp_dir':tmp,'log_level':'error'}))
        client=contract.load_module('client','mcp-client.py').Client([str(ROOT/'bin/pixel-mcp')],dict(os.environ,PIXEL_MCP_CONFIG=str(config)))
        def call(name,arguments):
            contract.validate_call(tools,{'name':name,'arguments':arguments})
            result=client.call(name,arguments);contract.Draft202012Validator(tools[name]['outputSchema']).validate(result);return result
        def pixels(path,frame=1,layer='Layer 1',size=16):
            r=call('get_pixels',{'sprite_path':path,'layer_name':layer,'frame_number':frame,'x':0,'y':0,'width':size,'height':size})
            return {(p['x'],p['y']):p['color'].upper() for p in r['pixels']}
        def timing(path):
            sheet=out/'check-timing.png'
            r=call('export_spritesheet',{'sprite_path':path,'output_path':str(sheet),'layout':'horizontal','padding':0,'include_json':True})
            frames=json.loads(Path(r['metadata_path']).read_text())['frames'];frames=list(frames.values()) if isinstance(frames,dict) else frames
            return [f['duration'] for f in frames]
        report=[]
        try:
            contract.compare(client.tools(),list(tools.values()))
            for recipe in recipes():
                dest=out/recipe['id'];dest.mkdir(exist_ok=True)
                ctx={'output':str(dest)}
                if recipe.get('fixture'):
                    path=call('create_canvas',{'width':16,'height':16,'color_mode':'rgb'})['file_path']
                    call('draw_rectangle',{'sprite_path':path,'layer_name':'Layer 1','frame_number':1,'x':6,'y':6,'width':4,'height':4,'color':'#4477AA','filled':True})
                    for _ in range(recipe['fixture']['frames']-1):call('add_frame',{'sprite_path':path,'duration_ms':100})
                    ctx['source']=path
                for step in recipe['steps']:
                    result=call(step['name'],resolve(step['arguments'],ctx))
                    if step.get('save'):ctx[step['save']]=result
                name=recipe['id'];path=ctx.get('result',{}).get('file_path')
                if name=='heart':
                    data=pixels(path,size=8);red={xy for xy,c in data.items() if c=='#FF0000FF'}
                    assert len(red)==32 and (3,6) in red and (0,0) not in red
                    assert all((7-x,y) in red for x,y in red)
                elif name=='sword':
                    data=pixels(path);assert data[7,2]=='#FFFFFFFF' and data[5,10]=='#DDAA33FF' and data[7,12]=='#6B4423FF'
                elif name=='layered-character':
                    assert 'Character' in call('get_sprite_info',{'sprite_path':path})['layers']
                    assert pixels(path)[0,0]=='#1D2B53FF' and pixels(path,layer='Character')[6,6]=='#1A1A24FF'
                elif name=='breathing-idle':
                    assert pixels(path,2)[6,5]=='#4477AAFF' and pixels(path,2)[6,9].endswith('00')
                    assert pixels(path,1)[6,9]=='#4477AAFF' and timing(path)==[500,500]
                elif name=='attack-timing':
                    assert pixels(path,2)[12,7]=='#FFFFFFFF' and pixels(path,3).get((12,7),'#00000000').endswith('00')
                    assert timing(path)==[150,30,100]
                elif name=='steel-shading':
                    colors={c for (x,y),c in pixels(path).items() if 3<=x<13 and 3<=y<13}
                    assert len(colors)>1 and colors<=set(c+'FF' for c in ['#1A1A24','#3A3A4A','#6A6A7A','#AAAABB','#FFFFFF'])
                elif name=='manual-checker':
                    data=pixels(path);assert sum(data[x,y]=='#000000FF' for x in range(8) for y in range(8))==32
                    assert all(data[x,y]!=data[x+1,y] for x in range(7) for y in range(8))
                elif name=='scaled-animation-export':
                    assert call('get_sprite_info',{'sprite_path':ctx['source']})['width']==16
                    assert call('get_sprite_info',{'sprite_path':ctx['png']['exported_path']})['width']==32
                    assert call('get_sprite_info',{'sprite_path':ctx['gif']['exported_path']})['frame_count']==2
                    assert timing(ctx['copy']['file_path'])==[150,100]
                if path:
                    call('export_sprite',{'sprite_path':path,'output_path':str(dest/'preview.png'),'format':'png','frame_number':1})
                report.append({'recipe':name,'status':'PASS','output':str(dest)});print('PASS:',name,flush=True)
        finally:
            client.close();(out/'results.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
