#!/usr/bin/env python3
"""Run isolated real-Aseprite workflows through the plugin's selected MCP wrapper."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import struct
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('contract', ROOT/'bin/validate-mcp-contract.py')
contract = importlib.util.module_from_spec(spec)
spec.loader.exec_module(contract)


def linked_cels(path):
    """Inspect Aseprite file cel chunks; identical pixels alone do not prove a link."""
    data = Path(path).read_bytes()
    assert struct.unpack_from('<H', data, 4)[0] == 0xA5E0
    pos, links = 128, []
    for frame in range(struct.unpack_from('<H', data, 6)[0]):
        size, magic, old_count = struct.unpack_from('<IHH', data, pos)
        assert magic == 0xF1FA
        count = struct.unpack_from('<I', data, pos+12)[0] or old_count
        chunk = pos+16
        for _ in range(count):
            length, kind = struct.unpack_from('<IH', data, chunk)
            if kind == 0x2005:
                layer, x, y, opacity, cel_type = struct.unpack_from('<HhhBH', data, chunk+6)
                if cel_type == 1:
                    target = struct.unpack_from('<H', data, chunk+6+16)[0]
                    links.append((frame, layer, target))
            chunk += length
        pos += size
    return links


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--aseprite', required=True, type=Path, help='real Aseprite executable')
    args=parser.parse_args()
    aseprite=args.aseprite.resolve(strict=True)
    subprocess.run([str(aseprite),'--version'], check=True)
    snapshot=json.loads((ROOT/'config/mcp-contract.json').read_text())['tools']
    schemas={t['name']:t for t in snapshot}
    with tempfile.TemporaryDirectory(prefix='pixel-plugin-live-') as tmp:
        work=Path(tmp)
        config=work/'config.json'
        config.write_text(json.dumps({'aseprite_path':str(aseprite),'temp_dir':str(work/'sprites'),'log_level':'error'}))
        env=dict(os.environ, PIXEL_MCP_CONFIG=str(config))
        subprocess.run([str(ROOT/'bin/pixel-mcp'),'--health'],env=env,check=True)
        client=contract.load_module('client','mcp-client.py').Client([str(ROOT/'bin/pixel-mcp')],env)
        calls=0
        def call(name, **arguments):
            nonlocal calls
            contract.validate_call(schemas, {'name':name,'arguments':arguments})
            value=client.call(name,arguments)
            contract.Draft202012Validator(schemas[name]['outputSchema']).validate(value)
            for flag in ['success','Success']:
                if flag in value:
                    assert value[flag] is True, (name,value)
            calls+=1
            return value
        try:
            contract.compare(client.tools(),snapshot)
            sprite=call('create_canvas',width=16,height=16,color_mode='rgb')['file_path']
            s={'sprite_path':sprite}
            assert call('add_frame',**s,duration_ms=100)['frame_number']==2
            # Frames precede Shared layer, so both target cels really are absent.
            call('add_layer',**s,layer_name='Shared')
            d={**s,'layer_name':'Shared','frame_number':1}
            assert call('draw_pixels',**d,pixels=[{'x':2,'y':3,'color':'#FF0000'}])['pixels_drawn']==1
            call('link_cel',**s,layer_name='Shared',source_frame=1,target_frame=2)
            assert linked_cels(sprite), 'No serialized native linked cel'
            call('draw_pixels',**d,pixels=[{'x':2,'y':3,'color':'#00FF00'}])
            for frame in [1,2]:
                pixels=call('get_pixels',**s,layer_name='Shared',frame_number=frame,x=2,y=3,width=1,height=1)['pixels']
                assert pixels[0]['color'].upper().startswith('#00FF00'), pixels
            call('create_tag',**s,tag_name='idle',from_frame=1,to_frame=2,direction='pingpong')
            call('set_frame_duration',**s,frame_number=1,duration_ms=150)
            info=call('get_sprite_info',**s)
            assert info['frame_count']==2 and 'Shared' in info['layers']
            # A second layer exercises backward links without overwriting cels.
            call('add_layer',**s,layer_name='Backward')
            call('draw_pixels',**s,layer_name='Backward',frame_number=2,pixels=[{'x':4,'y':4,'color':'#1122FF'}])
            call('link_cel',**s,layer_name='Backward',source_frame=2,target_frame=1)
            assert len(linked_cels(sprite))>=2
            print('PASS: forward/backward native linked cels, shared edits, frame timing and tags')
            # A documented export workflow modifies only a native copy.
            copy_path=call('save_as',**s,output_path=str(work/'scaled.aseprite'))['file_path']
            dimensions=call('scale_sprite',sprite_path=copy_path,scale_x=2,scale_y=2,algorithm='nearest')
            assert dimensions['new_width']==32 and dimensions['new_height']==32
            png=work/'hero.png'
            result=call('export_sprite',sprite_path=copy_path,output_path=str(png),format='png',frame_number=1)
            assert result['file_size']>0 and png.read_bytes()[:8]==b'\x89PNG\r\n\x1a\n'
            assert struct.unpack('>II',png.read_bytes()[16:24])==(32,32)
            gif=work/'hero.gif'
            call('export_sprite',**s,output_path=str(gif),format='gif',frame_number=0)
            assert gif.read_bytes()[:6] in [b'GIF87a',b'GIF89a']
            assert call('get_sprite_info',sprite_path=str(gif))['frame_count']==2, 'GIF did not contain both frames'
            sheet=call('export_spritesheet',**s,output_path=str(work/'sheet.png'),layout='rows',padding=1,include_json=True)
            assert sheet['frame_count']==2 and Path(sheet['spritesheet_path']).stat().st_size>0
            metadata=json.loads(Path(sheet['metadata_path']).read_text())
            frames=metadata['frames']; frames=list(frames.values()) if isinstance(frames,dict) else frames
            assert len(frames)==2 and frames[0]['duration']==150 and frames[1]['duration']==100
            assert call('get_sprite_info',**s)['width']==16, 'Export scaling changed original'
            print('PASS: saved-copy scaling, PNG dimensions, animated GIF, spritesheet and actual JSON timing')
            indexed=call('create_canvas',width=16,height=16,color_mode='indexed')['file_path']
            p={'sprite_path':indexed}
            layer=call('get_sprite_info',**p)['layers'][0]
            call('set_palette',**p,colors=['#000000','#CC8844','#FFFFFF'])
            target={**p,'layer_name':layer,'frame_number':1}
            call('draw_rectangle',**target,x=3,y=3,width=10,height=10,color='#CC8844',filled=True,use_palette=True)
            before=call('get_pixels',**target,x=3,y=3,width=10,height=10)['pixels']
            shade=call('apply_auto_shading',**target,light_direction='top_left',intensity=0.6,style='cell',hue_shift=True)
            assert shade['regions_shaded']>0 and shade['palette']
            after=call('get_pixels',**target,x=3,y=3,width=10,height=10)['pixels']
            assert before!=after, 'Automatic shading made no pixel changes'
            palette=call('get_palette',**p)['colors']
            assert len(set(x['color'] for x in after))>1, 'Indexed shading lost color variation'
            assert len(palette)>3, 'Indexed shading did not preserve generated palette colors'
            # Dither and quantization are distinct actual calls; validate legacy output casing.
            call('draw_with_dither',**target,region={'x':0,'y':0,'width':2,'height':2},color1='#000000',color2='#FFFFFF',pattern='checkerboard',density=0.5)
            transparent=client.request('tools/call', {'name':'quantize_palette','arguments':{**p,'target_colors':4,'algorithm':'median_cut','dither':True,'preserve_transparency':True,'convert_to_indexed':True}})
            assert transparent.get('isError') and '#00000000' in str(transparent), 'Review transparent quantization limitation: upstream behavior changed'
            print('KNOWN UPSTREAM LIMITATION: transparent quantization rejected #00000000 (not a successful quantization)')
            opaque=call('create_canvas',width=8,height=8,color_mode='rgb')['file_path']
            opaque_layer=call('get_sprite_info',sprite_path=opaque)['layers'][0]
            call('draw_with_dither',sprite_path=opaque,layer_name=opaque_layer,frame_number=1,region={'x':0,'y':0,'width':8,'height':8},color1='#223344',color2='#CCDDEE',pattern='checkerboard',density=0.5)
            quant=call('quantize_palette',sprite_path=opaque,target_colors=4,algorithm='median_cut',dither=True,preserve_transparency=True,convert_to_indexed=True)
            assert quant['color_mode']=='indexed' and quant['quantized_colors']<=4
            call('suggest_antialiasing',**target,auto_apply=False,use_palette=True)
            print('PASS: indexed auto shading changes real colors, dither fill, opaque-image quantization and AA analysis')
            print(f'PASS: {calls} real tools/call operations with input/output schema validation')
        finally:
            client.close()


if __name__=='__main__':
    main()
