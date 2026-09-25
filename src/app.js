(() => {
'use strict';
const {evidence,mechanisms,citations,predictions,config}=window.RESEARCH_DATA;
document.querySelectorAll('.contents-menu a').forEach(a=>a.addEventListener('click',()=>{a.closest('details').open=false;}));
const byId=Object.fromEntries(evidence.map(c=>[c.id,c]));
const refs=Object.fromEntries(citations.map(c=>[c.id,c]));
const inspector=document.getElementById('inspector');
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const pretty=s=>({established:'Established mechanism',supported:'Supported synthesis',proposed:'Proposed mechanism',horizon:'Horizon hypothesis'}[s]);
let selected='C09';
function showClaim(id,scroll=false){
 const c=byId[id];if(!c)return;selected=id;
 inspector.innerHTML=`<div class="eyebrow">Connection ${esc(c.id)}</div><span class="badge ${c.status}">${pretty(c.status)} · ${c.grade}</span><h3>${esc(c.title)}</h3><p class="scope">${esc(c.scope)}</p><h4>What the evidence supports</h4><p>${esc(c.mechanism)}</p><h4>Unresolved connection</h4><p>${esc(c.uncertainty)}</p><h4>Strongest rival explanation</h4><p>${esc(c.rival)}</p><h4>What would weaken it</h4><p>${esc(c.falsifier)}</p><h4>Sources ${c.grade==='E0'?'· background / provenance':''}</h4><p>${c.citations.map(id=>`<a href="${esc(refs[id].url)}" ${refs[id].url.startsWith('http')?'target="_blank" rel="noopener"':''}>[${id}] ${esc(refs[id].authors)} ${refs[id].year}</a>`).join('<br>')}</p>`;
 document.querySelectorAll('.edgegroup').forEach(el=>el.classList.toggle('selected',el.dataset.claim===id));
 if(scroll&&(window.innerWidth<761||inspector.getBoundingClientRect().top<80||inspector.getBoundingClientRect().top>window.innerHeight))inspector.scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth',block:'start'});
}
function showLayer(id){
 const layer=mechanisms.layers.find(l=>l.id===id);if(!layer)return;
 inspector.innerHTML=`<div class="eyebrow">Layer ${layer.number}</div><h3>${esc(layer.title)}</h3><p>${esc(layer.description)}</p><h4>Explore its claims</h4>${layer.claims.map(c=>`<button data-claim="${c}">${esc(byId[c].title)}<br><span class="badge ${byId[c].status}">${pretty(byId[c].status)}</span></button>`).join('')}`;
 document.querySelectorAll('.operator').forEach(el=>el.classList.toggle('selected',el.dataset.layer===id));
}
document.addEventListener('click',e=>{const c=e.target.closest('[data-claim]');if(c){showClaim(c.dataset.claim,true);return}const l=e.target.closest('[data-layer]');if(l)showLayer(l.dataset.layer)});
document.querySelectorAll('.map-graphic [role=button]').forEach(el=>el.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();el.dispatchEvent(new MouseEvent('click',{bubbles:true}));}}));
const filters=[...document.querySelectorAll('[name=evidence-filter]')];
function filter(){const allowed=filters.filter(f=>f.checked).map(f=>f.value);let count=0;document.querySelectorAll('[data-evidence-status]').forEach(el=>el.classList.toggle('is-hidden',!allowed.includes(el.dataset.evidenceStatus)));for(const c of evidence)if(allowed.includes(c.status))count++;document.getElementById('filter-count').textContent=`${count} of ${evidence.length} claims shown. ${allowed.includes('proposed')?'':'Proposed bridges are hidden; the full cascade is not demonstrated.'}`;const current=byId[selected];if(current&&!allowed.includes(current.status)){inspector.innerHTML='<h3>Evidence view updated</h3><p>Select a visible connection to inspect its scope and sources.</p>'}}
filters.forEach(f=>f.addEventListener('change',filter));
document.getElementById('pause-motion').addEventListener('click',e=>{const paused=document.body.classList.toggle('motion-off');e.currentTarget.textContent=paused?'Resume motion':'Pause motion';e.currentTarget.setAttribute('aria-pressed',String(paused));});
const exo=document.getElementById('exo'),endo=document.getElementById('endo');
function rcb(){const a=+exo.value,b=+endo.value,v=Math.log(a/b);document.getElementById('exo-value').textContent=a.toFixed(1);document.getElementById('endo-value').textContent=b.toFixed(1);document.getElementById('rcb-value').textContent=(v>0?'+':'')+v.toFixed(2);document.getElementById('rcb-marker').style.left=(50+v/Math.log(10)*48)+'%';document.getElementById('rcb-interpretation').textContent=Math.abs(v)<.005?'Equal positive gains in this example.':v>0?'The chosen external gain is larger. This example has an exoregulatory bias.':'The chosen internal gain is larger. This example has an endoregulatory bias.';}
exo.addEventListener('input',rcb);endo.addEventListener('input',rcb);document.getElementById('reset-rcb').addEventListener('click',()=>{exo.value=4;endo.value=4;rcb()});rcb();
const stages=[['Early contribution','Multiple channel types contribute in the developing preparation. The drawing is qualitative, with no fitted proportions.'],['Reallocation','Relative contributions and release coupling change with development. Timing depends on preparation and synapse.'],['Later contribution','P/Q-type contribution becomes more prominent at the studied auditory synapse. This is not a universal human maturation endpoint.']];
document.getElementById('stage').addEventListener('input',e=>{const t=+e.target.value;document.getElementById('stage-title').textContent=stages[t][0];document.getElementById('stage-description').textContent=stages[t][1];document.getElementById('stage-cursor').setAttribute('x1',60+t*190);document.getElementById('stage-cursor').setAttribute('x2',60+t*190);});
const dagCopy={integrated:['Parallel paths + candidate hinge','Solid connections show exposure/confounding assumptions; dashed amber paths nominate unproven molecular mediation. Each arrow here is an assumption for study design, not an estimated causal effect.'],confounding:['Confounding-only alternative','Maternal/familial factors and obstetric indication generate associations between delivery and outcome. The delivery-mediated paths are absent.'],bypass:['Hinge-bypass alternative','Endocrine or microbial effects reach outcome without α₂δ mediation. A positive intervention outcome alone cannot distinguish this model from the proposed hinge.']};
document.querySelectorAll('[data-dag]').forEach(b=>b.addEventListener('click',()=>{document.querySelectorAll('[data-dag]').forEach(x=>x.setAttribute('aria-pressed',String(x===b)));document.querySelectorAll('[data-dag-view]').forEach(x=>x.hidden=x.dataset.dagView!==b.dataset.dag);document.getElementById('dag-title').textContent=dagCopy[b.dataset.dag][0];document.getElementById('dag-copy').textContent=dagCopy[b.dataset.dag][1];}));
const search=document.getElementById('bib-search'),topic=document.getElementById('bib-topic');
function bib(){const q=search.value.trim().toLowerCase();let count=0;document.querySelectorAll('#bibliography .bibliography li').forEach(el=>{const c=refs[el.dataset.ref];const show=(topic.value==='all'||c.topic===topic.value)&&JSON.stringify(c).toLowerCase().includes(q);el.hidden=!show;if(show)count++});document.getElementById('bib-count').textContent=`${count} reference${count===1?'':'s'}${count===0?' — try a different term.':''}`;}
search.addEventListener('input',bib);topic.addEventListener('change',bib);bib();
document.getElementById('print-paper').addEventListener('click',()=>window.print());
if(config.repository_url){document.querySelectorAll('[data-github]').forEach(a=>{a.href=config.repository_url;a.textContent='GitHub source'});}
showClaim('C09');filter();
})();
