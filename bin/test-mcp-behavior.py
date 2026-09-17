#!/usr/bin/env python3
"""Actual MCP tool sweep; persistent artifacts, independent read-only Aseprite inspection."""
import argparse,importlib.util,json,os,subprocess,traceback,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--aseprite',type=Path,required=True);parser.add_argument('--output',type=Path,default=ROOT/'test-outputs/mcp-behavior');args=parser.parse_args()
OUT=args.output.resolve();OUT.mkdir(parents=True,exist_ok=True)
RUN=OUT/('run-'+uuid.uuid4().hex[:8]);RUN.mkdir()
ASE=str(args.aseprite.resolve(strict=True))
def module(n,p):
 spec=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
clientmod=module('client',ROOT/'bin/mcp-client.py')
from jsonschema import Draft202012Validator
config=RUN/'config.json';config.write_text(json.dumps({'aseprite_path':ASE,'temp_dir':str(RUN/'sprites'),'log_level':'error'}))
env=dict(os.environ,PIXEL_MCP_CONFIG=str(config))
version=subprocess.check_output([str(ROOT/'bin/pixel-mcp'),'--version'],env=env,text=True).strip()

(RUN/'version.txt').write_text(version+'\n')
c=clientmod.Client([str(ROOT/'bin/pixel-mcp')],env)
tools={t['name']:t for t in c.tools()};results=[];calls=[];focus=''
def call(name,**a):
 Draft202012Validator(tools[name]['inputSchema']).validate(a)
 row={'case':focus,'name':name,'arguments':a};calls.append(row)
 try:
  r=c.call(name,a);row['result']=r
  Draft202012Validator(tools[name]['outputSchema']).validate(r)
  for flag in ['success','Success']:
   if flag in r:assert r[flag],r
  return r
 except Exception as e:row['error']=str(e);raise
 finally:(RUN/'calls.json').write_text(json.dumps(calls,indent=2))
def inspect(p):
 r=subprocess.run([ASE,'--batch',p,'--script',str(ROOT/'bin/inspect-sprite.lua')],text=True,capture_output=True,timeout=30)
 assert r.returncode==0,r.stderr+r.stdout
 return json.loads(r.stdout.strip())
def px(p,l='Layer 1',frame=1):
 s=inspect(p)
 for layer in s['layers']:
  if layer['name']==l:
   for cel in layer['cels']:
    if cel['frame']==frame:return cel['pixels'] if isinstance(cel['pixels'],dict) else {}
 return {}
def sprite(mode='rgb',w=16,h=16):return call('create_canvas',width=w,height=h,color_mode=mode)['file_path']
def draw(p,x=2,y=3,color='#FF0000',layer='Layer 1',frame=1):return call('draw_pixels',sprite_path=p,layer_name=layer,frame_number=frame,pixels=[{'x':x,'y':y,'color':color}])
def rect(p,color='#AA6644',x=0,y=0,w=16,h=16):return call('draw_rectangle',sprite_path=p,layer_name='Layer 1',frame_number=1,x=x,y=y,width=w,height=h,color=color,filled=True)
def case(name,fn,variant='basic'):
 global focus
 focus=name+':'+variant
 try:
  detail=fn();results.append({'tool':name,'variant':variant,'status':'PASS','detail':detail or 'persistent output verified'});print('PASS',focus,flush=True)
 except Exception as e:
  results.append({'tool':name,'variant':variant,'status':'FAIL','error':str(e),'traceback':traceback.format_exc()});print('FAIL',focus,str(e)[:250],flush=True)
 (RUN/'results.json').write_text(json.dumps(results,indent=2))
def basic(name):
 p=sprite();s={'sprite_path':p};d={**s,'layer_name':'Layer 1','frame_number':1}
 if name=='create_canvas':assert inspect(p)['width']==16 and len(inspect(p)['frames'])==1
 elif name=='get_sprite_info':
  r=call(name,**s);q=inspect(p);assert r['width']==q['width'] and r['frame_count']==len(q['frames']) and r['layers']==[l['name'] for l in q['layers']]
 elif name=='add_layer':call(name,**s,layer_name='Ink');assert 'Ink' in [l['name'] for l in inspect(p)['layers']]
 elif name=='delete_layer':call('add_layer',**s,layer_name='Discard');call(name,**s,layer_name='Discard');assert [l['name'] for l in inspect(p)['layers']]==['Layer 1']
 elif name=='flatten_layers':
  draw(p);call('add_layer',**s,layer_name='Top');draw(p,5,6,'#00FF00',layer='Top');call(name,**s);q=inspect(p);assert len(q['layers'])==1;v=px(p,q['layers'][0]['name']);assert v['2,3']=='#FF0000FF' and v['5,6']=='#00FF00FF'
 elif name=='add_frame':r=call(name,**s,duration_ms=137);assert r['frame_number']==2 and inspect(p)['frames'][1]==137
 elif name=='delete_frame':call('add_frame',**s,duration_ms=137);call(name,**s,frame_number=2);assert len(inspect(p)['frames'])==1
 elif name=='duplicate_frame':
  draw(p);r=call(name,**s,source_frame=1,insert_after=0);assert r['new_frame_number']==2 and px(p,frame=2)==px(p)
 elif name=='set_frame_duration':call(name,**s,frame_number=1,duration_ms=173);assert inspect(p)['frames'][0]==173
 elif name in ['create_tag','delete_tag']:
  call('add_frame',**s,duration_ms=100);call('create_tag',**s,tag_name='idle',from_frame=1,to_frame=2,direction='pingpong');assert inspect(p)['tags'][0]=={'name':'idle','from':1,'to':2}
  if name=='delete_tag':call(name,**s,tag_name='idle');assert len(inspect(p)['tags'])==0
 elif name=='link_cel':
  call('add_frame',**s,duration_ms=100);call('add_layer',**s,layer_name='Shared');draw(p,layer='Shared');call(name,**s,layer_name='Shared',source_frame=1,target_frame=2);draw(p,color='#00FF00',layer='Shared');assert px(p,'Shared',2)['2,3']=='#00FF00FF'
 elif name=='draw_pixels':
  draw(p,7,8);draw(p,1,2,'#00FF00');assert px(p)=={'7,8':'#FF0000FF','1,2':'#00FF00FF'}
 elif name=='draw_line':call(name,**d,x1=2,y1=3,x2=8,y2=3,color='#FF0000',thickness=1);assert all(px(p)[f'{x},3']=='#FF0000FF' for x in range(2,9))
 elif name=='draw_contour':call(name,**d,points=[{'x':2,'y':2},{'x':6,'y':2},{'x':6,'y':6}],color='#FF0000',thickness=1,closed=True);assert all(k in px(p) for k in ['2,2','6,2','6,6','4,4'])
 elif name=='draw_rectangle':rect(p,x=2,y=3,w=4,h=5);assert len(px(p))==20 and px(p)['2,3']=='#AA6644FF'
 elif name=='draw_circle':call(name,**d,center_x=8,center_y=8,radius=3,color='#FF0000',filled=True);assert px(p)['8,8']=='#FF0000FF' and '0,0' not in px(p)
 elif name=='fill_area':call(name,**d,x=0,y=0,color='#FF0000',tolerance=0);assert len(px(p))==256 and set(px(p).values())=={'#FF0000FF'}
 elif name=='get_pixels':
  draw(p);r=call(name,**d,x=0,y=0,width=4,height=4,page_size=3);pixels=r['pixels']
  while r.get('next_cursor'):r=call(name,**d,x=0,y=0,width=4,height=4,page_size=3,cursor=r['next_cursor']);pixels+=r['pixels']
  assert len(pixels)==16 and next(x for x in pixels if x['x']==2 and x['y']==3)['color'].upper()=='#FF0000FF'
 elif name in ['set_palette','get_palette','set_palette_color','add_palette_color','sort_palette']:
  colors=['#FFFFFF','#000000','#888888'];call('set_palette',**s,colors=colors)
  if name=='set_palette_color':call(name,**s,index=1,color='#FF0000');assert inspect(p)['palette'][1]=='#FF0000FF'
  elif name=='add_palette_color':r=call(name,**s,color='#112233');assert inspect(p)['palette'][r['color_index']]=='#112233FF'
  elif name=='sort_palette':call(name,**s,method='luminance',ascending=True);assert inspect(p)['palette']==['#000000FF','#888888FF','#FFFFFFFF']
  else:
   r=call('get_palette',**s);assert [v[:7].upper() for v in r['colors']]==colors and inspect(p)['palette']==[v+'FF' for v in colors]
 elif name=='analyze_palette_harmonies':
  r=call(name,palette=['#FF0000','#00FFFF']);assert any({x['color1'].upper(),x['color2'].upper()}=={'#FF0000','#00FFFF'} for x in r['complementary'])
 elif name=='draw_with_dither':
  call(name,**d,region={'x':0,'y':0,'width':16,'height':16},color1='#000000',color2='#FFFFFF',pattern='checkerboard',density=.5);v=px(p);assert len(v)==256 and set(v.values())=={'#000000FF','#FFFFFFFF'} and v['0,0']!=v['1,0'], f'Expected two-color alternating pattern; actual colors={set(v.values())}'
 elif name in ['apply_shading','apply_auto_shading']:
  rect(p,x=3,y=3,w=10,h=10);before=px(p)
  if name=='apply_shading':call(name,**d,region={'x':3,'y':3,'width':10,'height':10},palette=['#221100','#AA6644','#FFCCAA'],light_direction='top_left',intensity=1,style='hard')
  else:call(name,**d,light_direction='top_left',intensity=.7,style='cell',hue_shift=True)
  assert px(p)!=before and len(set(px(p).values()))>1
 elif name=='quantize_palette':
  rect(p);draw(p,color='#FFFFFF');r=call(name,**s,target_colors=4,algorithm='median_cut',dither=True,preserve_transparency=True,convert_to_indexed=True);assert r['color_mode']=='indexed' and len(set(px(p).values()))<=4 and inspect(p)['mode']==2
 elif name=='suggest_antialiasing':
  call('draw_pixels',**d,pixels=[{'x':x,'y':y,'color':'#FFFFFF'} for x,y in [(2,0),(3,0),(1,1),(2,1),(0,2),(1,2)]]);before=px(p)
  r=call(name,**d,threshold=20,auto_apply=True,use_palette=False);assert r['applied'] and r['total_edges']>0 and px(p)!=before
 elif name=='save_as':draw(p);r=call(name,**s,output_path=str(RUN/'copy.aseprite'));assert px(r['file_path'])==px(p) and Path(r['file_path']).exists()
 elif name=='export_sprite':
  draw(p);out=RUN/'export.png';r=call(name,**s,output_path=str(out),format='png',frame_number=1);assert r['file_size']==out.stat().st_size and px(str(out),inspect(str(out))['layers'][0]['name'])==px(p)
 elif name=='export_spritesheet':
  draw(p);call('add_frame',**s,duration_ms=137);r=call(name,**s,output_path=str(RUN/'sheet.png'),layout='horizontal',padding=0,include_json=True);q=inspect(r['spritesheet_path']);assert (q['width'],q['height'])==(32,16);m=json.loads(Path(r['metadata_path']).read_text());f=m['frames'];f=list(f.values()) if isinstance(f,dict) else f;assert len(f)==2 and f[1]['duration']==137
 elif name in ['import_image','analyze_reference','downsample_image']:
  rect(p,color='#AA6644');draw(p,0,0,'#FFFFFF');png=RUN/(name+'.png');call('export_sprite',**s,output_path=str(png),format='png',frame_number=1)
  if name=='import_image':
   dest=sprite(w=32,h=32);call(name,sprite_path=dest,image_path=str(png),layer_name='Imported',frame_number=1,position={'x':4,'y':5});assert px(dest,'Imported')['4,5']=='#FFFFFFFF' and px(dest,'Imported')['5,5']=='#AA6644FF'
  elif name=='analyze_reference':
   r=call(name,reference_path=str(png),target_width=8,target_height=8,palette_size=5);assert r['metadata']['source_dimensions']=={'width':16,'height':16} and len(r['brightness_map']['grid'])==8 and any(v['color'].upper().startswith('#AA6644') for v in r['palette'])
  else:
   r=call(name,source_path=str(png),target_width=8,target_height=8,output_path=str(RUN/'downsample.aseprite'));assert inspect(r['output_path'])['width']==8 and px(r['output_path'])['1,1']=='#AA6644FF'
 elif name=='flip_sprite':draw(p);call(name,**s,direction='horizontal',target='sprite');assert px(p)=={'13,3':'#FF0000FF'}
 elif name=='rotate_sprite':draw(p);call(name,**s,angle=90,target='sprite');assert px(p)=={'12,2':'#FF0000FF'}
 elif name=='scale_sprite':draw(p);call(name,**s,scale_x=2,scale_y=2,algorithm='nearest');assert inspect(p)['width']==32 and len(px(p))==4 and px(p)['4,6']=='#FF0000FF'
 elif name=='crop_sprite':draw(p);call(name,**s,x=1,y=2,width=8,height=8);assert inspect(p)['width']==8 and px(p)=={'1,1':'#FF0000FF'}
 elif name=='resize_canvas':draw(p);call(name,**s,width=20,height=20,anchor='top_left');assert inspect(p)['width']==20 and px(p)=={'2,3':'#FF0000FF'}
 elif name=='apply_outline':draw(p);call(name,**d,color='#00FF00',thickness=1);assert px(p)['2,3']=='#FF0000FF' and any(v=='#00FF00FF' for v in px(p).values())
 elif name in ['select_rectangle','select_ellipse','select_all','deselect','move_selection','copy_selection','cut_selection','paste_clipboard']:
  rect(p,color='#FF0000')
  if name=='select_all':call(name,**s);assert all(json.loads(inspect(p)['data'])['selection'][k]==v for k,v in {'x':0,'y':0,'w':16,'h':16}.items()), f'Invalid selection persistence: {inspect(p)["data"]}'
  elif name=='select_ellipse':call(name,**s,x=2,y=2,width=6,height=6,mode='replace');assert json.loads(inspect(p)['data'])['selection']['w']==6, f'Expected width 6; persisted data={inspect(p)["data"]}'
  else:
   call('select_rectangle',**s,x=2,y=3,width=3,height=3,mode='replace')
   if name=='select_rectangle':assert all(json.loads(inspect(p)['data'])['selection'][k]==v for k,v in {'x':2,'y':3,'w':3,'h':3}.items())
   elif name=='deselect':call(name,**s);assert inspect(p)['data']==''
   elif name=='move_selection':call(name,**s,dx=1,dy=2);assert all(json.loads(inspect(p)['data'])['selection'][k]==v for k,v in {'x':3,'y':5,'w':3,'h':3}.items())
   elif name=='cut_selection':call(name,**d);assert '2,3' not in px(p) and '1,3' in px(p)
   else:
    call('copy_selection',**s);assert len(px(p,'__mcp_clipboard__'))==9
    if name=='paste_clipboard':
     call('add_layer',**s,layer_name='Destination');call(name,**s,layer_name='Destination',frame_number=1,x=8,y=9);assert px(p,'Destination').get('8,9')=='#FF0000FF' and len(px(p,'Destination'))==9
 else:raise AssertionError('No implementation for '+name)
def dither_variant(pattern):
 p=sprite();call('draw_with_dither',sprite_path=p,layer_name='Layer 1',frame_number=1,region={'x':0,'y':0,'width':16,'height':16},color1='#000000',color2='#FFFFFF',pattern=pattern,density=.5)
 colors=set(px(p).values());assert colors=={'#000000FF','#FFFFFFFF'}, f'Two-color fill collapsed to {colors}'
def quant_variant(algorithm,transparent):
 p=sprite();rect(p,x=0,y=0,w=16 if not transparent else 8,h=16)
 for x,color in enumerate(['#224466','#448822','#AA6644','#CCBB88','#FFFFFF','#FF0000']):draw(p,x,0,color)
 r=call('quantize_palette',sprite_path=p,target_colors=4,algorithm=algorithm,dither=True,preserve_transparency=True,convert_to_indexed=True)
 assert r['quantized_colors']<=4 and inspect(p)['mode']==2
 if transparent:assert '15,15' not in px(p), 'Transparent pixel became opaque'
def shading_variant(style):
 p=sprite();rect(p,color='#808080');before=px(p)
 palette=['#'+f'{v:02X}'*3 for v in range(0,256,16)]
 call('apply_shading',sprite_path=p,layer_name='Layer 1',frame_number=1,region={'x':0,'y':0,'width':16,'height':16},palette=palette,light_direction='top_left',intensity=1,style=style)
 assert px(p)!=before and len(set(px(p).values()))>1, 'No shading variation in output'
def auto_variant(style,mode):
 p=sprite(mode);call('set_palette',sprite_path=p,colors=['#000000','#CC8844','#FFFFFF'])
 call('draw_rectangle',sprite_path=p,layer_name='Layer 1',frame_number=1,x=3,y=3,width=10,height=10,color='#CC8844',filled=True,use_palette=True)
 if mode=='indexed':
  script=RUN/'transparent-index.lua';script.write_text('local s=app.activeSprite; s.transparentColor=0; s:saveAs(s.filename)');subprocess.run([ASE,'--batch',p,'--script',str(script)],check=True,capture_output=True)
 before=px(p);assert mode!='indexed' or '0,0' not in before
 r=call('apply_auto_shading',sprite_path=p,layer_name='Layer 1',frame_number=1,light_direction='top_left',intensity=.7,style=style,hue_shift=True)
 assert r['regions_shaded']>0 and px(p)!=before and len(set(px(p).values()))>1
 if mode=='indexed':assert '0,0' not in px(p), 'Shading filled transparent background'
def export_variant(fmt):
 p=sprite();rect(p,color='#FF0000');out=RUN/('format.'+fmt);call('export_sprite',sprite_path=p,output_path=str(out),format=fmt,frame_number=1)
 q=inspect(str(out));assert q['width']==16 and q['height']==16 and out.stat().st_size>0
 pixels=px(str(out),q['layers'][0]['name']);assert len(pixels)==256
 color=pixels['0,0'];assert int(color[1:3],16)>240 and int(color[3:5],16)<15, color
def sheet_variant(layout):
 p=sprite();draw(p);call('add_frame',sprite_path=p,duration_ms=137);out=RUN/('sheet-'+layout+'.png')
 r=call('export_spritesheet',sprite_path=p,output_path=str(out),layout=layout,padding=1,include_json=True)
 q=inspect(str(out));m=json.loads(Path(r['metadata_path']).read_text());f=m['frames'];f=list(f.values()) if isinstance(f,dict) else f
 assert len(f)==2 and f[1]['duration']==137 and q['width']>16 and q['height']>16
 for frame in f:
  box=frame['frame'];assert box['x']+box['w']<=q['width'] and box['y']+box['h']<=q['height']
def draw_variant(mode):
 p=sprite(mode);call('set_palette',sprite_path=p,colors=['#000000','#FFFFFF','#FF0000'])
 call('add_layer',sprite_path=p,layer_name='New');draw(p,10,11,'#FFFFFF',layer='New');draw(p,1,2,'#FFFFFF',layer='New')
 assert px(p,'New')=={'10,11':'#FFFFFFFF','1,2':'#FFFFFFFF'}, f'Actual new layer pixels: {px(p,"New")}'
def copy_offset(tool):
 p=sprite();draw(p,7,8);call('select_rectangle',sprite_path=p,x=7,y=8,width=1,height=1,mode='replace')
 if tool=='cut_selection':call(tool,sprite_path=p,layer_name='Layer 1',frame_number=1)
 else:call(tool,sprite_path=p)
 assert px(p,'__mcp_clipboard__').get('7,8')=='#FF0000FF', f'Offset cel copy lost pixel: {px(p,"__mcp_clipboard__")}'
def seed_offset(p):
 script=RUN/'offset.lua'
 script.write_text('local s=app.activeSprite; local i=Image(2,2,ColorMode.RGB); i:drawPixel(0,0,app.pixelColor.rgba(255,0,0,255)); s:newCel(s.layers[1],s.frames[1],i,Point(7,8)); s:saveAs(s.filename)')
 subprocess.run([ASE,'--batch',p,'--script',str(script)],check=True,capture_output=True,text=True)
 assert px(p)=={'7,8':'#FF0000FF'}
def offset_draw():
 p=sprite();seed_offset(p);draw(p,1,2,'#00FF00');assert px(p)=={'7,8':'#FF0000FF','1,2':'#00FF00FF'}
def offset_copy(tool):
 p=sprite();seed_offset(p);call('select_rectangle',sprite_path=p,x=7,y=8,width=1,height=1,mode='replace')
 if tool=='cut_selection':call(tool,sprite_path=p,layer_name='Layer 1',frame_number=1)
 else:call(tool,sprite_path=p)
 assert px(p,'__mcp_clipboard__').get('7,8')=='#FF0000FF', f'Copied pixels={px(p,"__mcp_clipboard__")}'
def all_then_copy():
 p=sprite();rect(p);call('select_all',sprite_path=p);call('copy_selection',sprite_path=p);assert len(px(p,'__mcp_clipboard__'))==256
def ellipse_cut():
 p=sprite();rect(p);call('select_ellipse',sprite_path=p,x=2,y=2,width=6,height=6,mode='replace');call('cut_selection',sprite_path=p,layer_name='Layer 1',frame_number=1)
 assert '2,2' in px(p), 'Ellipse corner outside mask was erased'
def offset_link():
 p=sprite();call('add_frame',sprite_path=p,duration_ms=100);seed_offset(p)
 script=RUN/'clear-target.lua';script.write_text('local s=app.activeSprite; local c=s.layers[1]:cel(2); if c then s:deleteCel(c) end; s:saveAs(s.filename)');subprocess.run([ASE,'--batch',p,'--script',str(script)],check=True,capture_output=True)
 call('link_cel',sprite_path=p,layer_name='Layer 1',source_frame=1,target_frame=2);draw(p,7,8,'#00FF00')
 assert px(p,frame=2)['7,8']=='#00FF00FF';q=inspect(p);assert all(c['x']==7 and c['y']==8 for c in q['layers'][0]['cels'])

def palette_snap():
 p=sprite('indexed');call('set_palette',sprite_path=p,colors=['#000000','#FFFFFF','#FF0000']);call('add_layer',sprite_path=p,layer_name='New')
 call('draw_pixels',sprite_path=p,layer_name='New',frame_number=1,pixels=[{'x':1,'y':2,'color':'#FFFFFF'}],use_palette=True)
 assert px(p,'New')=={'1,2':'#FFFFFFFF'}, px(p,'New')
try:
 snapshot=json.loads((ROOT/'config/mcp-contract.json').read_text())['tools'];assert list(tools.values())==snapshot
 for name in tools:case(name,lambda n=name:basic(n))
 for pattern in ['bayer_2x2','bayer_4x4','bayer_8x8','checkerboard','floyd_steinberg','grass','water','stone','cloud','brick','dots','diagonal','cross','noise','horizontal_lines','vertical_lines']:case('draw_with_dither',lambda v=pattern:dither_variant(v),pattern)
 for algorithm in ['median_cut','kmeans','octree']:
  for transparent in [False,True]:case('quantize_palette',lambda a=algorithm,t=transparent:quant_variant(a,t),algorithm+('-transparent' if transparent else '-opaque'))
 for style in ['hard','smooth','pillow']:case('apply_shading',lambda v=style:shading_variant(v),style)
 for style in ['cell','smooth','soft']:
  for mode in ['rgb','indexed']:case('apply_auto_shading',lambda s=style,m=mode:auto_variant(s,m),style+'-'+mode)
 for fmt in ['png','gif','jpg','bmp']:case('export_sprite',lambda v=fmt:export_variant(v),fmt)
 for layout in ['horizontal','vertical','rows','columns','packed']:case('export_spritesheet',lambda v=layout:sheet_variant(v),layout)
 for mode in ['rgb','grayscale','indexed']:case('draw_pixels',lambda v=mode:draw_variant(v),mode+'-new-layer-offset')
 for tool in ['copy_selection','cut_selection']:case(tool,lambda t=tool:copy_offset(t),'offset-cel')
 case('draw_pixels',offset_draw,'actual-cel-offset')
 case('link_cel',offset_link,'actual-cel-offset')
 for tool in ['copy_selection','cut_selection']:case(tool,lambda t=tool:offset_copy(t),'actual-cel-offset')
 case('select_all',all_then_copy,'followed-by-copy')
 case('select_ellipse',ellipse_cut,'followed-by-cut-mask')
 case('draw_pixels',palette_snap,'indexed-use-palette-true')
finally:
 c.close();summary={'server_version':version,'run_dir':str(RUN),'calls':len(calls),'results':results,'tools_unattempted':sorted(set(tools)-{x['tool'] for x in results})};(RUN/'summary.json').write_text(json.dumps(summary,indent=2));(OUT/'latest-run.txt').write_text(str(RUN)+'\n');print('ARTIFACTS',RUN,flush=True)

raise SystemExit(1 if any(r["status"]=="FAIL" for r in results) else 0)
