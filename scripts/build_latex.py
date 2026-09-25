#!/usr/bin/env python3
"""Generate and compile the conventional two-column LaTeX edition."""
from __future__ import annotations
import json, re, shutil, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "papers/latex"
PARTS = OUT / "sections"
PARTS.mkdir(parents=True, exist_ok=True)
paper = (ROOT / "papers/integrated-paper.md").read_text().split("<!-- GENERATED APPENDICES -->")[0]
refs = json.loads((ROOT / "data/citations.json").read_text())
claims = json.loads((ROOT / "data/evidence.json").read_text())
FENCE = chr(96) * 3

def escape(s: str) -> str:
    s = s.replace("\\", r"\textbackslash{}")
    for a,b in [("&",r"\&"),("%",r"\%"),("_",r"\_"),("#",r"\#"),("$",r"\$"),("{",r"\{"),("}",r"\}")]:
        s = s.replace(a,b)
    for a,b in [("α₂δ",r"\ensuremath{\alpha_2\delta}"),("α2δ",r"\ensuremath{\alpha_2\delta}"),
                ("→",r"\ensuremath{\rightarrow}"),("↔",r"\ensuremath{\leftrightarrow}"),
                ("×",r"\ensuremath{\times}"),("κ",r"\ensuremath{\kappa}"),("α",r"\ensuremath{\alpha}"),("β",r"\ensuremath{\beta}"),("δ",r"\ensuremath{\delta}"),("₁",r"\textsubscript{1}"),("₀",r"\textsubscript{0}"),("₂",r"\textsubscript{2}")]:
        s = s.replace(a,b)
    return s.replace("L. reuteri",r"\emph{L. reuteri}")

def key(ref: str) -> str:
    return ("proj" + ref) if ref.startswith("P") else ("ref" + ref)

citation_re = re.compile(r"\[([0-9P,\s–-]+)\]")
def inline(s: str) -> str:
    out=[]; pos=0
    for m in citation_re.finditer(s):
        out.append(escape(s[pos:m.start()]))
        ids=[]
        for part in m[1].split(","):
            part=part.strip()
            if re.fullmatch(r"\d+[–-]\d+",part):
                lo,hi=map(int,re.split("[–-]",part));ids.extend(str(i) for i in range(lo,hi+1))
            elif re.fullmatch(r"P\d+[–-]P\d+",part):
                lo,hi=map(lambda x:int(x[1:]),re.split("[–-]",part));ids.extend(f"P{i}" for i in range(lo,hi+1))
            else: ids.append(part)
        if not all(re.fullmatch(r"(?:\d+|P\d+)",i) for i in ids): raise ValueError(m[0])
        out.append(r"\cite{"+",".join(key(i) for i in ids)+"}")
        pos=m.end()
    out.append(escape(s[pos:]))
    return "".join(out)

def paragraphs(s: str) -> str:
    out=[]
    for block in re.split(r"\n\s*\n",s.strip()):
        if block.startswith(FENCE+"equation"):
            if "RCB(" in block:
                out.append(r"""\begin{equation}
\mathrm{RCB}_{i,\tau,s}=\ln\!\left(\frac{G_{\mathrm{exo}}}{G_{\mathrm{endo}}}\right),
\qquad G_{\mathrm{exo}},G_{\mathrm{endo}}>0 .
\end{equation}""")
            else:
                out.append(r"""\begin{align}
P_0 &= F(G,B_0,M_0,I_0,A_0,U_P),\\
C_{t+1} &= f_C(C_t,P_0,N_t,\nonumber\\
&\qquad I_t,E_t,U_C),\\
N_{t+1} &= f_N(N_t,C_t,E_t,A_t,U_N),\\
R_{t+1} &= f_R(R_t,N_t,\nonumber\\
&\qquad \mathrm{body}_t,E_t,U_R),\\
E_{t+1} &= f_E(E_t,R_t,\nonumber\\
&\qquad \mathrm{action}_t,\mathrm{institutions}_t,U_E).
\end{align}""")
        elif block.startswith("#"): raise ValueError(block[:80])
        else: out.append(inline(" ".join(block.splitlines())))
    return "\n\n".join(out)+"\n"

head=re.compile(r"^## (\d+)\. (.+)$",re.M)
matches=list(head.finditer(paper));assert len(matches)==24
abstract=paper[paper.index("## Abstract")+len("## Abstract"):matches[0].start()].strip()
abstract_text,keywords=abstract.rsplit("\n\nKeywords:",1)
sections={}
for j,m in enumerate(matches):
    end=matches[j+1].start() if j+1<len(matches) else paper.index("## References",m.end())
    sections[int(m[1])]=(m[2],paper[m.end():end].strip())
groups=[
 ("01-introduction","Introduction",[1,2,3]),
 ("02-architecture","Causal architecture",[4]),
 ("03-perinatal","Perinatal pathways",[5,6,7,8]),
 ("04-molecular","Molecular and constitutional mechanisms",[9,10,11]),
 ("05-regulation","Regulatory phenotype and context",[12,13,14,15]),
 ("06-identification","Causal identification and human evidence",[16,17]),
 ("07-tests","Predictions and discriminating studies",[18,19,20]),
 ("08-discussion","Discussion and limitations",[21,22]),
 ("09-conclusion","Conclusion",[23]),
 ("10-declarations","Declarations and provenance",[24])]
for fname,title,numbers in groups:
    content=[(r"\section*{" if fname=="10-declarations" else r"\section{")+escape(title)+"}"]
    for num in numbers:
        heading,body=sections[num]
        if len(numbers)>1 and num!=1:content.append(r"\subsection{"+escape(heading)+"}")
        content.append(paragraphs(body.replace("Section 16","the causal-identification section")))
    if fname=="02-architecture":
        content.append(r"""\begin{figure*}[t]
\centering
\includegraphics[height=5.6in,keepaspectratio]{../../assets/master-map.png}
\caption{Evidence-graded master field. Solid links concern bounded evidence; dashed links mark proposed bridges or horizon claims. Connection IDs resolve to the claim ledger. Feedback is indexed across time.}
\label{fig:master}
\end{figure*}""")
    if fname=="06-identification":
        content.append(r"""\begin{figure*}[t]
\centering
\begin{minipage}{.48\textwidth}\centering
\includegraphics[width=\linewidth]{../../assets/dag-integrated.png}\\
\small (a) Candidate mediator
\end{minipage}\hfill
\begin{minipage}{.48\textwidth}\centering
\includegraphics[width=\linewidth]{../../assets/dag-confounding.png}\\
\small (b) Confounding-only alternative
\end{minipage}\\[.8em]
\begin{minipage}{.48\textwidth}\centering
\includegraphics[width=\linewidth]{../../assets/dag-bypass.png}\\
\small (c) Hinge-bypass alternative
\end{minipage}
\caption{Competing causal architectures. The same outcome can arise with or without the candidate molecular mediator; these are study assumptions, not fitted effects.}
\label{fig:alternatives}
\end{figure*}""")
    (PARTS/(fname+".tex")).write_text("\n\n".join(content).rstrip()+"\n")
bib=[r"\begin{thebibliography}{99}",r"\small"]
bibtex=[]
for ref in refs:
    rid=key(ref["id"]);url=ref["url"]
    if not url.startswith("https://"):url="https://github.com/ETEllis/DRC/blob/main/"+url
    label=("doi:"+url.rsplit("/",1)[1]) if "doi.org/" in url else (("PMID:"+url.rstrip("/").rsplit("/",1)[1]) if "pubmed.ncbi.nlm.nih.gov/" in url else "source file")
    bib.append(r"\bibitem{"+rid+"} "+escape(ref["authors"])+" ("+str(ref["year"])+"). "+escape(ref["title"])+". "+escape(ref["publication"])+". "+r"\href{"+url+"}{"+escape(label)+"}")
    bibtex.append("@misc{"+rid+",\n  author={"+ref["authors"].replace("{","").replace("}","")+"},\n  title={"+ref["title"].replace("{","").replace("}","")+"},\n  year={"+str(ref["year"])+"},\n  howpublished={"+ref["publication"].replace("{","").replace("}","")+"},\n  url={"+url+"}\n}\n")
bib.append(r"\end{thebibliography}")
(OUT/"references.tex").write_text("\n\n".join(bib)+"\n")
(OUT/"references.bib").write_text("\n".join(bibtex))
ledger=[r"\appendix",r"\section{Claim-level evidence ledger}",
        "Status and design code are separate. An E0 citation supplies background or provenance without establishing the whole bridge."]
for claim in claims:
    ledger.append(r"\subsection*{"+escape(claim["id"]+" · "+claim["title"])+"}")
    ledger.append(r"\noindent\textbf{"+escape(claim["status"].title()+" · "+claim["grade"]+" · "+claim["scope"])+r"}\par")
    for label,field in [("Claim","mechanism"),("Limit","uncertainty"),("Rival","rival"),("Discriminator","falsifier")]:
        ledger.append(r"\textit{"+label+r".} "+inline(claim[field])+r"\par")
    ledger.append(r"\textit{Sources.} \cite{"+",".join(key(i) for i in claim["citations"])+r"}\par")
(OUT/"claim-ledger.tex").write_text("\n".join(ledger)+"\n")
template=r"""\documentclass[10pt,letterpaper,twocolumn]{article}
\usepackage[letterpaper,top=.72in,bottom=.72in,left=.68in,right=.68in,columnsep=.25in]{geometry}
\usepackage{fontspec}
\setmainfont{lmroman10-regular.otf}[BoldFont=lmroman10-bold.otf,ItalicFont=lmroman10-italic.otf,BoldItalicFont=lmroman10-bolditalic.otf]
\setsansfont{lmsans10-regular.otf}[BoldFont=lmsans10-bold.otf]
\usepackage{amsmath,amssymb,graphicx,microtype}
\usepackage[font=small,labelfont=bf]{caption}
\usepackage[hidelinks]{hyperref}
\usepackage{xcolor}
\definecolor{linktone}{HTML}{245C55}
\hypersetup{colorlinks=true,linkcolor=linktone,citecolor=linktone,urlcolor=linktone,
pdftitle={The Developmental Regulatory Cascade},pdfauthor={E. T. Ellis}}
\setlength{\parindent}{1em}
\setlength{\parskip}{0pt}
\emergencystretch=1em
\raggedbottom
\begin{document}
\twocolumn[{
\begin{center}
{\small\sffamily\bfseries RESEARCH ARTICLE}\\[.7em]
{\huge\bfseries The Developmental Regulatory Cascade}\\[.6em]
{\large Constitution, perinatal initialization, and the \ensuremath{\alpha_2\delta}--CaV2 hinge in a coupled organism--environment research program}\\[1em]
{\normalsize E. T. Ellis}\\
{\small Independent researcher \quad \textbullet \quad 25 September 2026}\\[.45em]
{\small Working hypothesis manuscript v1.1 \quad \textbullet \quad Not peer reviewed}
\end{center}
\vspace{.25em}
\begin{center}
\begin{minipage}{.86\textwidth}
\begin{center}\normalsize\sffamily\bfseries Abstract\end{center}
\vspace{.1em}
\small @@ABSTRACT@@

\vspace{.55em}
\noindent\textbf{Keywords:} @@KEYWORDS@@
\end{minipage}
\end{center}
\vspace{1em}
}]
@@INPUTS@@
\input{claim-ledger}
\input{references}
\end{document}
"""
inputs="\n".join(r"\input{sections/"+g[0]+"}" for g in groups)
main=template.replace("@@ABSTRACT@@",inline(abstract_text.replace("\n"," "))).replace("@@KEYWORDS@@",escape(keywords.strip())).replace("@@INPUTS@@",inputs)
(OUT/"main.tex").write_text(main)
print(f"Generated 10 LaTeX sections, {len(refs)} references, {len(claims)} ledger entries.")
subprocess.run(["tectonic","main.tex","--outdir","."],cwd=OUT,check=True)
shutil.copyfile(OUT/"main.pdf",ROOT/"papers/integrated-paper.pdf")
(OUT/"main.pdf").unlink()
print("Compiled the two-column academic PDF.")
