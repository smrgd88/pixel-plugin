local s=app.activeSprite
local o={width=s.width,height=s.height,mode=s.colorMode,transparent=s.transparentColor,data=s.data,palette={},frames={},layers={},tags={}}
local store=s.properties("pixel-mcp/selection")
if store.version==1 then o.selection=store.mask
elseif s.data~="" then
 local ok,legacy=pcall(function() return json.decode(s.data).selection end)
 if ok then o.selection=legacy end
end
for i=0,#s.palettes[1]-1 do
 local c=s.palettes[1]:getColor(i)
 o.palette[#o.palette+1]=string.format('#%02X%02X%02X%02X',c.red,c.green,c.blue,c.alpha)
end
for _,f in ipairs(s.frames) do o.frames[#o.frames+1]=math.floor(f.duration*1000+0.5) end
for _,t in ipairs(s.tags) do o.tags[#o.tags+1]={name=t.name,from=t.fromFrame.frameNumber,to=t.toFrame.frameNumber} end
for _,l in ipairs(s.layers) do
 local v={name=l.name,visible=l.isVisible,cels={}}
 for _,cel in ipairs(l.cels) do
  local c={frame=cel.frame.frameNumber,x=cel.position.x,y=cel.position.y,pixels={}}
  for y=0,cel.image.height-1 do for x=0,cel.image.width-1 do
   local raw=cel.image:getPixel(x,y)
   local color
   if s.colorMode==ColorMode.INDEXED then
    if raw < #s.palettes[1] then color=s.palettes[1]:getColor(raw) else c.pixels[tostring(x+cel.position.x)..','..tostring(y+cel.position.y)]='INVALID_PALETTE_INDEX_'..raw; color=Color(0,0,0,0) end
    if raw==s.transparentColor and not l.isBackground then color=Color(0,0,0,0) end
   elseif s.colorMode==ColorMode.GRAY then
    local val=app.pixelColor.grayaV(raw);color=Color(val,val,val,app.pixelColor.grayaA(raw))
   else color=Color{r=app.pixelColor.rgbaR(raw),g=app.pixelColor.rgbaG(raw),b=app.pixelColor.rgbaB(raw),a=app.pixelColor.rgbaA(raw)} end
   if color.alpha>0 then c.pixels[tostring(x+cel.position.x)..','..tostring(y+cel.position.y)]=string.format('#%02X%02X%02X%02X',color.red,color.green,color.blue,color.alpha) end
  end end
  v.cels[#v.cels+1]=c
 end
 o.layers[#o.layers+1]=v
end
print(json.encode(o))
