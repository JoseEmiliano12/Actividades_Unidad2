"""Genera una visualización HTML autónoma a partir del algoritmo Python."""
from __future__ import annotations

import json
from pathlib import Path
from algoritmo import Configuracion, FUNCIONES, ejecutar, resumen_generaciones


def generar(destino: Path | None = None) -> Path:
    destino = destino or Path(__file__).with_name("visualizacion.html")
    proyecto = Path(__file__).parent.name
    datos = []
    for funcion in FUNCIONES:
        historia = ejecutar(funcion, Configuracion())
        datos.append({
            "nombre": funcion.nombre,
            "minimo": funcion.minimo,
            "maximo": funcion.maximo,
            "optimo": [funcion.optimo_x, funcion.optimo_y],
            "curva": [funcion.evaluar(funcion.minimo + (funcion.maximo - funcion.minimo) * i / 699) for i in range(700)],
            "historia": [[[ind.x, ind.aptitud] for ind in poblacion] for poblacion in historia],
            "evolucion": resumen_generaciones(historia),
        })
    carga = json.dumps(datos, ensure_ascii=False, separators=(",", ":"))
    # Se escapa el cierre de script por si algún nombre se cambia en el futuro.
    carga = carga.replace("</", "<\\/")
    plantilla = r'''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>PROYECTO · Visualización de algoritmo genético</title>
<style>
:root{font-family:Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;color:#17283c;background:#eef3f8}
*{box-sizing:border-box}body{margin:0}.app{max-width:1200px;margin:auto;padding:30px 22px 50px}
.hero{background:linear-gradient(120deg,#102743,#155775 72%,#187991);color:white;border-radius:24px;padding:34px 40px;box-shadow:0 18px 40px #1034522b;display:flex;align-items:center;justify-content:space-between;gap:22px}
.eyebrow{font-size:.76rem;letter-spacing:.15em;font-weight:800;text-transform:uppercase;color:#9ee4ee}.hero h1{font-size:clamp(1.7rem,3vw,2.55rem);line-height:1.15;margin:10px 0}.hero p{max-width:650px;margin:0;color:#d9edf5;line-height:1.55}.badge{border:1px solid #ffffff66;background:#ffffff1e;padding:10px 14px;border-radius:999px;white-space:nowrap;font-size:.84rem;font-weight:700}
.panel{background:white;border:1px solid #dce5ef;border-radius:20px;padding:24px;margin-top:18px;box-shadow:0 8px 26px #18324a0b}
.toolbar{display:grid;grid-template-columns:minmax(180px,1fr) auto;gap:18px;align-items:end}.control label,.slider-label{display:block;font-size:.76rem;font-weight:800;letter-spacing:.09em;text-transform:uppercase;color:#64788d;margin-bottom:8px}
.actions{display:flex;gap:8px;flex-wrap:wrap}button,select{font:inherit;border:1px solid #cbd9e6;background:#fff;border-radius:10px;padding:10px 13px;color:#20354b}select{width:100%;max-width:340px;font-weight:650}button{font-weight:700}button:hover{background:#e8f5f8;border-color:#76b9c9;cursor:pointer}button:focus-visible,select:focus-visible,input:focus-visible{outline:3px solid #48b7d2;outline-offset:2px}.primary{background:#136781;color:#fff;border-color:#136781}.primary:hover{background:#0b526a;color:#fff}
.timeline{grid-column:1/-1;border-top:1px solid #e8eef4;padding-top:16px;display:flex;align-items:center;gap:15px}.timeline input{flex:1;accent-color:#147895;min-width:80px}.counter{font-variant-numeric:tabular-nums;background:#e8f5f8;color:#12627d;padding:7px 12px;border-radius:999px;font-weight:800;white-space:nowrap}
.section-head{display:flex;justify-content:space-between;align-items:center;gap:12px;margin-bottom:8px}.section-head h2{margin:0;font-size:1.12rem}.section-head span{font-size:.78rem;font-weight:700;color:#64788d;text-transform:uppercase;letter-spacing:.07em}
canvas{display:block;width:100%;height:410px}#trayectoria,#evolucion{height:220px}.stats{background:#ecf7f8;border:1px solid #cce8ed;color:#17465c;border-radius:12px;padding:13px 15px;font-weight:700;margin:8px 0 17px;line-height:1.5;font-variant-numeric:tabular-nums}.hint{font-size:.91rem;color:#587087;line-height:1.5;margin:0 0 12px}.legend{display:flex;gap:18px;flex-wrap:wrap;font-size:.86rem;color:#526b82}.swatch{display:inline-block;width:11px;height:11px;border-radius:50%;margin-right:6px}.footer{color:#6d8295;text-align:center;font-size:.82rem;margin-top:24px}
@media(max-width:700px){.app{padding:12px 12px 30px}.hero{padding:26px 22px;display:block}.badge{display:inline-block;margin-top:20px}.panel{padding:16px;border-radius:16px}.toolbar{grid-template-columns:1fr}.actions button{flex:1}.timeline{grid-column:auto;flex-wrap:wrap}.timeline .slider-label{width:100%;margin:0}canvas{height:330px}#trayectoria,#evolucion{height:200px}}
</style>
</head><body><main class="app">
<header class="hero"><div><div class="eyebrow">Proyecto 1 · Simulación interactiva</div><h1>Optimización de funciones</h1><p>Explora las dos funciones del proyecto. Reproduce el algoritmo genético y observa cómo cambia la población en cada generación.</p></div><span class="badge">Python · sin DEAP</span></header>
<section class="panel toolbar" aria-label="Controles de simulación"><div class="control"><label for="funcion">Función a optimizar</label><select id="funcion"><option value="0">Función 1</option><option value="1">Función 2</option></select></div>
<div class="actions"><button id="inicio" title="Ir a la primera generación">|◀ Inicio</button><button id="anterior">◀ Anterior</button><button id="siguiente">Siguiente ▶</button><button id="final" title="Ir a la última generación">Final ▶|</button><button id="reproducir" class="primary">▶ Reproducir</button></div>
<div class="timeline"><label class="slider-label" for="generacion">Generación</label><input id="generacion" type="range" min="0" max="60" value="0" aria-label="Generación"><span id="contador" class="counter">0 / 60</span></div></section>
<section class="panel"><div class="section-head"><h2>Población sobre la función</h2><span>Vista por generación</span></div><canvas id="grafica" aria-label="Gráfica de la función y sus individuos"></canvas><div id="estadisticas" class="stats" aria-live="polite"></div><div class="legend"><span><span class="swatch" style="background:#28518c"></span>Función</span><span><span class="swatch" style="background:#b45309"></span>Óptimo de referencia</span><span>★ Mejor de la generación</span><span>Selecciona un punto para destacarlo.</span></div></section>
<section class="panel"><div class="section-head"><h2>Evolución del resultado</h2><span>Mejor y media</span></div><p class="hint">Compara el mejor de cada generación, la media de la población y el mejor valor encontrado hasta ese momento.</p><canvas id="evolucion" aria-label="Mejor de la generación, media y mejor acumulado"></canvas><div class="legend"><span><span class="swatch" style="background:#28518c"></span>Mejor acumulado</span><span><span class="swatch" style="background:#df7842"></span>Mejor de la generación</span><span><span class="swatch" style="background:#7c8b99"></span>Media</span></div></section>
<section class="panel"><div class="section-head"><h2>Movimiento de la población</h2><span>Historial</span></div><p class="hint">Cada color representa una posición de la población. Después del cruce y la mutación, una posición puede pertenecer a un individuo nuevo.</p><canvas id="trayectoria" aria-label="Trayectorias de las posiciones de la población"></canvas></section>
<p class="footer">Atajos: ← y → para avanzar · Inicio y Fin para saltar · Espacio para reproducir o pausar</p>
<div class="footer">Algoritmo genético binario · Proyecto 1</div>
</main><script>
const datos = DATOS;
let indice=0,gen=0,seleccionado=null,temporizador=null,fraccion=0;
const grafica=document.getElementById('grafica'),tray=document.getElementById('trayectoria'),evol=document.getElementById('evolucion');
const slider=document.getElementById('generacion'),contador=document.getElementById('contador'),stats=document.getElementById('estadisticas');
function color(i,n){return `hsl(${Math.round(i*360/n)} 70% 42%)`}
function preparar(canvas){const dpr=window.devicePixelRatio||1,rect=canvas.getBoundingClientRect();canvas.width=Math.round(rect.width*dpr);canvas.height=Math.round(rect.height*dpr);let ctx=canvas.getContext('2d');ctx.setTransform(dpr,0,0,dpr,0,0);return [ctx,rect.width,rect.height]}
function detener(){if(temporizador){clearInterval(temporizador);temporizador=null}document.getElementById('reproducir').textContent='▶ Reproducir';fraccion=0}
function fijar(n){detener();gen=Math.max(0,Math.min(datos[indice].historia.length-1,n));slider.value=gen;dibujar()}
function dibujar(){
 const d=datos[indice], [ctx,w,h]=preparar(grafica), L=63,R=w-24,T=22,B=h-46;
 let ymin=Math.min(...d.curva),ymax=Math.max(...d.curva),m=Math.max((ymax-ymin)*.1,.05);ymin-=m;ymax+=m;
 const pt=(x,y)=>[L+(x-d.minimo)/(d.maximo-d.minimo)*(R-L), B-(y-ymin)/(ymax-ymin)*(B-T)];
 ctx.fillStyle='#526174';ctx.font='12px system-ui';ctx.strokeStyle='#e9edf3';ctx.lineWidth=1;
 for(let j=0;j<=4;j++){let y=T+(B-T)*j/4,x=L+(R-L)*j/4;ctx.beginPath();ctx.moveTo(L,y);ctx.lineTo(R,y);ctx.moveTo(x,T);ctx.lineTo(x,B);ctx.stroke();ctx.textAlign='right';ctx.fillText((ymax-(ymax-ymin)*j/4).toFixed(2),L-8,y+4);ctx.textAlign='center';ctx.fillText((d.minimo+(d.maximo-d.minimo)*j/4).toFixed(2),x,B+18)}
 ctx.strokeStyle='#28518c';ctx.lineWidth=2;ctx.beginPath();d.curva.forEach((y,i)=>{let [x0,y0]=pt(d.minimo+(d.maximo-d.minimo)*i/699,y);i?ctx.lineTo(x0,y0):ctx.moveTo(x0,y0)});ctx.stroke();
 let [ox,oy]=pt(...d.optimo);ctx.fillStyle='#b45309';ctx.textAlign='center';ctx.font='bold 14px system-ui';ctx.fillText('★ óptimo',ox,oy-12);
 const pop=d.historia[gen],prev=d.historia[Math.max(0,gen-1)],next=d.historia[Math.min(gen+1,d.historia.length-1)];
 window.puntos=[];
 pop.forEach((ind,i)=>{let [x,y]=pt(...ind),[nx,ny]=pt(...next[i]),[px,py]=pt(...prev[i]);ctx.strokeStyle=color(i,pop.length);ctx.lineWidth=1;ctx.setLineDash([3,3]);ctx.beginPath();if(fraccion>0){ctx.moveTo(x,y);ctx.lineTo(nx,ny)}else if(gen>0){ctx.moveTo(px,py);ctx.lineTo(x,y)}ctx.stroke();ctx.setLineDash([]);if(fraccion>0){x+=(nx-x)*fraccion;y+=(ny-y)*fraccion}window.puntos.push([x,y]);});
 pop.forEach((ind,i)=>{let [x,y]=window.puntos[i];ctx.beginPath();ctx.arc(x,y,i===seleccionado?7:4,0,2*Math.PI);ctx.fillStyle=color(i,pop.length);ctx.fill();ctx.strokeStyle=i===seleccionado?'#111827':'white';ctx.lineWidth=i===seleccionado?2:1;ctx.stroke()});
 let mejor=pop.reduce((a,b)=>a[1]>b[1]?a:b),media=pop.reduce((a,b)=>a+b[1],0)/pop.length;
 let [mx,my]=pt(...mejor);ctx.fillStyle='#173d58';ctx.textAlign='center';ctx.font='bold 13px system-ui';ctx.fillText('★ mejor',mx,my+18);
 stats.textContent=`Generación ${gen}/${d.historia.length-1} · Mejor: x=${mejor[0].toFixed(5)}, f(x)=${mejor[1].toFixed(5)} · Media=${media.toFixed(5)} · Mejor acumulado=${d.evolucion[gen][2].toFixed(5)}`+(seleccionado===null?'':` · Punto ${seleccionado+1}: x=${pop[seleccionado][0].toFixed(5)}`);
 contador.textContent=`${gen} / ${d.historia.length-1}`;
 dibujarEvolucion();dibujarTrayectoria();
}
function dibujarEvolucion(){const d=datos[indice],[ctx,w,h]=preparar(evol),L=63,R=w-24,T=16,B=h-32,total=d.evolucion.length-1;
 const valores=d.evolucion.flat(),min0=Math.min(...valores),max0=Math.max(...valores),m=Math.max((max0-min0)*.08,.05),ymin=min0-m,ymax=max0+m;
 const pt=(g,v)=>[L+g/Math.max(total,1)*(R-L),B-(v-ymin)/(ymax-ymin)*(B-T)];
 ctx.font='12px system-ui';ctx.fillStyle='#526174';ctx.strokeStyle='#e9edf3';ctx.lineWidth=1;
 for(let j=0;j<=4;j++){let y=T+j*(B-T)/4,x=L+j*(R-L)/4;ctx.beginPath();ctx.moveTo(L,y);ctx.lineTo(R,y);ctx.moveTo(x,T);ctx.lineTo(x,B);ctx.stroke();ctx.textAlign='right';ctx.fillText((ymax-j*(ymax-ymin)/4).toFixed(2),L-7,y+4);ctx.textAlign='center';ctx.fillText(String(Math.round(j*total/4)),x,B+16)}
 ctx.textAlign='center';ctx.fillText('Generación',(L+R)/2,h-6);
 [[2,'#28518c',3],[0,'#df7842',2],[1,'#7c8b99',2]].forEach(([col,color,width])=>{ctx.strokeStyle=color;ctx.lineWidth=width;ctx.beginPath();d.evolucion.forEach((fila,g)=>{let [x,y]=pt(g,fila[col]);g?ctx.lineTo(x,y):ctx.moveTo(x,y)});ctx.stroke();let [x,y]=pt(gen,d.evolucion[gen][col]);ctx.beginPath();ctx.arc(x,y,4,0,2*Math.PI);ctx.fillStyle=color;ctx.fill()});
 let [x]=pt(gen,ymin);ctx.strokeStyle='#334155';ctx.setLineDash([4,3]);ctx.beginPath();ctx.moveTo(x,T);ctx.lineTo(x,B);ctx.stroke();ctx.setLineDash([])}
function dibujarTrayectoria(){let d=datos[indice],[ctx,w,h]=preparar(tray),L=58,R=w-23,T=16,B=h-30,total=d.historia.length-1;
 const pt=(g,x)=>[L+g/total*(R-L),B-(x-d.minimo)/(d.maximo-d.minimo)*(B-T)];
 ctx.font='12px system-ui';ctx.fillStyle='#526174';ctx.strokeStyle='#e9edf3';ctx.lineWidth=1;
 for(let j=0;j<=4;j++){let y=T+j*(B-T)/4;ctx.beginPath();ctx.moveTo(L,y);ctx.lineTo(R,y);ctx.stroke();ctx.textAlign='right';ctx.fillText((d.maximo-(d.maximo-d.minimo)*j/4).toFixed(1),L-7,y+4)}
 ctx.textAlign='center';ctx.fillText('Generación',(L+R)/2,h-8);
 for(let i=0;i<d.historia[0].length;i++){ctx.strokeStyle=color(i,d.historia[0].length);ctx.lineWidth=i===seleccionado?3:1;ctx.beginPath();for(let g=0;g<=gen;g++){let [x,y]=pt(g,d.historia[g][i][0]);g?ctx.lineTo(x,y):ctx.moveTo(x,y)}ctx.stroke();let [x,y]=pt(gen,d.historia[gen][i][0]);ctx.beginPath();ctx.arc(x,y,3,0,2*Math.PI);ctx.fillStyle=color(i,d.historia[0].length);ctx.fill()}
 let [x]=pt(gen,d.minimo);ctx.strokeStyle='#334155';ctx.setLineDash([4,3]);ctx.beginPath();ctx.moveTo(x,T);ctx.lineTo(x,B);ctx.stroke();ctx.setLineDash([])}
document.getElementById('funcion').onchange=e=>{indice=Number(e.target.value);seleccionado=null;slider.max=datos[indice].historia.length-1;fijar(0)};
document.getElementById('inicio').onclick=()=>fijar(0);document.getElementById('final').onclick=()=>fijar(datos[indice].historia.length-1);
document.getElementById('anterior').onclick=()=>fijar(gen-1);document.getElementById('siguiente').onclick=()=>fijar(gen+1);slider.oninput=e=>fijar(Number(e.target.value));
document.getElementById('reproducir').onclick=()=>{if(temporizador){detener();return}if(gen>=datos[indice].historia.length-1)gen=0;document.getElementById('reproducir').textContent='⏸ Pausar';temporizador=setInterval(()=>{fraccion+=.2;if(fraccion>=1){fraccion=0;gen++;slider.value=gen;if(gen>=datos[indice].historia.length-1)detener()}dibujar()},45)};
grafica.onclick=e=>{let r=grafica.getBoundingClientRect(),x=e.clientX-r.left,y=e.clientY-r.top,mejor=-1,dist=12;window.puntos.forEach((p,i)=>{let d=Math.hypot(x-p[0],y-p[1]);if(d<dist){dist=d;mejor=i}});if(mejor>=0){seleccionado=mejor;dibujar()}};
document.addEventListener('keydown',e=>{if(['INPUT','SELECT','BUTTON','TEXTAREA'].includes(document.activeElement?.tagName))return;let destino=null;if(e.key==='ArrowLeft')destino=gen-1;else if(e.key==='ArrowRight')destino=gen+1;else if(e.key==='Home')destino=0;else if(e.key==='End')destino=datos[indice].historia.length-1;else if(e.key===' '){e.preventDefault();document.getElementById('reproducir').click();return}if(destino!==null){e.preventDefault();fijar(destino)}});
window.onresize=dibujar;slider.max=datos[0].historia.length-1;dibujar();
</script></body></html>'''
    destino.write_text(plantilla.replace("PROYECTO", "Proyecto " + proyecto[-1]).replace("DATOS", carga), encoding="utf-8")
    return destino


if __name__ == "__main__":
    print(generar())
