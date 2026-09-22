(async()=>{
'use strict';
const canvas=document.getElementById('game'),ctx=canvas.getContext('2d'),status=document.getElementById('status'),score=document.getElementById('score'),clock=document.getElementById('clock');
const keys=new Set(),pointers=new Map();let loaded=false,last=0,announced=-1;
const g=createAppleEngine(),W=960,H=360,ground=278,world=1440,scale=3;
function load(src){return new Promise((resolve,reject)=>{const i=new Image();i.onload=()=>resolve(i);i.onerror=reject;i.src=src;});}
let roll,idle;try{[roll,idle]=await Promise.all([load(ASSETS.roll),load(ASSETS.idle)]);}catch(e){status.textContent='이미지를 불러오지 못했습니다. 파일을 다시 열어주세요.';return;}
loaded=true;window.appleGame={ready:true,state:()=>JSON.parse(JSON.stringify(g.state))};status.textContent='씨앗 5개를 모아 오른쪽 깃발까지 굴러가세요.';
function reset(){g.reset();keys.clear();pointers.clear();announced=-1;status.textContent='씨앗 5개를 모아 오른쪽 깃발까지 굴러가세요.';canvas.focus();}
document.getElementById('reset').addEventListener('click',reset);
const accepted=['ArrowLeft','ArrowRight','a','A','d','D',' '];
window.addEventListener('keydown',e=>{if(e.ctrlKey||e.metaKey||e.altKey)return;if(e.key==='r'||e.key==='R'){reset();e.preventDefault();return;}if(accepted.includes(e.key)){if(e.key===' '&&e.target.tagName==='BUTTON')return;keys.add(e.key);e.preventDefault();}});
window.addEventListener('keyup',e=>keys.delete(e.key));
function clear(){keys.clear();pointers.clear();}
window.addEventListener('blur',clear);document.addEventListener('visibilitychange',()=>{if(document.hidden)clear();});
for(const b of document.querySelectorAll('[data-control]')){
 b.addEventListener('pointerdown',e=>{e.preventDefault();b.setPointerCapture(e.pointerId);pointers.set(e.pointerId,b.dataset.control);canvas.focus();});
 for(const type of ['pointerup','pointercancel','lostpointercapture'])b.addEventListener(type,e=>pointers.delete(e.pointerId));
}
canvas.addEventListener('pointerdown',()=>canvas.focus());
function rect(x,y,w,h,c){ctx.fillStyle=c;ctx.fillRect(Math.round(x),Math.round(y),w,h);}
function cloud(x,y){rect(x,y,52,12,'#fff4dd');rect(x+10,y-8,24,8,'#fff4dd');rect(x+36,y-4,24,12,'#fff4dd');}
function seed(x,y,t){ctx.fillStyle='#996129';ctx.beginPath();ctx.moveTo(x,y-9);ctx.lineTo(x+7,y);ctx.lineTo(x,y+9);ctx.lineTo(x-7,y);ctx.closePath();ctx.fill();ctx.fillStyle='#ffd772';ctx.beginPath();ctx.moveTo(x,y-6);ctx.lineTo(x+4,y);ctx.lineTo(x,y+6);ctx.lineTo(x-4,y);ctx.closePath();ctx.fill();rect(x-1,y-3,2,3,'#fff4c7');}
function frame(now){
 const dt=last?Math.min((now-last)/1000,.25):0;last=now;
 const touch=[...pointers.values()],left=keys.has('ArrowLeft')||keys.has('a')||keys.has('A')||touch.includes('left'),right=keys.has('ArrowRight')||keys.has('d')||keys.has('D')||touch.includes('right');
 for(let remain=dt;remain>0;){const sub=Math.min(remain,1/60);g.step(sub,(right?1:0)-(left?1:0),keys.has(' ')||touch.includes('brake'));remain-=sub;}
 const s=g.state,cam=Math.round(Math.max(0,Math.min(world-W,s.x-250))),count=s.collected.filter(Boolean).length;
 ctx.imageSmoothingEnabled=false;rect(0,0,W,H,'#f5dfb2');rect(0,0,W,160,'#f9e9c8');cloud(90-cam*.2,65);cloud(430-cam*.2,38);cloud(800-cam*.2,85);
 ctx.fillStyle='#b6c594';ctx.beginPath();ctx.moveTo(0,250);ctx.lineTo(0,190);ctx.lineTo(150-cam*.15,137);ctx.lineTo(330-cam*.15,217);ctx.lineTo(630-cam*.15,125);ctx.lineTo(W,193);ctx.lineTo(W,280);ctx.closePath();ctx.fill();
 rect(0,ground,W,H-ground,'#b99163');rect(0,ground,W,7,'#79945b');rect(0,ground+7,W,4,'#627c49');
 for(let x=0;x<world;x+=37){rect(x-cam,ground+31+(x%3)*9,6,3,'#9d7954');}
 // Route markers and a finish basket/flag make the objective visible while scrolling.
 for(let x=170;x<1300;x+=200){rect(x-cam,ground-5,3,5,'#e5d5a1');}
 g.seeds.forEach((x,i)=>{if(!s.collected[i])seed(x-cam,ground-35+Math.sin(now/320+i)*3);});
 const fx=g.goal-cam;rect(fx,ground-118,5,118,'#76513c');rect(fx+5,ground-117,42,25,'#c95e54');rect(fx+9,ground-112,8,8,'#ffe5aa');rect(fx+25,ground-104,8,8,'#ffe5aa');
 ctx.fillStyle='#68583b44';ctx.beginPath();ctx.ellipse(s.x-cam,ground-2,31,5,0,0,Math.PI*2);ctx.fill();
 const a=((s.angle%(Math.PI*2))+Math.PI*2)%(Math.PI*2),upright=Math.min(a,Math.PI*2-a)<.035;
 if(Math.abs(s.v)<.5&&upright){const f=Math.floor(now/100)%24;ctx.drawImage(idle,f*32,0,32,32,Math.round(s.x-cam-48),ground-90,96,96);}
 else{const f=Math.round(a/(Math.PI*2)*32)%32,foot=ASSETS.feet[f];ctx.drawImage(roll,f*40,0,40,40,Math.round(s.x-cam-60),ground-(foot+1)*scale,120,120);}
 score.textContent=count+' / 5';clock.textContent=s.time.toFixed(1)+'초';
 if(count!==announced){announced=count;if(count===5)status.textContent='씨앗을 모두 모았어요! 오른쪽 깃발까지 가세요.';}
 if(s.won){status.textContent='도착! 씨앗 5개를 모두 모았습니다. 다시 하기로 한 번 더 굴려보세요.';rect(260,88,440,108,'#263f35ee');ctx.textAlign='center';ctx.fillStyle='#fff0cf';ctx.font='bold 28px system-ui';ctx.fillText('잘 굴렸어요!',480,133);ctx.font='16px system-ui';ctx.fillText('씨앗 5개 · '+s.time.toFixed(1)+'초',480,167);}
 requestAnimationFrame(frame);
}
requestAnimationFrame(frame);
})();
