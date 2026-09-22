(function(root){
'use strict';
function createEngine(){
 const seeds=[260,460,700,950,1190],limit=1380,goal=1320;
 let s;
 function reset(){s={x:88,v:0,angle:0,time:0,collected:seeds.map(()=>false),won:false};return s;}
 function step(dt,input=0,brake=false){
  dt=Math.max(0,Math.min(dt,1/30));if(s.won)return s;s.time+=dt;
  if(brake||!input){const drag=(brake?1050:390)*dt;s.v=Math.sign(s.v)*Math.max(0,Math.abs(s.v)-drag);}
  else s.v=Math.max(-185,Math.min(185,s.v+input*650*dt));
  const old=s.x;s.x=Math.max(45,Math.min(limit,s.x+s.v*dt));
  if(s.x===45&&s.v<0||s.x===limit&&s.v>0)s.v=0;
  s.angle+=(s.x-old)/36;
  if(Math.abs(s.v)<.5){let a=((s.angle+Math.PI)%(Math.PI*2)+Math.PI*2)%(Math.PI*2)-Math.PI;s.angle-=a*Math.min(1,dt*10);}
  seeds.forEach((x,i)=>{if(Math.abs(s.x-x)<32)s.collected[i]=true;});
  if(s.x>=goal&&s.collected.every(Boolean)){s.won=true;s.v=0;}
  return s;
 }
 reset();return {reset,step,get state(){return s;},seeds,limit,goal};
}
if(typeof module!=='undefined'&&module.exports)module.exports={createEngine};else root.createAppleEngine=createEngine;
})(typeof window!=='undefined'?window:globalThis);
