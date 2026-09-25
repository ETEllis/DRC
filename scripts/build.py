"""Build offline HTML and publication PDF from the canonical manuscript/data."""
from pathlib import Path
import json,re,html,shutil,math,sys
ROOT=Path(__file__).resolve().parents[1]
def read(n):return json.loads((ROOT/'data'/n).read_text())
data={k:read(k+'.json') for k in ['evidence','mechanisms','citations','predictions','config']}
H=html.escape
by={c['id']:c for c in data['evidence']}
pretty={'established':'Established mechanism','supported':'Supported synthesis','proposed':'Proposed mechanism','horizon':'Horizon hypothesis'}
colors={'established':'#7fe0ce','supported':'#8bbdf6','proposed':'#f0bc69','horizon':'#c6a2f1'}
coords={'constitution':(415,70),'birth':(415,205),'microbiome':(185,365),'hinge':(615,365),'network':(615,540),'phenotype':(415,690),'trajectory':(185,855),'environment':(615,855)}
routes=[('M415 115 L415 160',430,141),('M375 250 Q320 285 185 320',205,285),('M455 250 Q540 280 615 320',545,272),('M315 365 L485 365',320,351),('M580 410 L580 495',545,450),('M650 410 L650 495',665,468),('M615 585 Q580 625 450 645',555,620),('M70 410 L70 690 L285 690',77,583),('M370 735 Q305 770 185 810',172,766),('M545 690 Q620 720 615 810',548,753),('M315 855 L485 855',327,842),('M745 855 L795 855 L795 540 L745 540',665,940)]
def arrowhead(d,color):
 nums=[float(x) for x in re.findall(r'-?\d+(?:\.\d+)?',d)];x0,y0,x,y=nums[-4:];dx=x-x0;dy=y-y0;n=math.hypot(dx,dy);ux,uy=dx/n,dy/n;px,py=-uy,ux
 pts=[(x,y),(x-10*ux+4*px,y-10*uy+4*py),(x-10*ux-4*px,y-10*uy-4*py)]
 return '<polygon points="'+' '.join(f'{a:.2f},{b:.2f}' for a,b in pts)+'" fill="'+color+'"/>'
svg=['<svg class="map-graphic" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 830 975" role="group" aria-label="Evidence-graded master causal map">','<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#9fb7d1"/></marker></defs>']
for e,(d,x,y) in zip(data['mechanisms']['edges'],routes):
 c=by[e['claim']];dash='6 6' if c['grade']=='E0' else 'none'
 svg.append(f'<g class="edgegroup" data-claim="{c["id"]}" data-evidence-status="{c["status"]}" role="button" tabindex="0" aria-label="{H(c["title"])}: {pretty[c["status"]]}"><title>{H(c["title"])}</title><path class="edge {c["status"]}" d="{d}" fill="none" stroke="{colors[c["status"]]}" stroke-width="2" stroke-dasharray="{dash}" /><path class="edgehit" d="{d}" fill="none" stroke="transparent" stroke-width="22"/><text class="arrow-label" x="{x}" y="{y}" fill="#bacbe0" font-size="13">{c["id"]}</text></g>')
# Explicit arrowheads also survive the PDF renderer.
for e,(d,x,y) in zip(data['mechanisms']['edges'],routes):
 c=by[e['claim']];svg.append('<g data-evidence-status="'+c['status']+'">'+arrowhead(d,colors[c['status']])+'</g>')
for l in data['mechanisms']['layers']:
 x,y=coords[l['id']]
 svg.append(f'<g class="operator" data-layer="{l["id"]}" role="button" tabindex="0" aria-label="Expand {H(l["title"])}"><rect x="{x-130}" y="{y-45}" width="260" height="90" rx="5" fill="#142237" stroke="#4b6480"/><text x="{x-112}" y="{y-23}" class="num" fill="#80ced4" font-size="12">{l["number"]} / LAYER</text><text x="{x-112}" y="{y+4}" class="title" fill="#eef3ff" font-size="{15 if l['id']=='environment' else 16 if l['id']=='trajectory' else 18}">{H(l["title"])}</text><text x="{x-112}" y="{y+26}" class="sub" fill="#b5c4d8" font-size="13">{H(l["subtitle"])}</text></g>')
svg.append('</svg>');master=''.join(svg)
(ROOT/'assets/master-map.svg').write_text(master)
def dag(mode):
 s=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 700 350" role="img" aria-label="'+mode+' causal assumptions"><defs><marker id="a'+mode+'" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0 L10 5 L0 10z" fill="#8aa4bd"/></marker></defs>']
 boxes={'U':(340,45,'Familial factors / indication'),'D':(110,200,'Birth conditions'),'M':(325,155,'Microbial state'),'B':(325,255,'Endocrine state'),'C':(535,160,'α₂δ–CaV2'),'Y':(590,290,'Outcome')}
 paths=[('M240 45 Q100 45 110 178',False),('M440 45 Q660 50 650 270',False)]
 if mode!='confounding':paths += [('M195 190 L240 160',False),('M195 210 L240 250',False)]
 if mode=='integrated':paths += [('M410 155 L460 160',True),('M410 255 L480 183',True),('M550 182 L580 268',True)]
 if mode=='bypass':paths += [('M410 155 Q550 200 575 268',True),('M410 255 L505 285',True)]
 for d,hyp in paths:s.append(f'<path d="{d}" fill="none" stroke="{"#e6ad57" if hyp else "#90adc6"}" stroke-width="2" stroke-dasharray="{"5 5" if hyp else "none"}" />')
 for k,(x,y,t) in boxes.items():
  if k=='C' and mode!='integrated':continue
  if k in ['M','B'] and mode=='confounding':continue
  w=215 if k=='U' else 170
  s.append(f'<rect x="{x-w/2}" y="{y-23}" width="{w}" height="46" rx="3" fill="#182c43" stroke="#5b708d"/><text x="{x}" y="{y+5}" text-anchor="middle" fill="#eff3ff" font-size="14" font-family="sans-serif">{H(t)}</text>')
 for d,hyp in paths:s.append(arrowhead(d,'#e6ad57' if hyp else '#90adc6'))
 s.append('</svg>');return ''.join(s)
dags={m:dag(m) for m in ['integrated','confounding','bypass']}
for m,s in dags.items():(ROOT/f'assets/dag-{m}.svg').write_text(s)
md=(ROOT/'papers/integrated-paper.md').read_text().split('<!-- GENERATED APPENDICES -->')[0].rstrip()
def slug(s):return re.sub('[^a-z0-9]+','-',s.lower()).strip('-')
def inline(s):
 s=H(s)
 return re.sub(r'\[((?:\d+|P\d+))\]',lambda m:f'<a href="#ref-{m[1]}">[{m[1]}]</a>',s)
def mdhtml(text):
 out=[];toc=[]
 for chunk in re.split(r'\n\s*\n',text.strip()):
  if chunk.startswith('```equation'):out.append('<pre class="equation">'+H(chunk.split('\n',1)[1].rsplit('```',1)[0].strip())+'</pre>')
  elif chunk.startswith('#'):
   for line in chunk.splitlines():
    level=len(line)-len(line.lstrip('#'));title=line[level:].strip();id=slug(title);out.append(f'<h{level} id="paper-{id}">{H(title)}</h{level}>')
    if level==2 and (title[:1].isdigit() or title=='Abstract'):toc.append((id,title))
  else:out.append('<p>'+inline(chunk.replace('\n',' '))+'</p>')
 return ''.join(out),toc
paper,toc=mdhtml(md)
refhtml=''.join(f'<li id="ref-{r["id"]}" data-ref="{r["id"]}"><span class="ref-id">[{r["id"]}] {H(r["authors"])} · {r["year"]}</span><div><a class="bib-title" href="{H(r["url"])}">{H(r["title"])}</a></div><p>{H(r["publication"])}.</p><span class="quiet">{H(r["scope"])}</span></li>' for r in data['citations'])
ledger=''.join(f'<details data-evidence-status="{c["status"]}"><summary><span class="badge {c["status"]}">{c["grade"]} · {c["status"]}</span>{c["id"]} / {H(c["title"])}</summary><p><b>Scope:</b> {H(c["scope"])}.</p><p>{H(c["mechanism"])}</p><p><b>Uncertainty:</b> {H(c["uncertainty"])}</p><p><b>Rival:</b> {H(c["rival"])}</p><p><b>Falsifier:</b> {H(c["falsifier"])}</p><p>Sources: '+', '.join(f'<a href="#ref-{r}">[{r}]</a>' for r in c['citations'])+'</p></details>' for c in data['evidence'])
mobile=''.join(f'<details><summary>{l["number"]} / {H(l["title"])}</summary><p>{H(l["description"])}</p>'+''.join(f'<button data-claim="{c}" data-evidence-status="{by[c]["status"]}">{c} · {H(by[c]["title"])}</button>' for c in l['claims'])+'</details>' for l in data['mechanisms']['layers'])
filters=''.join(f'<label class="filter {s}"><input name="evidence-filter" type="checkbox" value="{s}" checked>{s.capitalize()}</label>' for s in pretty)
predhtml=''.join(f'<article class="prediction"><span class="eyebrow">{p["id"]} / STUDY {p["study"]}</span><h3>{H(p["title"])}</h3><p>{H(p["prediction"])}</p><p class="falsifier"><b>Falsifier:</b> {H(p["falsifier"])}</p></article>' for p in data['predictions'])
template='''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="An evidence-graded research program connecting constitution, perinatal initialization, synaptic development and regulatory coupling. E. T. Ellis."><meta name="color-scheme" content="light"><title>The Developmental Regulatory Cascade — E. T. Ellis</title><link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='5' fill='%230c1929'/%3E%3Cpath d='M7 8h18L7 24h18' fill='none' stroke='%238bd9dc' stroke-width='3'/%3E%3C/svg%3E"><link rel="stylesheet" href="src/style.css"><link rel="stylesheet" href="src/light.css"><script src="src/data.js" defer></script><script src="src/app.js" defer></script></head>
<body><a class="skip" href="#atlas">Skip to theory</a><header class="masthead"><div class="wrap topbar"><a class="brand" href="#atlas"><span>E.T. ELLIS</span> / RESEARCH ATLAS</a><nav aria-label="Primary"><a href="#atlas">The cascade</a><a href="#mechanisms">Mechanisms</a><a href="#experiments">Tests</a><a href="#manuscript">Paper</a><a href="#downloads">Downloads</a></nav></div></header>
<main class="wrap"><div class="intro"><div><p class="eyebrow">INTEGRATED RESEARCH PROGRAM / v1.1 / 25 SEP 2026</p><h1>The developmental<br><em>regulatory cascade.</em></h1><p>From constitutional constraints to the environments in which regulation takes shape.<br>Explore the mechanisms, the missing bridges, and the experiments that can separate them.</p></div><div class="intro-meta"><strong>One architecture.<br>Different levels of certainty.</strong>Hypothesis and research-program manuscript.<br>Not peer reviewed.<br><a href="papers/integrated-paper.pdf">Download the paper ↗</a></div></div>
<noscript><p class="nojs">The full manuscript, evidence ledger, diagrams and downloads remain available below. JavaScript enables connection inspection, filters and the explanatory controls.</p></noscript>
<section id="atlas" class="explore-section" aria-label="Interactive master causal map"><div class="controls"><span class="quiet">Show evidence:</span>@@FILTERS@@<button id="pause-motion" class="btn secondary" aria-pressed="false">Pause motion</button></div><p class="quiet" id="filter-count" role="status"></p><div class="atlas-layout"><div class="map-shell"><div class="map-label"><span>THE MASTER FIELD</span><span>SELECT A LAYER OR CONNECTION</span></div><div class="desktop-map">@@MASTER@@</div><div class="mobile-map">@@MOBILE@@</div><p class="map-note">Solid: evidence within the stated preparation. Dashed: proposed bridge. Dotted: horizon interpretation. The feedback path unfolds across time. Connection IDs resolve to the ledger.</p></div><aside id="inspector" class="inspector" aria-live="polite" aria-atomic="true"><span class="badge proposed">Proposed mechanism · E0</span><h3>The missing bridge</h3><p>Does realistic perinatal variation change α₂δ–CaV2 organization in a way that mediates later network development?</p><p>The complete cascade has not been demonstrated. Select an arrow to inspect its evidence and limits.</p></aside></div></section>
<section id="mechanisms" class="section explore-section"><p class="eyebrow">01 / PARALLEL PATHS</p><h2>Birth is a transition,<br>not a single exposure.</h2><p class="section-lead">Endocrine response and microbial inheritance are distinct routes. Their proposed convergence on the molecular hinge is the central test—not an established result.</p><div class="split"><article class="panel"><span class="badge supported">Human observational evidence</span><h3>Endocrine / physiological route</h3><div class="pathway"><button data-claim="C02">Labor + physiological transition</button><div class="connector"></div><button data-claim="C02">AVP / copeptin response</button><div class="connector proposed"></div><button data-claim="C09">Candidate α₂δ–CaV2 modulation</button></div><p class="quiet">Oxytocin and vasopressin are not interchangeable. A birth-stress study found the AVP response without an OXT response. <a href="#ref-2">[2]</a></p></article><article class="panel"><span class="badge supported">Human transmission evidence</span><h3>Microbial / ecological route</h3><div class="pathway"><button data-claim="C03">Maternal reservoirs + feeding + contacts</button><div class="connector"></div><button data-claim="C03">Strain acquisition / persistence</button><div class="connector proposed"></div><button data-claim="C09">Candidate immune / metabolic mediation</button></div><p class="quiet">Measure what is acquired. Delivery mode alone cannot identify the organism or pathway responsible for an outcome. <a href="#ref-3">[3]</a></p></article></div></section>
<section class="section explore-section"><div class="split"><article><p class="eyebrow">02 / A SPECIFIC PRECLINICAL PATHWAY</p><h2>Microbial signal.<br>Social-reward circuitry.</h2><p class="section-lead">The L. reuteri pathway has mechanistic support in mouse models. Human trials test a smaller claim: whether particular formulations affect particular outcomes.</p><div class="pathway"><button data-claim="C04">L. reuteri intervention</button><div class="connector"></div><button data-claim="C04">Vagal integrity</button><div class="connector"></div><button data-claim="C04">Oxytocin signaling</button><div class="connector"></div><button data-claim="C04">VTA social-interaction plasticity</button><div class="connector"></div><button data-claim="C04">Social behavior in the studied mouse models</button></div><span class="badge established">E3 · Mouse mechanism [4]</span><p class="quiet">A proposed developmental influence on disgust is a separate, unverified branch. <button class="btn secondary" data-claim="C14">Inspect disgust hypothesis</button></p></article><article class="panel"><p class="eyebrow">03 / THE MOLECULAR HINGE</p><h2 style="font-size:2.4rem">A developmental handoff,<br>with boundaries.</h2><p>Channel contributions change in particular synapses. This qualitative diagram illustrates the idea; it contains no fitted biological proportions or human-age scale.</p><svg class="channel-chart" viewBox="0 0 520 240" role="img" aria-label="Qualitative illustration of changing N-type and P/Q-type channel contributions, not measured data"><path d="M45 25V195H480" fill="none" stroke="#627f9e"/><path d="M60 65C150 65 180 145 440 165" fill="none" stroke="#f1bd76" stroke-width="4"/><path d="M60 160C190 160 230 65 440 45" fill="none" stroke="#88d9df" stroke-width="4"/><line id="stage-cursor" x1="60" x2="60" y1="20" y2="195" stroke="#d5e1ee" stroke-dasharray="4 5"/><text x="300" y="35">P/Q-type / CaV2.1</text><text x="310" y="187">N-type / CaV2.2</text><text x="65" y="224">Earlier</text><text x="395" y="224">Later</text></svg><div class="range-row"><label for="stage">Illustrative developmental stage</label><input id="stage" type="range" min="0" max="2" step="1" value="0"></div><div class="chart-state" aria-live="polite"><strong id="stage-title">Early contribution</strong><p id="stage-description">Multiple channel types contribute in the developing preparation. The drawing is qualitative, with no fitted proportions.</p></div><button class="btn secondary" data-claim="C08">Inspect the rat synapse evidence [8]</button><p class="quiet">α₂δ-1 also participates in thrombospondin-dependent synaptogenesis. This function is not simply the channel switch. <a href="#ref-10">[10–12]</a></p></article></div></section>
<section id="closure" class="section explore-section"><p class="eyebrow">04 / THE PROPOSED MEASUREMENT</p><h2>Where does regulation close?</h2><div class="split"><div><p class="section-lead">Regulatory Closure Bias compares positive regulatory gains from external interaction and internally sustained stabilization.</p><pre class="equation">RCB = ln(Gexo / Gendo)
Both gains must be positive and commensurate.</pre><p>Move either gain to see the relationship. These arbitrary values explain the equation; they do not measure a person or estimate a biological trait.</p><p class="quiet">A real protocol must define regulatory error, match conditions, estimate uncertainty and independently validate the index. Zero or negative measured gains require a different analysis.</p></div><article class="panel"><span class="badge horizon">Illustration · unvalidated construct</span><div class="range-row"><label for="exo">External interaction gain <output id="exo-value">4.0</output></label><input id="exo" type="range" min="1" max="10" step="0.1" value="4"></div><div class="range-row"><label for="endo">Internal stabilization gain <output id="endo-value">4.0</output></label><input id="endo" type="range" min="1" max="10" step="0.1" value="4"></div><div class="result" id="rcb-value" role="status">0.00</div><p id="rcb-interpretation" aria-live="polite">Equal positive gains in this example.</p><div class="meter"><span class="marker" id="rcb-marker"></span></div><div class="meter-labels"><span>Endoregulatory bias</span><span>Exoregulatory bias</span></div><button id="reset-rcb" class="btn secondary" style="margin-top:25px">Reset gains</button></article></div></section>
<section id="alternatives" class="section explore-section"><p class="eyebrow">05 / CAUSAL IDENTIFICATION</p><h2>Three explanations.<br>Different experiments.</h2><p class="section-lead">An association between birth conditions and later outcomes cannot tell these models apart. The molecular claim earns support only when mediation survives direct tests.</p><div class="toggle-row" role="group" aria-label="Alternative causal models"><button data-dag="integrated" aria-pressed="true">Candidate hinge</button><button data-dag="confounding" aria-pressed="false">Confounding only</button><button data-dag="bypass" aria-pressed="false">Hinge bypass</button></div><h3 id="dag-title">Parallel paths + candidate hinge</h3><p id="dag-copy">Solid connections show exposure/confounding assumptions; dashed amber paths nominate unproven molecular mediation. Each arrow here is an assumption for study design, not an estimated causal effect.</p>@@DAGS@@<p class="quiet">Condensed DAGs omit some covariates for readability. Section 16 specifies antibiotics, selection, indication and mediator–outcome confounding. Feedback is represented across successive time steps.</p><div class="split"><article class="panel"><span class="badge supported">Counterevidence [19]</span><h3>Adjusted birth-mode associations can be null.</h3><p>NHS II: ASD OR 1.02 (95% CI 0.81–1.29); ADHD OR 1.06 (0.95–1.18). Dimensional hypotheses must be specified in advance, not substituted after an unwanted result.</p></article><article class="panel"><span class="badge supported">Pilot intervention [20]</span><h3>Domain-specific effects do not identify the hinge.</h3><p>The VMT follow-up favored a social-emotional score while total ASQ-3 was not significant. Neither result establishes an α₂δ mediator or a universal developmental benefit.</p></article></div></section>
<section id="predictions" class="section explore-section"><p class="eyebrow">06 / PREDICTIONS THAT CAN FAIL</p><h2>Make the theory vulnerable.</h2><div class="prediction-grid">@@PREDICTIONS@@</div></section>
<section id="experiments" class="section explore-section"><p class="eyebrow">07 / THE MINIMUM DISCRIMINATING PROGRAM</p><h2>Three core studies.<br>One contingent next step.</h2><article class="study"><div class="letter">A</div><div><h3>Test the molecular bridge directly</h3><p>One defined developmental exposure × selective mediator perturbation, plus orthogonal rescue. Measure molecular state before network outcomes; control viability and maturation. This separates an α₂δ-mediated effect from a bypass.</p><span class="badge proposed">First gate for the hinge hypothesis</span></div></article><article class="study"><div class="letter">B</div><div><h3>Measure the trajectory prospectively</h3><p>Mother–infant recruitment before delivery, obstetric indication and exposure timing, maternal reservoirs, repeated strain acquisition, validated endocrine assays and prespecified developmental dimensions. Compare confounding-only and mediation models in a held-out cohort.</p><span class="badge supported">Human longitudinal design · proposed study</span></div></article><article class="study"><div class="letter">C</div><div><h3>Randomize the environment</h3><p>Measure RCB independently, then cross responsive versus internally paced tasks with AI and completion constraints. Score completed, verified artifacts, errors and recovery. This tests environmental coupling independently of the perinatal model.</p><span class="badge horizon">Independent test of regulatory fit</span></div></article><article class="study"><div class="letter">D</div><div><h3>Replicate an intervention only when justified</h3><p>A preregistered microbial trial with screened procedures, explicit safety monitoring, measured mediators and longer follow-up. Randomization does not make a post-treatment comparison of engrafters and non-engrafters automatically causal.</p><span class="badge proposed">Contingent extension</span></div></article></section>
<section id="ledger" class="section explore-section"><p class="eyebrow">08 / THE CLAIM REGISTER</p><h2>Every bridge has a status.</h2><p class="section-lead">E0 conceptual · E1 observational · E2 replicated observational / task synthesis · E3 animal/cell experiment · E4 human intervention · E5 replicated human causal evidence. These describe designs, not probabilities of truth.</p><div class="ledger">@@LEDGER@@</div></section>
<section id="downloads" class="section downloads-section"><p class="eyebrow">09 / THE PUBLICATION COLLECTION</p><h2>Read the synthesis.<br>Keep the provenance.</h2><div class="downloads"><article class="download-card"><span class="eyebrow">INTEGRATED MANUSCRIPT / v1.1</span><h3>The Developmental Regulatory Cascade</h3><p>Formal synthesis, causal architecture, evidence ledger and discriminating experiments.</p><a class="btn" href="papers/integrated-paper.pdf" download>Download PDF ↓</a></article><article class="download-card"><span class="eyebrow">CANONICAL SOURCE / v3.2</span><h3>RCCX–Hunter–Dąbrowski Cascade</h3><p>The original visual atlas, preserved as supplied.</p><a class="btn secondary" href="papers/rccx-hunter-dabrowski-v3.2.pdf" download>Download atlas ↓</a></article><article class="download-card"><span class="eyebrow">CANONICAL SOURCE / v0.1</span><h3>The Polymathic Singularity</h3><p>The environmental and human–AI coupling framework, preserved as supplied.</p><a class="btn secondary" href="papers/polymathic-singularity-v0.1.pdf" download>Download paper ↓</a></article></div><p class="quiet" style="margin-top:20px"><a href="papers/perinatal-extension-source.md" download>Perinatal extension source</a> · <a href="papers/integrated-paper.md" download>Editable manuscript</a> · <a href="papers/latex/main.tex" download>LaTeX source</a> · <a href="https://github.com/ETEllis/DRC/archive/refs/heads/main.zip">Complete repository source</a></p></section>
<section id="manuscript" class="section"><div class="interactive-only"><p class="eyebrow">10 / FULL MANUSCRIPT</p><button class="btn secondary" id="print-paper">Print / save a reading copy</button></div><div class="paper-layout"><nav class="paper-toc" aria-label="Manuscript sections">@@TOC@@</nav><article class="paper-body">@@PAPER@@<div class="print-only"><h2>Figure 1. Evidence-graded master field</h2>@@MASTER@@<h2>Figure 2. Candidate causal architecture</h2>@@DAGSTATIC@@</div><div class="print-ledger ledger"><h2>Evidence ledger</h2>@@LEDGER@@</div><div class="print-refs"><h2>Scholarly bibliography</h2><ol class="bibliography">@@REFS@@</ol></div></article></div></section>
<section id="bibliography" class="section bibliography-section"><p class="eyebrow">11 / BIBLIOGRAPHY EXPLORER</p><h2>Follow the evidence.</h2><div class="bib-controls"><label class="skip" for="bib-search">Search bibliography</label><input id="bib-search" type="search" placeholder="Search author, mechanism, year…" aria-label="Search bibliography"><select id="bib-topic" aria-label="Filter bibliography by topic"><option value="all">All topics</option>@@TOPICS@@</select></div><p id="bib-count" class="quiet" role="status"></p><ol class="bibliography">@@REFS@@</ol></section>
</main><footer class="wrap footer"><div>E. T. Ellis · Integrated v1.1 · 25 September 2026<br>Hypothesis and research program. Not a diagnostic or treatment tool.</div><div><a data-github href="https://github.com/ETEllis">Author on GitHub ↗</a><a href="https://github.com/ETEllis/DRC/archive/refs/heads/main.zip">Source archive ↓</a><a href="README.md">Repository notes</a></div></footer></body></html>'''
replace={'FILTERS':filters,'MASTER':master,'MOBILE':mobile,'DAGS':''.join(f'<div class="dag" data-dag-view="{m}" {"hidden" if m!="integrated" else ""}>{s}</div>' for m,s in dags.items()),'DAGSTATIC':dags['integrated'],'PREDICTIONS':predhtml,'LEDGER':ledger,'REFS':refhtml,'TOC':''.join(f'<a href="#paper-{id}">{H(t)}</a>' for id,t in toc),'PAPER':paper,'TOPICS':''.join(f'<option value="{t}">{t.capitalize()}</option>' for t in sorted(set(r['topic'] for r in data['citations'])))}
loop_claims=['C21','C22','C23','C24','C25','C26']
loop_cards=''.join(f'<button class="loop-claim" data-claim="{id}"><span class="badge {by[id]["status"]}">{by[id]["grade"]} · {pretty[by[id]["status"]]}</span><strong>{H(by[id]["title"])}</strong><small>{H(by[id]["scope"])}</small></button>' for id in loop_claims)
loop_section='<section id="recursion" class="section explore-section"><p class="eyebrow">LIFE-COURSE FEEDBACK / A SECOND SCALE</p><h2>Development keeps moving.</h2><p class="section-lead">Early conditions may matter, but current physiology, attention, action and social response continue to change one another. The arrows below cross time; they do not form a same-moment causal cycle.</p><div class="loop-track"><div><span>t</span><strong>State & attention</strong><small>sleep · stress · reward</small></div><b aria-hidden="true">→</b><div><span>t</span><strong>Action & adaptation</strong><small>sampling · masking · work</small></div><b aria-hidden="true">→</b><div><span>t+1</span><strong>Selected environment</strong><small>feedback · tools · support</small></div><b aria-hidden="true">→</b><div><span>t+1</span><strong>Updated regulation</strong><small>multiple trajectories</small></div></div><p class="quiet">Each arrow represents C15 · proposed mechanism · E0 conceptual, across time rather than within one instant. <button class="inline-claim" data-claim="C15">Inspect that feedback claim</button> Select a bounded observation below to inspect its sources and rival explanation.</p><div class="loop-claims">'+loop_cards+'</div></section>'
template=template.replace('<section id="closure"',loop_section+'<section id="closure"')
template=template.replace('<section class="section explore-section"><div class="split"><article><p class="eyebrow">02 / A SPECIFIC PRECLINICAL PATHWAY', '<section id="social" class="section explore-section"><div class="split"><article><p class="eyebrow">02 / A SPECIFIC PRECLINICAL PATHWAY')
template=template.replace('<article class="panel"><p class="eyebrow">03 / THE MOLECULAR HINGE', '<article id="channel" class="panel"><p class="eyebrow">03 / THE MOLECULAR HINGE')
chapters=[('atlas','Master field'),('mechanisms','Birth pathways'),('social','Social signaling'),('channel','Channel handoff'),('recursion','Across time'),('closure','Regulatory closure'),('alternatives','Competing DAGs'),('predictions','Predictions'),('experiments','Studies'),('ledger','Claim ledger'),('downloads','Downloads'),('manuscript','Full paper'),('bibliography','Bibliography')]
contents='<details class="contents-menu"><summary>Contents <span aria-hidden="true">▾</span></summary><nav aria-label="All research sections">'+''.join(f'<a href="#{key}">{label}</a>' for key,label in chapters)+'</nav></details>'
template=template.replace('</nav></div></header>','</nav>'+contents+'</div></header>',1)

template=template.replace('<a href="#mechanisms">Mechanisms</a>','<a href="#mechanisms">Mechanisms</a><a href="#recursion">Across time</a>')
for k,v in replace.items():template=template.replace('@@'+k+'@@',v)
# Print-only references must not duplicate interactive IDs.
first=template.index('<div class="print-refs">');last=template.index('</article>',first)
template=template[:first]+template[first:last].replace('id="ref-','id="print-ref-')+template[last:]
printstart=template.index('<div class="print-only">');printend=template.index('</article>',printstart)
template=template[:printstart]+template[printstart:printend].replace('id="arrow"','id="print-arrow"').replace('url(#arrow)','url(#print-arrow)').replace('id="aintegrated"','id="print-aintegrated"').replace('url(#aintegrated)','url(#print-aintegrated)').replace('<details ', '<details open ')+template[printend:]
(ROOT/'index.html').write_text(template)
(ROOT/'src/data.js').write_text('window.RESEARCH_DATA = '+json.dumps(data,ensure_ascii=False).replace('</','<\\/')+';\n')

def explicit_dashes(d):
 # MuPDF's SVG importer omits dash patterns; segment them for exact PDF meaning.
 toks=re.findall(r'[MLQ]|-?\d+(?:\.\d+)?',d);i=0;pts=[];current=(0.,0.)
 while i<len(toks):
  op=toks[i];i+=1
  if op=='M':current=(float(toks[i]),float(toks[i+1]));i+=2;pts.append(current)
  elif op=='L':
   end=(float(toks[i]),float(toks[i+1]));i+=2;steps=max(1,int(math.dist(current,end)))
   pts.extend([(current[0]+(end[0]-current[0])*k/steps,current[1]+(end[1]-current[1])*k/steps) for k in range(1,steps+1)]);current=end
  elif op=='Q':
   c=(float(toks[i]),float(toks[i+1]));end=(float(toks[i+2]),float(toks[i+3]));i+=4;steps=max(1,int(math.dist(current,c)+math.dist(c,end)))
   pts.extend([((1-k/steps)**2*current[0]+2*(1-k/steps)*(k/steps)*c[0]+(k/steps)**2*end[0],(1-k/steps)**2*current[1]+2*(1-k/steps)*(k/steps)*c[1]+(k/steps)**2*end[1]) for k in range(1,steps+1)]);current=end
 out=[];distance=0
 for a,b in zip(pts,pts[1:]):
  distance+=math.dist(a,b)
  if int(distance/6)%2==0:out.append(f'M{a[0]:.2f} {a[1]:.2f}L{b[0]:.2f} {b[1]:.2f}')
 return ' '.join(out)
def make_pdf():
 def PDFH(value):return H(value).replace("₂","<sub>2</sub>").replace("₀","<sub>0</sub>").replace("₁","<sub>1</sub>")
 from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,PageBreak,Image,KeepTogether
 from reportlab.lib.styles import ParagraphStyle
 from reportlab.lib.colors import HexColor
 from reportlab.pdfbase import pdfmetrics
 from reportlab.pdfbase.ttfonts import TTFont
 import pymupdf
 fontdir=Path('/usr/share/fonts/truetype/dejavu')
 fonts=[('Body','DejaVuSerif.ttf'),('BodyBold','DejaVuSerif-Bold.ttf'),('Sans','DejaVuSans.ttf'),('SansBold','DejaVuSans-Bold.ttf')] if fontdir.exists() else [('Body','Georgia.ttf'),('BodyBold','Georgia Bold.ttf'),('Sans','Arial.ttf'),('SansBold','Arial Bold.ttf')]
 if not fontdir.exists():fontdir=Path('/System/Library/Fonts/Supplemental')
 for name,file in fonts:pdfmetrics.registerFont(TTFont(name,str(fontdir/file)))
 pdfmetrics.registerFontFamily('Body',normal='Body',bold='BodyBold',italic='Body',boldItalic='BodyBold')
 pdfmetrics.registerFontFamily('Sans',normal='Sans',bold='SansBold',italic='Sans',boldItalic='SansBold')
 body=ParagraphStyle('body',fontName='Body',fontSize=10.1,leading=15.1,spaceAfter=10,textColor=HexColor('#182c42'))
 styles={1:ParagraphStyle('title',fontName='Body',fontSize=29,leading=34,spaceAfter=18,textColor=HexColor('#102a40')),2:ParagraphStyle('h2',fontName='SansBold',fontSize=14,leading=19,spaceBefore=18,spaceAfter=9,keepWithNext=True,textColor=HexColor('#15364c'))}
 small=ParagraphStyle('small',parent=body,fontName='Sans',fontSize=8.2,leading=12,spaceAfter=9)
 eq=ParagraphStyle('eq',parent=body,fontName='Sans',fontSize=9.5,leading=17,backColor=HexColor('#edf5f7'),borderPadding=12,spaceBefore=10,spaceAfter=16)
 story=[]
 def fig(name,width=480):
  svgtext=(ROOT/'assets'/name).read_text();svgtext=re.sub(r'<path class="edgehit"[^>]+/>','',svgtext);svgtext=re.sub(r'<path[^>]+stroke-dasharray="(?:6 6|5 5)"[^>]*/>',lambda m:re.sub(r'd="([^"]+)"',lambda q:'d="'+explicit_dashes(q[1])+'"',m[0]),svgtext);doc=pymupdf.open(stream=svgtext.encode(),filetype='svg');pdf=pymupdf.open('pdf',doc.convert_to_pdf());page=pdf[0];pix=page.get_pixmap(matrix=pymupdf.Matrix(2,2),alpha=True);out=ROOT/'assets'/name.replace('.svg','.png');pix.save(out)
  # Dark background preserves semantic color coding and legibility.
  from PIL import Image as PI
  im=PI.open(out).convert('RGBA');bg=PI.new('RGBA',im.size,'#0c1625');bg.alpha_composite(im);bg.convert('RGB').save(out)
  w,h=im.size;return Image(str(out),width=width,height=width*h/w)
 for chunk in re.split(r'\n\s*\n',md.strip()):
  if chunk.startswith('```equation'):
   story.append(Paragraph(PDFH(chunk.split('\n',1)[1].rsplit('```',1)[0].strip()).replace('\n','<br/>'),eq));continue
  if chunk.startswith('#'):
   for line in chunk.splitlines():
    level=len(line)-len(line.lstrip('#'));title=line[level:].strip()
    if title=='References':continue
    story.append(Paragraph(PDFH(title),styles.get(level,styles[2])))
   continue
  if chunk.startswith('The complete numbered bibliography'):continue
  story.append(Paragraph(PDFH(chunk.replace('\n',' ')),body))
 story.append(Spacer(1,12));story.append(Paragraph('Figure 1. The master causal field',styles[2]));story.append(Paragraph('Connection IDs resolve to the ledger. Solid lines mark evidence in its stated preparation; dashed lines mark unproven bridges. Feedback summarizes a time-indexed sequence.',small));story.append(fig('master-map.svg',400))
 story.append(PageBreak());story.append(Paragraph('Figure 2. Competing causal architectures',styles[2]))
 for mode,title in [('integrated','A. Parallel paths with a candidate molecular mediator'),('confounding','B. Shared-cause / confounding-only alternative'),('bypass','C. Endocrine or microbial effect without the hinge')]:
  story.append(Paragraph(title,small));story.append(fig('dag-'+mode+'.svg',375));story.append(Spacer(1,8))
 story.append(Paragraph('These condensed DAGs show assumptions, not measured effects. Additional exposure timing, confounding and selection considerations are specified in Section 16.',small))
 story.append(PageBreak());story.append(Paragraph('Appendix A. Evidence-status ledger',styles[2]))
 story.append(Paragraph('Established mechanism ≠ supported synthesis ≠ proposed mechanism ≠ horizon hypothesis. Design codes classify evidence; they do not quantify certainty. For E0 connections, sources supply background or provenance rather than support for the whole arrow.',body))
 for c in data['evidence']:
  start=len(story)
  story.append(Paragraph(c['id']+'. '+PDFH(c['title']),styles[2]));story.append(Paragraph(PDFH(pretty[c['status']]+' · '+c['grade']+' · '+c['scope']),small))
  story.append(Paragraph('<b>Mechanism / claim:</b> '+PDFH(c['mechanism']),body));story.append(Paragraph('<b>Unresolved:</b> '+PDFH(c['uncertainty']),body));story.append(Paragraph('<b>Rival:</b> '+PDFH(c['rival']),body));story.append(Paragraph('<b>Discriminator:</b> '+PDFH(c['falsifier']),body));story.append(Paragraph('Sources: '+', '.join('['+x+']' for x in c['citations']),small))
  parts=story[start:];del story[start:];story.append(KeepTogether(parts))
 story.append(PageBreak());story.append(Paragraph('References',styles[2]))
 for r in data['citations']:
  link=f'<br/><link href="{PDFH(r["url"])}" color="#1b6175">{PDFH(r["url"])}</link>' if r['url'].startswith('http') else '<br/>Included in the source collection: '+PDFH(r['url'])
  story.append(Paragraph(f'[{r["id"]}] {PDFH(r["authors"])} ({r["year"]}). {PDFH(r["title"])}. {PDFH(r["publication"])}.'+link,small))
 def footer(c,doc):
  c.setStrokeColor(HexColor('#afbfcb'));c.line(52,42,543,42);c.setFont('Sans',7.5);c.setFillColor(HexColor('#465e74'));c.drawString(52,29,'E. T. Ellis · Developmental Regulatory Cascade · v1.1 · 25 Sep 2026');c.drawRightString(543,29,str(doc.page))
 doc=SimpleDocTemplate(str(ROOT/'papers/integrated-paper.pdf'),pagesize=(595.28,841.89),rightMargin=52,leftMargin=52,topMargin=49,bottomMargin=59,title='The Developmental Regulatory Cascade',author='E. T. Ellis',subject='Integrated hypothesis and research-program manuscript')
 doc.build(story,onFirstPage=footer,onLaterPages=footer)
 print('Built manuscript PDF.')
if "--legacy-pdf" in sys.argv:make_pdf()
print('Built static HTML, shared data bundle and diagrams.')

# The downloadable Markdown includes its complete bibliography and claim appendix.
refsmd='\n\n'.join(f'[{r["id"]}] {r["authors"]} ({r["year"]}). {r["title"]}. {r["publication"]}. {r["url"]}' for r in data['citations'])
ledgermd='\n\n'.join(f'### {c["id"]}: {c["title"]}\n\n{pretty[c["status"]]} · {c["grade"]} · {c["scope"]}\n\n{c["mechanism"]}\n\nUncertainty: {c["uncertainty"]}\n\nFalsifier: {c["falsifier"]}\n\nSources: '+', '.join('['+r+']' for r in c['citations']) for c in data['evidence'])
(ROOT/'papers/integrated-paper.md').write_text(md+'\n\n<!-- GENERATED APPENDICES -->\n\n'+refsmd+'\n\n## Appendix A. Evidence ledger\n\n'+ledgermd+'\n')
