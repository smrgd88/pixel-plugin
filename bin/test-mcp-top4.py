#!/usr/bin/env python3
"""Pinned bundle workflows: native identity/revisions, nested editing and protected export.

Uses real MCP/Aseprite and Pillow as an independent image decoder. No user config writes.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import uuid
from PIL import Image
from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parents[1]

def module(name,file):
 spec=importlib.util.spec_from_file_location(name,ROOT/'bin'/file)
 m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--aseprite',type=Path,required=True)
 parser.add_argument('--output',type=Path,default=ROOT/'test-outputs/top4/workflow')
 args=parser.parse_args();ase=str(args.aseprite.resolve(strict=True))
 out=args.output.resolve()/('run-'+uuid.uuid4().hex[:8]);out.mkdir(parents=True)
 config=out/'config.json';config.write_text(json.dumps({'aseprite_path':ase,'temp_dir':str(out/'sprites'),'snapshot_dir':str(out/'snapshots'),'enable_history':False,'timeout':30,'log_level':'error'}))
 env=dict(os.environ,PIXEL_MCP_CONFIG=str(config));env.pop('PIXEL_MCP_BINARY',None)
 schema={t['name']:t for t in json.loads((ROOT/'config/mcp-contract.json').read_text())['tools']}
 client=module('client','mcp-client.py').Client([str(ROOT/'bin/pixel-mcp')],env)
 calls=[];ids=set();checks=[];completed=False
 def state(path):
  p=Path(path);s=p.stat();return (p.read_bytes(),s.st_ino,s.st_mtime_ns,s.st_mode)
 def call(name,/,**arguments):
  wire=client.request('tools/call',{'name':name,'arguments':arguments});calls.append({'name':name,'arguments':arguments,'wire':wire})
  rid=wire.get('_meta',{}).get('io.github.smrgd88.pixel-mcp/request_id');assert rid and rid not in ids;uuid.UUID(rid);ids.add(rid)
  text=json.loads('\n'.join(c['text'] for c in wire['content'] if c['type']=='text'))
  if wire.get('isError'):
   assert 'structuredContent' not in wire and text['request_id']==rid
   assert text['error']==wire['_meta']['io.github.smrgd88.pixel-mcp/error']
   return wire,text
  Draft202012Validator(schema[name]['inputSchema']).validate(arguments)
  value=wire['structuredContent'];assert value==text
  Draft202012Validator(schema[name]['outputSchema']).validate(value)
  for flag in ['success','Success']:
   if flag in value:assert value[flag],value
  return wire,value
 def ok(tool,**args):
  wire,value=call(tool,**args);assert not wire.get('isError'),value;return value
 def reject(tool,code,path=None,**args):
  before=state(path) if path else None
  output_parent=Path(args['output_path']).parent if tool.startswith('export_') else None
  def output_state():
   if not output_parent.exists():return None
   return {str(x.relative_to(output_parent)):hashlib.sha256(x.read_bytes()).hexdigest() if x.is_file() else 'directory' for x in output_parent.rglob('*')}
  outputs=output_state() if output_parent else None
  wire,value=call(tool,**args);assert wire.get('isError') and value['error']['code']==code,(tool,value)
  if path:assert state(path)==before,(tool,'source changed on failure')
  if output_parent:assert output_state()==outputs,(tool,'output set changed on rejection')
 def query(path):
  q=ok('get_sprite_structure',sprite_path=path);assert q['revision']==hashlib.sha256(Path(path).read_bytes()).hexdigest();return q
 def layer(q,name):return next(x for x in q['layers'] if x['name']==name)
 def png(path):return Image.open(path).convert('RGBA')
 inspector=out/'inspect.lua'
 inspector.write_text('''local s=app.activeSprite;local o={width=s.width,height=s.height,mode=s.colorMode,data=s.data,marker=s.properties("org/top4").marker,frames={},layers={},tags={},palettes={}};local seen={}
for _,f in ipairs(s.frames) do o.frames[#o.frames+1]=math.floor(f.duration*1000+0.5) end
local function walk(ls,parent) for i,l in ipairs(ls) do local id=parent=="" and tostring(i) or parent.."/"..i;local r={id=id,name=l.name,data=l.data,visible=l.isVisible,editable=l.isEditable,cels={}}
for _,c in ipairs(l.cels) do local key=tostring(c.image.id);if not seen[key] then seen[key]=id.."@"..c.frame.frameNumber end;local a={frame=c.frame.frameNumber,x=c.position.x,y=c.position.y,opacity=c.opacity,z=c.zIndex,data=c.data,ref=seen[key],pixels={}};for p in c.image:pixels() do a.pixels[#a.pixels+1]=p() end;r.cels[#r.cels+1]=a end;o.layers[#o.layers+1]=r;if l.isGroup then walk(l.layers,id) end end end;walk(s.layers,"")
for _,t in ipairs(s.tags) do o.tags[#o.tags+1]={name=t.name,data=t.data,from=t.fromFrame.frameNumber,to=t.toFrame.frameNumber,direction=t.aniDir,repeats=t.repeats} end
for pi=1,#s.palettes do local p=s.palettes[pi];local a={};for i=0,#p-1 do local c=p:getColor(i);a[#a+1]=string.format("#%02x%02x%02x%02x",c.red,c.green,c.blue,c.alpha) end;o.palettes[#o.palettes+1]=a end;print(json.encode(o))''')
 def inspect(path):
  r=subprocess.run([ase,'--batch',str(path),'--script',str(inspector)],capture_output=True,text=True,timeout=30);assert r.returncode==0,r.stdout+r.stderr;return json.loads(r.stdout)
 def lua(path,body):
  f=out/'fixture.lua';f.write_text(body+'\napp.activeSprite:saveAs(app.activeSprite.filename)')
  r=subprocess.run([ase,'--batch',str(path),'--script',str(f)],capture_output=True,text=True,timeout=30);assert r.returncode==0,r.stdout+r.stderr
 def mark(label):checks.append(label);print('PASS:',label,flush=True)
 try:
  module('contract','validate-mcp-contract.py').compare(client.tools(),list(schema.values()))
  p=ok('create_canvas',width=16,height=16,color_mode='rgb')['file_path']
  for ms in [120,180]:ok('add_frame',sprite_path=p,duration_ms=ms)
  ok('add_layer',sprite_path=p,layer_name='Ink')
  ok('draw_pixels',sprite_path=p,layer_name='Ink',frame_number=1,pixels=[{'x':4,'y':5,'color':'#FF0000'}])
  for n in [2,3]:ok('link_cel',sprite_path=p,layer_name='Ink',source_frame=1,target_frame=n)
  q=query(p);g=ok('create_layer_group',sprite_path=p,expected_revision=q['revision'],name='Parts',parent_id='',stack_index=3)
  q=query(p);m=ok('move_layer',sprite_path=p,expected_revision=q['revision'],layer_id=layer(q,'Ink')['layer_id'],parent_id=g['layer']['layer_id'],stack_index=1)
  q=query(p);ink=layer(q,'Ink')['layer_id'];assert layer(q,'Ink')['name_path']==['Parts','Ink']
  ok('draw_pixels',sprite_path=p,layer_name='Ink',frame_number=1,pixels=[{'x':4,'y':5,'color':'#FF0000'},{'x':5,'y':5,'color':'#FF0000'}])
  lua(p,'local s=app.activeSprite;s.data="keep sprite";s.properties("org/top4").marker="KEEP";s.layers[2].layers[1].data="keep layer";s.layers[2].layers[1]:cel(1).data="keep cel"')
  native=inspect(p);q=query(p);ink=layer(q,'Ink')['layer_id'];assert layer(q,'Ink')['cels'][0]['linked_cel_count']==3
  rev=q['revision'];reject('set_cel_properties','lua_error',p,sprite_path=p,layer_id=ink,frame_number=1,expected_revision=rev,x=2)
  changed=ok('set_cel_properties',sprite_path=p,layer_id=ink,frame_number=1,expected_revision=rev,x=2,allow_linked=True)
  assert len(changed['affected_cels'])==3 and changed['warnings'][0]['code']=='linked_cel_properties'
  assert all(c['x']==2 for c in inspect(p)['layers'][2]['cels'])
  reject('set_cel_properties','file_changed',p,sprite_path=p,layer_id=ink,frame_number=1,expected_revision=rev,x=1,allow_linked=True)
  q=query(p);unlinked=ok('unlink_cel',sprite_path=p,layer_id=ink,frame_number=1,expected_revision=q['revision']);assert len(unlinked['remaining_linked_cels'])==2
  q=query(p);cs=layer(q,'Ink')['cels'];assert cs[0]['linked_cel_count']==1 and cs[1]['linked_cel_count']==2
  reject('unlink_cel','lua_error',p,sprite_path=p,layer_id=ink,frame_number=1,expected_revision=q['revision'])
  ok('set_cel_properties',sprite_path=p,layer_id=ink,frame_number=1,expected_revision=q['revision'],x=0,opacity=0)
  q=query(p);ok('set_cel_properties',sprite_path=p,layer_id=ink,frame_number=1,expected_revision=q['revision'],opacity=255)
  q=query(p);reject('set_cel_properties','lua_error',p,sprite_path=p,layer_id=ink,frame_number=1,expected_revision=q['revision'],opacity=255)
  after=inspect(p);assert after['data']==native['data'] and after['marker']=='KEEP';assert after['layers'][2]['data']=='keep layer' and after['layers'][2]['cels'][0]['data']=='keep cel'
  assert after['layers'][2]['cels'][0]['pixels']==native['layers'][2]['cels'][0]['pixels']
  mark('nested draw, native shared-set setter/warning, stale guard, unlink identity, explicit zero and metadata')
  # Requery for every mutation; lock/hidden/local/effective and source-name injection.
  q=query(p);group=layer(q,'Parts')['layer_id'];ok('set_layer_properties',sprite_path=p,layer_id=group,expected_revision=q['revision'],editable=False)
  q=query(p);reject('set_cel_properties','lua_error',p,sprite_path=p,layer_id=ink,frame_number=1,expected_revision=q['revision'],x=1)
  reject('set_layer_properties','lua_error',p,sprite_path=p,layer_id=group,expected_revision=q['revision'],editable=True,name='bad')
  ok('set_layer_properties',sprite_path=p,layer_id=group,expected_revision=q['revision'],editable=True)
  special='Ink/"雪\\\n; error("injected")'
  q=query(p);ok('set_layer_properties',sprite_path=p,layer_id=ink,expected_revision=q['revision'],name=special,visible=False,opacity=255)
  q=query(p);assert layer(q,special)['name']==special and not layer(q,special)['effective_visible']
  ok('draw_pixels',sprite_path=p,layer_name=special,frame_number=1,pixels=[{'x':4,'y':5,'color':'#FF0000'}])
  q=query(p);assert ok('get_sprite_structure',sprite_path=p,layer_offset=q['layer_count'])['layers']==[]
  mark('locked ancestor, unlock-only, hidden nested target, exact Unicode/quote/newline name and empty page')
  assert ok('get_sprite_tags',sprite_path=p)['tags']==[]
  ok('create_tag',sprite_path=p,tag_name='walk',from_frame=2,to_frame=3,direction='forward')
  tagname='walk/\"雪\\\n; metadata'
  t=ok('get_sprite_tags',sprite_path=p);tag=ok('set_tag_properties',sprite_path=p,tag_id=t['tags'][0]['tag_id'],expected_revision=t['revision'],name=tagname,direction='pingpong_reverse',repeats=0)['tag'];assert tag['repeats']==0
  reject('set_tag_properties','file_changed',p,sprite_path=p,tag_id=1,expected_revision=t['revision'],repeats=2)
  mark('empty tags and revision-guarded direction/repeats with stale tag rejection')
  # Source hidden; reveal only selected subtree in memory. Read-only export preserves all source state.
  q=query(p);ink=layer(q,special)['layer_id'];saved=state(p);native_before=inspect(p)
  reject('export_sprite','lua_error',p,sprite_path=p,output_path=str(out/'invisible.png'),format='png',frame_number=0,layer_id=ink,expected_revision=q['revision'],frame_start=2,frame_end=3)
  for opts in [dict(trim=True),dict(tag=tagname),dict(layer_id=ink,expected_revision=q['revision']),dict(frame_start=2),dict(include_hidden=True)]:
   reject('export_sprite','invalid_arguments',p,sprite_path=p,output_path=str(out/'unsupported.gif'),format='gif',frame_number=0,**opts)
  reject('export_sprite','invalid_arguments',p,sprite_path=p,output_path=str(out/'missing-revision.png'),format='png',frame_number=0,layer_id=ink)
  reject('export_sprite','invalid_arguments',p,sprite_path=p,output_path=str(out/'bad-zero.png'),format='png',frame_number=0,frame_start=0)
  exp=dict(sprite_path=p,layer_id=ink,expected_revision=q['revision'],include_hidden=True)
  seq=ok('export_sprite',**exp,output_path=str(out/'walk007.png'),format='png',frame_number=0,frame_start=2,frame_end=3,trim=True,overwrite=False)
  assert [f['frame_number'] for f in seq['files']]==[2,3]
  assert [Path(f['path']).name for f in seq['files']]==['walk007_0002.png','walk007_0003.png'];assert not (out/'walk007.png').exists()
  for f in seq['files']:
   im=png(f['path']);assert im.size==(2,1) and set(im.getdata())=={(255,0,0,255)}
  before_outputs={f['path']:Path(f['path']).read_bytes() for f in seq['files']}
  reject('export_sprite','invalid_arguments',p,**exp,output_path=str(out/'walk007.png'),format='png',frame_number=0,frame_start=2,frame_end=3,overwrite=False)
  assert all(Path(k).read_bytes()==v for k,v in before_outputs.items())
  sheet=ok('export_spritesheet',**exp,output_path=str(out/'sheet.png'),layout='horizontal',padding=3,include_json=True,tag=tagname,trim=True,extrude=True,border_padding=0,shape_padding=0,inner_padding=0,overwrite=False)
  im=png(sheet['spritesheet_path']);assert im.size==(8,3),im.size
  meta=json.loads(Path(sheet['metadata_path']).read_text());fr=meta['frames'];fr=sorted(fr.values(),key=lambda f:f['source_frame_number']) if isinstance(fr,dict) else fr
  assert [f['source_frame_number'] for f in fr]==[2,3] and [f['duration'] for f in fr]==[120,180]
  assert all(f['frame']['w']==2 and f['frame']['h']==1 and f['sourceSize']=={'w':16,'h':16} for f in fr)
  assert meta['meta']['image']=='sheet.png' and meta['meta']['frameTags'][0]['from']==0 and meta['meta']['frameTags'][0]['to']==1
  assert meta['meta']['frameTags'][0]['name']==tagname
  assert meta['meta']['frameTags'][0]['direction']=='pingpong_reverse' and set(im.getdata())=={(255,0,0,255)}
  mark('source-numbered trimmed sequence, GIF restrictions, explicit-zero padding/extrusion, source-indexed JSON and tag order')
  # Sidecar exists and participates in overwrite protection even without metadata_path.
  hidden=ok('export_spritesheet',**exp,output_path=str(out/'hidden.png'),layout='horizontal',padding=0,include_json=False)
  assert not hidden.get('metadata_path') and (out/'hidden.json').exists()
  texture=(out/'hidden.png').read_bytes();(out/'hidden.png').unlink();sidecar=(out/'hidden.json').read_bytes()
  reject('export_spritesheet','invalid_arguments',p,**exp,output_path=str(out/'hidden.png'),layout='horizontal',padding=0,include_json=False,overwrite=False)
  assert not (out/'hidden.png').exists() and (out/'hidden.json').read_bytes()==sidecar
  # Null fallback differs from explicit zero; fallback=1 on all three axes.
  ok('export_spritesheet',**exp,output_path=str(out/'fallback.png'),layout='horizontal',padding=1,include_json=True,frame_start=2,frame_end=3,border_padding=None,shape_padding=None,inner_padding=None)
  assert png(out/'fallback.png').size==(39,20),png(out/'fallback.png').size
  assert state(p)==saved and inspect(p)==native_before
  mark('include_json=false sidecar protection, null fallback and source bytes/native metadata unchanged')
  # Duplicate names cannot be selected by name for drawing/export; IDs remain usable.
  ok('add_layer',sprite_path=p,layer_name=special)
  reject('draw_pixels','lua_error',p,sprite_path=p,layer_name=special,frame_number=1,pixels=[{'x':0,'y':0,'color':'#FFFFFF'}])
  ok('create_tag',sprite_path=p,tag_name=tagname,from_frame=1,to_frame=1,direction='forward')
  reject('export_sprite','lua_error',p,sprite_path=p,output_path=str(out/'duplicate-tag.png'),format='png',frame_number=0,tag=tagname)
  empty=ok('create_canvas',width=8,height=8,color_mode='rgb')['file_path']
  ok('export_sprite',sprite_path=empty,output_path=str(out/'legacy-empty.png'),format='png',frame_number=1)
  reject('export_sprite','lua_error',empty,sprite_path=empty,output_path=str(out/'selected-empty.png'),format='png',frame_number=0,frame_start=1)
  mark('duplicate draw/tag rejection, preserved legacy empty export and selected-empty rejection')
  t=ok('get_sprite_tags',sprite_path=p);chosen=next(x for x in t['tags'] if x['from_frame']==2);old_id=chosen['tag_id']
  result=ok('set_tag_properties',sprite_path=p,tag_id=old_id,expected_revision=t['revision'],from_frame=1,to_frame=3)
  assert result['tag']['tag_id']!=old_id
  refreshed=ok('get_sprite_tags',sprite_path=p);assert refreshed['tags'][0]['from_frame']==1 and refreshed['tags'][0]['to_frame']==3
  reject('set_tag_properties','file_changed',p,sprite_path=p,tag_id=old_id,expected_revision=t['revision'],repeats=2)
  q=query(p);nested=next(l for l in q['layers'] if l['name_path']==['Parts',special])
  result=ok('unlink_cel',sprite_path=p,layer_id=nested['layer_id'],frame_number=2,expected_revision=q['revision']);assert len(result['remaining_linked_cels'])==1
  q=query(p);nested=next(l for l in q['layers'] if l['name_path']==['Parts',special]);assert all(c['linked_cel_count']==1 for c in nested['cels'])
  mark('tag range changes reorder IDs, stale old token rejects, unlink with one peer leaves all independent')
  q=query(p);duplicate=next(l for l in q['layers'] if l['name']==special and not l['parent_id'])
  ok('set_layer_properties',sprite_path=p,layer_id=duplicate['layer_id'],expected_revision=q['revision'],name='Other')
  ok('draw_pixels',sprite_path=p,layer_name=special,frame_number=3,pixels=[{'x':6,'y':5,'color':'#00FF00'}])
  t=ok('get_sprite_tags',sprite_path=p);target=next(x for x in t['tags'] if x['direction']=='pingpong_reverse')
  ok('set_tag_properties',sprite_path=p,tag_id=target['tag_id'],expected_revision=t['revision'],name='ordered')
  q=query(p);target=next(l for l in q['layers'] if l['name_path']==['Parts',special]);before=state(p)
  r=ok('export_spritesheet',sprite_path=p,output_path=str(out/'ordered.png'),layout='horizontal',padding=0,include_json=True,layer_id=target['layer_id'],expected_revision=q['revision'],include_hidden=True,tag='ordered',trim=True)
  fr=json.loads(Path(r['metadata_path']).read_text())['frames'];fr=sorted(fr.values(),key=lambda f:f['source_frame_number']) if isinstance(fr,dict) else fr
  assert [f['source_frame_number'] for f in fr]==[1,2,3] and [f['duration'] for f in fr]==[100,120,180]
  tex=png(r['spritesheet_path']);assert r['frame_count']==3 and tex.size==(6,1)
  for index,color in [(0,(255,0,0,255)),(1,(255,0,0,255)),(2,(0,255,0,255))]:
   bounds=fr[index]['frame'];assert tex.getpixel((bounds['x'],bounds['y']))==color
  assert state(p)==before
  mark('reverse/pingpong metadata does not expand or reorder exported source-frame pixels/durations')


  # Independent native background fixtures, including opaque indexed mask=3.
  for mode in ['rgb','grayscale','indexed']:
   bg=ok('create_canvas',width=16,height=16,color_mode=mode)['file_path']
   lua(bg,'''local s=app.activeSprite;app.command.BackgroundFromLayer();local bg=s.backgroundLayer;bg.name="BG";bg.data="keep background";local blue,red,green
if s.colorMode==ColorMode.INDEXED then s.transparentColor=3;local p=s.palettes[1];p:resize(4);p:setColor(3,Color(0,0,255,255));p:setColor(1,Color(255,0,0,255));p:setColor(2,Color(0,255,0,255));blue=3;red=1;green=2
elseif s.colorMode==ColorMode.GRAY then blue=app.pixelColor.graya(64,255);red=app.pixelColor.graya(192,255);green=app.pixelColor.graya(128,255)
else blue=app.pixelColor.rgba(0,0,255,255);red=app.pixelColor.rgba(255,0,0,255);green=app.pixelColor.rgba(0,255,0,255) end
bg:cel(1).image:clear(blue);for y=5,7 do for x=3,4 do bg:cel(1).image:drawPixel(x,y,red) end end;bg.isEditable=false
local l=s:newLayer();l.name="Foreground";l.isVisible=false;local im=Image(2,2,s.colorMode);im:clear(green);s:newCel(l,1,im,Point(10,11));s.data="keep background sprite"''')
   before=state(bg);native_bg=inspect(bg);q=query(bg)
   r=ok('export_spritesheet',sprite_path=bg,output_path=str(out/(mode+'-background.png')),layout='horizontal',padding=0,include_json=True,trim=True)
   im=png(r['spritesheet_path']);assert im.size==(16,16)
   for y in range(16):
    for x in range(16):
     want=((192,192,192,255) if mode=='grayscale' else (255,0,0,255)) if 3<=x<=4 and 5<=y<=7 else ((64,64,64,255) if mode=='grayscale' else (0,0,255,255))
     assert im.getpixel((x,y))==want,(mode,x,y,im.getpixel((x,y)),want)
   meta=json.loads(Path(r['metadata_path']).read_text());fr=meta['frames'];fr=sorted(fr.values(),key=lambda f:f['source_frame_number']) if isinstance(fr,dict) else fr;assert not fr[0]['trimmed']
   if mode=='indexed':assert Image.open(r['spritesheet_path']).mode in ['RGB','RGBA']
   r=ok('export_spritesheet',sprite_path=bg,output_path=str(out/(mode+'-foreground.png')),layout='horizontal',padding=0,include_json=True,trim=True,layer_id=layer(q,'Foreground')['layer_id'],expected_revision=q['revision'],include_hidden=True)
   assert png(r['spritesheet_path']).size==(2,2)
   assert state(bg)==before and inspect(bg)==native_bg
  mark('RGB/grayscale/indexed visible-background canvas and pixels, indexed RGBA texture, selected hidden foreground and byte/metadata preservation')
  # SDK mandatory-input errors retain JSON-RPC diagnostics rather than isError.
  try:
   client.request('tools/call',{'name':'set_cel_properties','arguments':{'sprite_path':p}})
   raise AssertionError('SDK accepted missing required fields')
  except Exception as error:
   assert getattr(error,'code',None)==-32602 and error.data['error']['code']=='invalid_arguments',error
   uuid.UUID(error.data['request_id']);assert error.data['request_id'] not in ids;ids.add(error.data['request_id'])
   calls.append({'name':'set_cel_properties','arguments':{'sprite_path':p},'jsonrpc_error':error.error})
  mark('new setter SDK rejection preserves JSON-RPC code and request ID')
  completed=True

 finally:
  client.close();(out/'calls.json').write_text(json.dumps(calls,indent=2)+'\n');(out/'summary.json').write_text(json.dumps({'result':'PASS' if completed else 'FAIL','checks':checks,'calls':len(calls),'request_ids':len(ids),'directory':str(out)},indent=2)+'\n');print('Evidence:',out)

if __name__=='__main__':main()
