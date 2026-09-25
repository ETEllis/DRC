const ns = 'http://www.w3.org/2000/svg';
const gradeColors = {A:'#94c5b5', B:'#c9d58b', C:'#e4a371', D:'#b6a1b8'};
const positions = {
  constitution:[42,101], perinatal:[42,310], channel:[262,310], stress:[472,122], attention:[472,353],
  environment:[684,122], adaptation:[684,353], coherence:[865,85], conversion:[865,288], output:[865,485]
};
const nodeWidth = 146, nodeHeight = 63;
let model, sources, activeGrade = 'all', selectedEdge = null;

function el(name, attrs = {}, text) {
  const x = document.createElementNS(ns, name);
  for (const [key,value] of Object.entries(attrs)) x.setAttribute(key, value);
  if (text !== undefined) x.textContent = text;
  return x;
}
function htmlEscape(value) {
  return String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}
function edgePath(edge) {
  const [sx,sy]=positions[edge.from], [tx,ty]=positions[edge.to];
  const backward = tx <= sx;
  let x1=sx+nodeWidth, y1=sy+nodeHeight/2, x2=tx, y2=ty+nodeHeight/2;
  if (backward) {
    x1=sx+nodeWidth/2; y1=sy+nodeHeight;
    x2=tx+nodeWidth/2; y2=ty+nodeHeight;
    const depth=Math.max(y1,y2)+55+(edge.id==='E16'?30:0);
    return `M${x1},${y1} C${x1},${depth} ${x2},${depth} ${x2},${y2}`;
  }
  const pull=Math.max(48,(x2-x1)*.45);
  return `M${x1},${y1} C${x1+pull},${y1} ${x2-pull},${y2} ${x2},${y2}`;
}
function drawGraph() {
  const svg=document.querySelector('#graph'); svg.replaceChildren();
  const defs=el('defs');
  Object.entries(gradeColors).forEach(([grade,color])=>{
    const marker=el('marker',{id:`arrow-${grade}`,viewBox:'0 0 10 10',refX:'9',refY:'5',markerWidth:'6',markerHeight:'6',orient:'auto-start-reverse'});
    marker.append(el('path',{d:'M 0 0 L 10 5 L 0 10 z',fill:color})); defs.append(marker);
  }); svg.append(defs);
  const lanes=[['01 / INITIAL',42],['02 / MOLECULAR',262],['03 / REGULATORY',472],['04 / CONTEXT',684],['05 / OUTCOME',865]];
  lanes.forEach(([label,x])=>{svg.append(el('text',{x,y:43,class:'lane-label'},label));svg.append(el('line',{x1:x,y1:52,x2:x+150,y2:52,class:'lane-line'}));});
  model.edges.forEach(edge=>{
    const dim=activeGrade!=='all'&&edge.grade!==activeGrade;
    const path=el('path',{d:edgePath(edge),class:`edge ${['E09','E10','E11','E16'].includes(edge.id)?'feedback':''} ${dim?'dimmed':''} ${selectedEdge===edge.id?'selected':''}`,stroke:gradeColors[edge.grade],'marker-end':`url(#arrow-${edge.grade})`});
    const hit=el('path',{d:edgePath(edge),class:'edge-hit',role:'button',tabindex:'0','aria-label':`${edge.id}, grade ${edge.grade}: ${edge.claim}`});
    hit.addEventListener('click',()=>selectEdge(edge.id));hit.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();selectEdge(edge.id);}});
    svg.append(path,hit);
  });
  model.nodes.forEach(node=>{
    const [x,y]=positions[node.id], group=el('g',{class:'node'});
    group.append(el('rect',{x,y,width:nodeWidth,height:nodeHeight}));
    const words=node.label.split(' '); let lines=[];
    if(node.label.length>19){let line='';for(const word of words){if((line+' '+word).trim().length>18){lines.push(line);line=word;}else line=(line+' '+word).trim();}lines.push(line);} else lines=[node.label];
    lines.forEach((line,i)=>group.append(el('text',{x:x+11,y:y+(lines.length===1?36:27)+i*18},line)));
    svg.append(group);
  });
}
function selectEdge(id){
  selectedEdge=id; drawGraph(); renderDetail(); renderEdges();
}
function renderDetail(){
  const edge=model.edges.find(e=>e.id===selectedEdge);
  if(!edge)return;
  const from=model.nodes.find(n=>n.id===edge.from).label,to=model.nodes.find(n=>n.id===edge.to).label;
  const sourceLinks=edge.sources.map(id=>{const s=sources.find(x=>x.id===id);return s?`<a href="${htmlEscape(s.url)}" target="_blank" rel="noopener noreferrer" title="${htmlEscape(s.title)}">${id} ↗</a>`:''}).join('');
  document.querySelector('#edge-detail').innerHTML=`<span class="detail-kicker">${edge.id} / ${htmlEscape(edge.status.toUpperCase())}</span><h3>${htmlEscape(from)} <span aria-hidden="true">→</span> ${htmlEscape(to)}</h3><span class="detail-grade" style="color:${gradeColors[edge.grade]}">GRADE ${edge.grade}</span><p>${htmlEscape(edge.claim)}</p><div class="detail-boundary"><b>TRANSFER BOUNDARY</b><p>${htmlEscape(edge.boundary)}</p></div><div class="detail-rival"><b>RIVAL EXPLANATION</b><p>${htmlEscape(edge.rival)}</p></div><div class="detail-sources">${sourceLinks}</div>`;
}
function renderEdges(){
  const box=document.querySelector('#edge-list');box.replaceChildren();
  model.edges.forEach(edge=>{
    const button=document.createElement('button');button.type='button';button.className=`edge-chip ${selectedEdge===edge.id?'selected':''} ${activeGrade!=='all'&&edge.grade!==activeGrade?'dimmed':''}`;
    const a=model.nodes.find(n=>n.id===edge.from).label,b=model.nodes.find(n=>n.id===edge.to).label;
    button.innerHTML=`<b style="color:${gradeColors[edge.grade]}">${edge.id} · ${edge.grade}</b><span>${htmlEscape(a)} → ${htmlEscape(b)}</span>`;
    button.addEventListener('click',()=>{selectEdge(edge.id);document.querySelector('#edge-detail').scrollIntoView({block:'nearest',behavior:'smooth'});});box.append(button);
  });
  document.querySelector('#model-count').textContent=`${activeGrade==='all'?model.edges.length:model.edges.filter(e=>e.grade===activeGrade).length} / ${model.edges.length} arrows visible`;
}
function renderSources(query=''){
  const list=document.querySelector('#source-list'), filtered=sources.filter(s=>[s.id,s.authors,s.title,s.venue,s.kind,s.supports].join(' ').toLowerCase().includes(query.toLowerCase()));
  list.innerHTML=filtered.map(s=>`<article class="source-item" id="source-${s.id}"><span class="source-id">${s.id}</span><div><h3><a href="${htmlEscape(s.url)}" target="_blank" rel="noopener noreferrer">${htmlEscape(s.title)} ↗</a></h3><div class="meta">${htmlEscape(s.authors)} · ${s.year} · ${htmlEscape(s.kind)}</div><p>${htmlEscape(s.supports)}</p></div></article>`).join('');
  document.querySelector('#source-count').textContent=`${filtered.length} / ${sources.length}`;
}
async function init(){
  try{
    const [m,s]=await Promise.all([fetch('data/model.json'),fetch('data/sources.json')]);
    if(!m.ok||!s.ok)throw new Error('Research data could not be loaded.');
    [model,sources]=await Promise.all([m.json(),s.json()]);
    drawGraph();renderEdges();renderSources();selectEdge('E03');
    document.querySelectorAll('.filter').forEach(button=>button.addEventListener('click',()=>{
      activeGrade=button.dataset.filter;
      document.querySelectorAll('.filter').forEach(b=>{b.classList.toggle('active',b===button);b.setAttribute('aria-pressed',String(b===button));});
      if(activeGrade!=='all'&&model.edges.find(e=>e.id===selectedEdge)?.grade!==activeGrade)selectedEdge=model.edges.find(e=>e.grade===activeGrade)?.id;
      drawGraph();renderEdges();renderDetail();
    }));
    document.querySelector('#source-search').addEventListener('input',e=>renderSources(e.target.value));
    document.querySelectorAll('[data-source]').forEach(a=>a.addEventListener('click',()=>{document.querySelector('#source-search').value=a.dataset.source;renderSources(a.dataset.source);}));
  }catch(error){document.querySelector('#edge-detail').innerHTML=`<h3>Research data unavailable</h3><p>${htmlEscape(error.message)} Reload from a web server or GitHub Pages.</p>`;}
}
init();
