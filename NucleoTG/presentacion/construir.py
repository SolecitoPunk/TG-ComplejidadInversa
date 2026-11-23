"""
construir.py: genera la presentación (16:9) y el guion de la defensa en HTML y los imprime a PDF.

    python construir.py            # escribe presentacion.html, guion.html y, si hay Chromium, los PDF

Solo usa la biblioteca estándar. Los símbolos que faltan en la fuente (∇, √, →, ≈, ≪, ∈) se dibujan
como SVG en línea. La estructura sigue la guía del director (correo del 21 de noviembre de 2026).
"""
import math
import re
import os
import shutil
import subprocess

AQUI = os.path.dirname(os.path.abspath(__file__))
NAVY, TEAL, OCHRE, GRIS = "#0b1a2e", "#0f8a80", "#c8892b", "#5b6676"

# ------------------------------------------------------------------ símbolos
def _svg(vb, w, h, d, sw=1.15, va="-0.08em"):
    return (f'<svg class="s" viewBox="{vb}" style="width:{w}em;height:{h}em;vertical-align:{va}">'
            f'<path d="{d}" fill="none" stroke="currentColor" stroke-width="{sw}" '
            f'stroke-linecap="round" stroke-linejoin="round"/></svg>')

NAB = _svg("0 0 10 11", .68, .78, "M0.9 1.1 H9.1 L5 10 Z")
ARR = _svg("0 0 18 10", 1.15, .62, "M1 5H15.6M11.6 1.6L16 5 11.6 8.4", va="0.02em")
APX = _svg("0 0 14 10", .85, .62, "M1 3.6C3.5 1.2 5.5 1.2 7 3.4S10.5 5.8 13 3.4M1 7.6C3.5 5.2 5.5 5.2 7 7.4S10.5 9.8 13 7.4", 1.05)
LL = _svg("0 0 16 10", .95, .62, "M8 1.6L2 5 8 8.4M14 1.6L8 5 14 8.4")
IN = _svg("0 0 10 10", .62, .62, "M9 1.5H6A3.5 3.5 0 0 0 6 8.5H9M2.6 5H9")
TO = ARR


GE = _svg("0 0 10 10", .62, .62, "M2 1.2L8 4.2 2 7.2M2 9.2H8")
NE = _svg("0 0 10 10", .62, .62, "M1.5 3.6H8.5M1.5 6.6H8.5M7 1L3 9.4")
PAR = _svg("0 0 10 12", .55, .72, "M3 2.2C4.5 .8 8 1.2 8 5.5 8 9.5 5.8 11 4 11 2.2 11 1.4 9.8 1.4 8.4 1.4 6.6 3 5.4 4.8 5.4 6.4 5.4 7.6 6.4 8 7.5", 1.1, "-0.05em")
OINT = ('<svg class="s" viewBox="0 0 10 16" style="width:.55em;height:.95em;vertical-align:-0.22em">'
        '<path d="M7.4 1.6C5.8 .4 4.8 1.8 4.8 4V12C4.8 14.2 3.9 15.6 2.4 14.4" fill="none" stroke="currentColor" stroke-width="1.1" stroke-linecap="round"/>'
        '<circle cx="4.8" cy="8" r="2.3" fill="none" stroke="currentColor" stroke-width="1"/></svg>')
SIM = _svg("0 0 14 10", .8, .62, "M1 5.6C3 2.6 5 2.6 7 5S11 7.6 13 4.6")
PERP = _svg("0 0 10 10", .6, .62, "M5 1.2V8.6M1 8.6H9")
RADG = _svg("0 0 8 10", .5, .66, "M.5 6L2 5.2 3.6 9.5 7.4 .6", 1.0, "-0.1em")
GLIFOS = {"∇": NAB, "√": RADG, "→": ARR, "⟶": ARR, "≈": APX, "≃": APX, "≪": LL, "∈": IN, "≥": GE, "≠": NE,
          "∂": PAR, "∮": OINT, "∼": SIM, "⊥": PERP}


def glifos(html):
    partes = re.split(r"(<svg.*?</svg>|<style>.*?</style>|<script>.*?</script>)", html, flags=re.S)
    for k in range(0, len(partes), 2):
        for c, s in GLIFOS.items():
            partes[k] = partes[k].replace(c, s)
    return "".join(partes)


def sq(x):
    return (f'<span class="sq"><svg class="rad" viewBox="0 0 8 16" preserveAspectRatio="none">'
            f'<path d="M0.4 9.6L2.4 8.4 4.5 15.3 7.7 0.6" fill="none" stroke="currentColor" stroke-width="0.9"/>'
            f'</svg><span class="rc">{x}</span></span>')


def fr(a, b):
    return f'<span class="fr"><span>{a}</span><span>{b}</span></span>'


def v(x):  # vector en negrita
    return f"<b>{x}</b>"


# expresiones frecuentes
HB = "ℏ"
U, J, A, B, R = v("u"), v("j"), v("A"), v("B"), v("r")
W0, WC = "ω<sub>0</sub>", "ω<sub>c</sub>"
BZ = "<i>B</i><sub><i>z</i></sub>"
P_, S_, V_, E_, m_, q_ = "<i>P</i>", "<i>S</i>", "<i>V</i>", "<i>E</i>", "<i>m</i>", "<i>q</i>"
MAESTRA = (f"{V_} − {E_} = {fr(HB+'²', '2'+m_)}{fr(NAB+'²'+sq(P_), sq(P_))} − {fr('|'+U+'|²', '2'+m_)}")

# ------------------------------------------------------------------ figuras
def fig_laboratorio():
    return f"""
<svg viewBox="0 0 760 300" class="fig" style="height:3.05in;width:auto;margin:0 auto">
 <defs><marker id="ah" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
  <path d="M0,0 L6,3 L0,6 Z" fill="{TEAL}"/></marker>
  <marker id="ahg" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
  <path d="M0,0 L6,3 L0,6 Z" fill="{GRIS}"/></marker></defs>
 <rect x="4" y="10" width="752" height="250" rx="16" fill="#f1f5f7"/>
 <!-- observador -->
 <circle cx="70" cy="80" r="15" fill="none" stroke="{GRIS}" stroke-width="2.5"/>
 <path d="M70 95 L70 160 M70 112 L105 128 M70 160 L50 215 M70 160 L92 215 M40 165 L105 165" stroke="{GRIS}" stroke-width="2.5" fill="none"/>
 <rect x="108" y="112" width="62" height="42" rx="4" fill="#e3edf0" stroke="{GRIS}" stroke-width="2"/>
 <path d="M114 138 C124 122 132 150 142 134 S158 124 164 132" stroke="{TEAL}" stroke-width="2" fill="none"/>
 <text x="98" y="243" class="ft" text-anchor="middle">Observador y control</text>
 <line x1="176" y1="132" x2="250" y2="132" stroke="{TEAL}" stroke-width="2.2" marker-end="url(#ah)"/>
 <text x="213" y="122" class="fs" text-anchor="middle">señales</text>
 <!-- criostato -->
 <rect x="258" y="58" width="170" height="150" rx="16" fill="#d9dee3" stroke="{GRIS}" stroke-width="2"/>
 <rect x="282" y="80" width="122" height="106" rx="12" fill="#fff" stroke="{NAVY}" stroke-width="2"/>
 <path d="M296 112 C296 92 390 92 390 112 M296 160 C296 182 390 182 390 160" stroke="{OCHRE}" stroke-width="7" fill="none"/>
 <rect x="318" y="124" width="50" height="26" rx="4" fill="#dff0ee" stroke="{TEAL}" stroke-width="1.5"/>
 <text x="343" y="141" class="fs" text-anchor="middle">muestra</text>
 <text x="343" y="243" class="ft" text-anchor="middle">Criostato y campo {BZ.replace('<sub>','<tspan baseline-shift="sub" font-size="70%">').replace('</sub>','</tspan>').replace('<i>','').replace('</i>','')}</text>
 <line x1="434" y1="132" x2="490" y2="132" stroke="{TEAL}" stroke-width="2.2" marker-end="url(#ah)"/>
 <!-- región cuántica -->
 <rect x="498" y="30" width="246" height="190" rx="12" fill="#fff" stroke="#c9d3db" stroke-width="1.5"/>
 <rect x="512" y="70" width="218" height="140" fill="#e7f3f2"/>
 <path d="M520 92 H574 L584 112 H520 Z M722 92 H668 L658 112 H722 Z M520 168 H574 L584 148 H520 Z M722 168 H668 L658 148 H722 Z" fill="{OCHRE}" opacity=".85"/>
 <ellipse cx="621" cy="130" rx="34" ry="20" fill="#dff0ee" stroke="{TEAL}" stroke-width="2.2"/>
 <circle cx="621" cy="130" r="5" fill="{NAVY}"/>
 {''.join(f'<line x1="{x}" y1="38" x2="{x}" y2="62" stroke="{GRIS}" stroke-width="1.6" marker-end="url(#ahg)"/>' for x in range(548, 720, 34))}
 <text x="621" y="243" class="ft" text-anchor="middle">Región cuántica: un electrón</text>
 <text x="380" y="285" class="fs" text-anchor="middle" fill="{GRIS}">Esquema conceptual, no a escala. La monografía no construye ni calibra el montaje.</text>
</svg>"""


def fig_seccion():
    flechas = "".join(f'<line x1="{x}" y1="8" x2="{x}" y2="34" stroke="{TEAL}" stroke-width="1.8" marker-end="url(#ah2)"/>'
                      for x in range(150, 360, 42))
    return f"""
<svg viewBox="0 0 520 180" class="fig">
 <defs><marker id="ah2" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="{TEAL}"/></marker></defs>
 {flechas}<text x="372" y="26" class="fs">campo B perpendicular</text>
 <rect x="20" y="40" width="480" height="26" fill="{OCHRE}" opacity=".35" stroke="{OCHRE}"/>
 <text x="490" y="58" class="fs" text-anchor="end">compuertas metálicas</text>
 <rect x="20" y="66" width="480" height="30" fill="#f7f9fa" stroke="#cdd5dc"/>
 <text x="30" y="86" class="fs" fill="{GRIS}">barrera / interfaz</text>
 <rect x="20" y="96" width="480" height="5" fill="{TEAL}"/>
 <rect x="20" y="101" width="480" height="52" fill="#e3f1ef" stroke="#cdd5dc"/>
 <text x="490" y="122" class="fs" fill="{TEAL}" text-anchor="end">gas electrónico cuasibidimensional</text>
 <text x="30" y="142" class="fs" fill="{GRIS}">semiconductor</text>
 <text x="260" y="174" class="fs" fill="{GRIS}" text-anchor="middle">Si la excitación en z es grande, solo queda el modo más bajo: ψ<tspan baseline-shift="sub" font-size="70%">3D</tspan> ~ ψ(x, y) φ<tspan baseline-shift="sub" font-size="70%">0</tspan>(z)</text>
</svg>"""


def fig_gauge():
    def panel(x0, titulo, campo, etiqueta):
        out = [f'<rect x="{x0}" y="6" width="230" height="200" rx="10" fill="#f1f5f7" stroke="#cdd5dc"/>',
               f'<text x="{x0+115}" y="28" class="ft" text-anchor="middle">{titulo}</text>']
        for gx in (-1, 0, 1):
            for gy in (-1, 0, 1):
                cx, cy = x0 + 115 + gx * 58, 112 - gy * 46
                ax, ay = campo(gx, gy)
                n = math.hypot(ax, ay)
                if n < 1e-9:
                    out.append(f'<circle cx="{cx}" cy="{cy}" r="2.5" fill="{TEAL}"/>')
                    continue
                L = 15 + 9 * n
                dx, dy = ax / n * L, -ay / n * L
                out.append(f'<line x1="{cx-dx/2:.1f}" y1="{cy-dy/2:.1f}" x2="{cx+dx/2:.1f}" y2="{cy+dy/2:.1f}" '
                           f'stroke="{TEAL}" stroke-width="2.4" marker-end="url(#ah3)"/>')
        out.append(f'<text x="{x0+115}" y="196" class="fs" text-anchor="middle">{etiqueta}</text>')
        return "".join(out)
    return f"""
<svg viewBox="0 0 520 212" class="fig">
 <defs><marker id="ah3" markerWidth="7" markerHeight="7" refX="5" refY="3" orient="auto"><path d="M0,0 L5,3 L0,6 Z" fill="{TEAL}"/></marker>
 <marker id="ah4" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="{NAVY}"/></marker></defs>
 {panel(0, "Gauge simétrico", lambda x, y: (-y, x), "A = (B/2)(−y, x)")}
 {panel(290, "Gauge de Landau", lambda x, y: (0, x + 1.0), "A = B(0, x)")}
 <line x1="236" y1="110" x2="284" y2="110" stroke="{NAVY}" stroke-width="2" marker-end="url(#ah4)"/>
 <text x="260" y="100" class="fs" text-anchor="middle">+ ∇χ</text>
</svg>""".replace("+ ∇χ", "+ grad χ")


def fig_perfiles():
    def P(n, l, x):
        if (n, l) == (0, 0):
            return math.exp(-x * x)
        if (n, l) == (0, 1):
            return x * x * math.exp(-x * x)
        return (1 - x * x) ** 2 * math.exp(-x * x)
    W, H, X0, Y0 = 430, 210, 46, 176
    sx, sy = (W - X0 - 12) / 3.5, (Y0 - 18) / 1.0
    series = [((0, 0), NAVY, "(0,0): sin nodo"), ((0, 1), TEAL, "(0,1): vórtice"), ((1, 0), OCHRE, "(1,0): nodo radial")]
    out = [f'<line x1="{X0}" y1="{Y0}" x2="{W-8}" y2="{Y0}" stroke="{GRIS}"/>',
           f'<line x1="{X0}" y1="{Y0}" x2="{X0}" y2="14" stroke="{GRIS}"/>']
    for t in range(0, 4):
        out.append(f'<text x="{X0+t*sx:.0f}" y="{Y0+16}" class="fs" text-anchor="middle">{t}</text>')
    out.append(f'<text x="{(W+X0)/2:.0f}" y="{Y0+32}" class="fs" text-anchor="middle">r / a</text>')
    out.append(f'<text x="{X0-8}" y="22" class="fs" text-anchor="end">1</text><text x="{X0-8}" y="{Y0}" class="fs" text-anchor="end">0</text>')
    for k, ((n, l), col, lab) in enumerate(series):
        pts = " ".join(f"{X0+x*sx:.1f},{Y0-P(n,l,x)*sy:.1f}" for x in [i * 3.5 / 200 for i in range(201)])
        out.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="3"/>')
        out.append(f'<line x1="{W-150}" y1="{30+k*20}" x2="{W-128}" y2="{30+k*20}" stroke="{col}" stroke-width="3"/>'
                   f'<text x="{W-122}" y="{35+k*20}" class="fs">{lab}</text>')
    out.append(f'<line x1="{X0+sx:.1f}" y1="{Y0}" x2="{X0+sx:.1f}" y2="70" stroke="{OCHRE}" stroke-dasharray="4 4"/>')
    return f'<svg viewBox="0 0 {W} {H+16}" class="fig">{"".join(out)}</svg>'


def fig_gantt():
    filas = [("Investigación documental", "OE1, OE5", 1, 5), ("Desarrollo analítico (con avance previo)", "OE2", 1, 7),
             ("Estados (0,0) y (0,1)", "OE3", 4, 8), ("Estado (1,0); convergencia y ruido", "OE3", 7, 11),
             ("Contraste con la literatura", "OE4", 10, 12), ("Discusión epistemológica", "OE5", 10, 13),
             ("Redacción, RAE y sustentación", "todos", 12, 16)]
    X0, W, top, rh = 380, 912, 46, 38
    wk = (W - 12 - X0) / 16
    out = [f'<rect x="{X0}" y="8" width="{16*wk:.1f}" height="28" fill="{NAVY}"/>',
           f'<text x="{X0+8*wk:.1f}" y="27" class="ft" style="fill:#fff" text-anchor="middle">Trabajo de Grado · 2027-1 (16 semanas)</text>']
    for i, (nom, obj, a, b) in enumerate(filas):
        y = top + i * rh
        if i % 2 == 0:
            out.append(f'<rect x="0" y="{y}" width="{W}" height="{rh}" fill="#f4f7f9"/>')
        out.append(f'<text x="8" y="{y+24}" class="ft">{nom}</text><text x="{X0-10}" y="{y+24}" class="fs" text-anchor="end" fill="{GRIS}">{obj}</text>')
        x = X0 + (a - 1) * wk
        out.append(f'<rect x="{x:.1f}" y="{y+8}" width="{(b-a+1)*wk:.1f}" height="{rh-16}" rx="5" fill="{NAVY}"/>')
    y = top + len(filas) * rh
    out.append(f'<text x="8" y="{y+24}" class="ft" style="fill:{OCHRE}">Bitácora de decisiones de modelado</text>'
               f'<rect x="{X0}" y="{y+12}" width="{16*wk:.1f}" height="10" rx="5" fill="{OCHRE}" opacity=".8"/>')
    for s in (1, 4, 8, 12, 16):
        if s == 1:
            xx, anc = X0 + 3, "start"
        elif s == 16:
            xx, anc = X0 + 16 * wk - 3, "end"
        else:
            xx, anc = X0 + (s - 0.5) * wk, "middle"
        out.append(f'<text x="{xx:.1f}" y="{y+52}" class="fs" text-anchor="{anc}">s{s}</text>')
    return f'<svg viewBox="0 0 {W} {y+60}" class="fig">{"".join(out)}</svg>'


# ------------------------------------------------------------------ contenido de las láminas
TITULO = "Análisis del problema inverso de la ecuación de Schrödinger estacionaria con potencial vectorial"
SUBT = "Formulación hidrodinámica y estudio de estados de Fock–Darwin"

LAMINAS = []  # (seccion, titulo, html, segundos, guion, notas)


def L(seccion, titulo, html, seg, guion, notas=""):
    LAMINAS.append(dict(seccion=seccion, titulo=titulo, html=html, seg=seg, guion=guion, notas=notas))


L("", "Presentación", "", 15,
  "Buenos días. Soy Juan Sebastián Sánchez Álvarez, del Programa de Física de la Universidad Distrital. Presento la "
  "propuesta «Análisis del problema inverso de la ecuación de Schrödinger estacionaria con potencial vectorial», "
  "dirigida por el profesor John Hernán Díaz Forero.",
  "El subtítulo queda en la lámina; no hace falta leerlo.")

L("Modalidad", "Monografía de investigación teórica", """
<div class="two">
 <div>
  <div class="card big"><div class="k">Acuerdo 004 de 2026 · Art. 2, literal b</div>
  «Trabajo académico, original y argumentativo que analiza un tema específico a través de la definición de preguntas
  de investigación y objetivos que se responden y cumplen con base en la selección, sistematización y revisión de
  fuentes primarias y secundarias.»</div>
  <p class="muted">Subtipo: <b>de investigación teórica</b> — presentación crítica y exposición basada en revisión documental teórica.</p>
 </div>
 <div>
  <ul class="lst">
   <li><b>Duración:</b> un periodo, 2027-1 (Art. 9); cierre previsto entre finales de mayo y mediados de junio de 2027</li>
   <li><b>Evaluación:</b> jurado; documento escrito 60 % y sustentación pública 40 % (Art. 26)</li>
   <li><b>Por qué esta modalidad:</b> el aporte es analítico y documental, apoyado en cálculo; no requiere estancia ni convocatoria de semillero</li>
  </ul>
 </div>
</div>""", 20,
  "La modalidad es monografía de investigación teórica, del artículo dos, literal b, del Acuerdo 004 de 2026: un "
  "trabajo original y argumentativo que responde una pregunta de investigación mediante la revisión crítica de "
  "fuentes, aquí apoyada en desarrollo analítico y en cálculo.",
  "Si preguntan por qué no la modalidad de investigación: esa exige vínculo a un grupo o semillero y convocatoria (Art. 20).")

L("Planteamiento físico · 1 de 4", "Laboratorio conceptual: el objeto real de referencia", f"""
{fig_laboratorio()}
<div class="row4">
 <div class="tag"><b>Sistema</b>un electrón confinado lateralmente en un punto cuántico semiconductor</div>
 <div class="tag"><b>Entorno</b>confinamiento y campo {BZ} perpendicular; red, contactos y electrónica no se modelan</div>
 <div class="tag"><b>Aparato</b>en la monografía: el procedimiento de reconstrucción (datos, gauge, malla)</div>
 <div class="tag"><b>Observador</b>teórico-computacional: prescribe datos ideales y calcula</div>
</div>
<div class="warn">Dato teórico ≠ magnitud medible: usar {P_} y {J} no implica que un laboratorio los mida localmente y sin error.</div>""", 55,
  "Empiezo por el objeto real de referencia: un punto cuántico semiconductor definido por compuertas. Un electrón "
  "queda confinado lateralmente en una región de unas decenas de nanómetros, dentro de un criostato, y un campo "
  "magnético atraviesa el plano perpendicularmente. Ese es el sistema físico. El entorno incluye la red cristalina, "
  "los contactos y la electrónica, que no se modelan. En un laboratorio, el observador ajusta voltajes y campo y "
  "obtiene información indirecta, espectroscópica o de transporte. En esta monografía el observador es "
  "teórico-computacional: elige un estado conocido, prescribe los datos, fija el gauge y la malla, y calcula. Hay "
  "que ser claro: que el método use la densidad y la corriente no significa que un laboratorio las mida directamente.",
  "P1–P3 del documento del director. Una simulación no es una medición experimental.")

L("Planteamiento físico · 2 de 4", "Del laboratorio al modelo ideal", f"""
<div class="two w55">
 <div>{fig_seccion()}
  <div class="levels"><span>Laboratorio 3D</span>{ARR}<span>Dominio plano <i>D</i></span>{ARR}<span>Estados <i>L</i>²(<i>D</i>)</span></div>
  <p class="muted c">El espacio de Hilbert no es un espacio físico ni un sistema de referencia.</p>
 </div>
 <div>
  <ul class="lst sm">
   <li><b>2D:</b> excitación transversal Δ<sub><i>z</i></sub> {LL} energías orbitales</li>
   <li><b>Una partícula</b>, sin espín, sin segunda cuantización</li>
   <li><b>Estacionario:</b> Ψ = ψ(<b>r</b>) e<sup>−<i>iEt</i>/ℏ</sup>; el tiempo solo es una fase</li>
   <li><b>Cuántico:</b> acción característica <i>m</i>ω<sub>0</sub><i>a</i><sub>0</sub>² ∼ ℏ</li>
   <li><b>No relativista:</b> banda parabólica de masa efectiva <i>m</i>*</li>
  </ul>
  <table class="tb"><tr><th colspan="2">Escalas ilustrativas (<i>m</i>* = 0,067 <i>m</i><sub>e</sub>, ℏω<sub>0</sub> = 2 meV, |{BZ}| = 1 T)</th></tr>
   <tr><td>Longitud de confinamiento <i>a</i><sub>0</sub></td><td>23,9 nm</td></tr>
   <tr><td>Energía ciclotrónica ℏω<sub>c</sub></td><td>1,73 meV</td></tr>
   <tr><td>Longitud magnética ℓ<sub><i>B</i></sub></td><td>25,7 nm</td></tr></table>
 </div>
</div>""", 55,
  "Del laboratorio se pasa a un modelo ideal. Si la excitación en la dirección perpendicular es mucho mayor que las "
  "energías orbitales, ese grado de libertad se congela y queda un movimiento en dos coordenadas, x e y. Distingo "
  "tres espacios: el laboratorio tridimensional, el dominio plano del modelo y el espacio de Hilbert de estados, que "
  "no es un espacio físico. ¿Por qué cuántico? Con valores típicos, masa efectiva de 0,067 la del electrón y una "
  "separación de 2 milielectronvoltios, la longitud de confinamiento es de unos 24 nanómetros y la acción "
  "característica es del orden de hache barra. ¿Por qué no relativista? Porque se describe una banda parabólica de "
  "masa efectiva. Además: una sola partícula, sin espín y en estado estacionario.",
  "Las escalas son ejemplos de orden de magnitud, no mediciones propias. P4–P7: el espín se excluye para aislar el problema orbital (Zeeman y espín-órbita quedan fuera).")

L("Planteamiento físico · 3 de 4", "Modelo físico-matemático", f"""
<div class="two w52">
 <div>
  <div class="eq">Ĥ = {fr('1', '2'+m_)} [ −<i>i</i>ℏ{NAB} − {q_}{A}(<b>r</b>) ]² + {V_}(<b>r</b>),&nbsp;&nbsp; Ĥψ = {E_}ψ</div>
  <ul class="lst sm">
   <li>Masa efectiva {m_} &gt; 0, carga {q_} ≠ 0, dominio <i>D</i> del plano; {V_} es una <b>energía</b> (eV), no un voltaje</li>
   <li>Campo: {BZ} = ∂<sub><i>x</i></sub><i>A</i><sub><i>y</i></sub> − ∂<sub><i>y</i></sub><i>A</i><sub><i>x</i></sub>;&nbsp; {WC} = {q_}{BZ}/{m_},&nbsp; Ω² = {W0}² + {WC}²/4</li>
   <li>Corriente: {J} = {fr('1', m_)} Re[ψ*(−<i>i</i>ℏ{NAB} − {q_}{A})ψ],&nbsp; {P_} = |ψ|²</li>
   <li><b>Fronteras:</b> en el plano, normalizable y con decaimiento; en el cálculo, dominio finito con ψ {APX} 0 en el borde</li>
  </ul>
 </div>
 <div>{fig_gauge()}
  <div class="card"><b>Cambio de gauge</b> {A} {ARR} {A} + {NAB}χ, &nbsp;ψ {ARR} e<sup><i>iq</i>χ/ℏ</sup>ψ, &nbsp;{S_} {ARR} {S_} + {q_}χ<br>
  <span class="ok">Invariantes:</span> {P_}, {J}, {BZ}, {V_} − {E_} y {U} = {NAB}{S_} − {q_}{A}.&nbsp; <span class="no">Dependen del gauge:</span> {A} y {S_}.</div>
 </div>
</div>""", 60,
  "El modelo es el hamiltoniano de una partícula de masa m y carga q con acoplamiento mínimo: el momento canónico "
  "menos q por el potencial vectorial, más un potencial escalar, que es una energía. El campo magnético es el "
  "rotacional de A. Un mismo campo admite varias representaciones: el gauge simétrico y el de Landau difieren en un "
  "gradiente. Al cambiar de gauge cambia la fase de la función de onda, pero la densidad, la corriente, el campo y V "
  "menos E no cambian: esas son las magnitudes físicas. El modelo exige además condiciones de frontera: en el plano, "
  "normalizabilidad y decaimiento; en el cálculo, un dominio finito con la función de onda prácticamente nula en el "
  "borde. Sin estas hipótesis no hay unicidad, aunque se cuenten las ecuaciones.",
  "P8: hay potencial vectorial aunque se conozca el campo porque el acoplamiento mínimo usa A. Momento canónico p = −iℏ∇ (depende del gauge) frente a momento cinético π = p − qA.")

L("Planteamiento físico · 4 de 4", "Del problema directo al inverso", f"""
<div class="flow">
 <div class="fb"><b>Directo</b> {V_}, {A}, fronteras</div>{ARR}<div class="fb">resolver Ĥψ = {E_}ψ</div>{ARR}<div class="fb">ψ, {E_}, {P_}, {J}</div>
 <div class="sp"></div>
 <div class="fb alt"><b>Inverso</b> datos del estado</div>{ARR}<div class="fb alt">Madelung</div>{ARR}<div class="fb alt">{V_} − {E_}, {BZ}, [{A}]<sub>gauge</sub></div>
</div>
<div class="two w50 mt">
 <div>
  <div class="eq sm">ψ = {sq(P_)} e<sup><i>iS</i>/ℏ</sup>,&nbsp; {U} = {NAB}{S_} − {q_}{A}</div>
  <div class="eq sm">{NAB}·({P_}{U}) = 0 &nbsp;&nbsp;(continuidad)</div>
  <div class="eq sm">{MAESTRA}</div>
  <div class="warn">Control exacto (Fock–Darwin, {WC}/{W0} = 2): si se ignora {A}, la inversión da ½<i>m</i>Ω²<i>r</i>², el <b>doble</b> del confinamiento real ½<i>m</i>{W0}²<i>r</i>².</div>
 </div>
 <div>
  <table class="tb cases"><tr><th>Datos</th><th>Qué se determina</th></tr>
   <tr><td>({P_}, {J})</td><td class="ok">{U} = {m_}{J}/{P_}; {V_} − {E_} y {BZ} localmente, fuera de nodos</td></tr>
   <tr><td>({P_}, {S_})</td><td class="no">{BZ} indeterminado: Φ {ARR} Φ + <i>F</i>({P_}) cumple la continuidad</td></tr>
   <tr><td>({P_}, {S_}, {BZ})</td><td>{A} salvo gauge (ecuación elíptica); luego {V_} − {E_}</td></tr>
   <tr><td>({P_}, {S_}, {V_})</td><td>problema no lineal por estudiar</td></tr></table>
  <p class="muted">Nodos y vórtices: los cocientes por {P_} no se evalúan directamente; circulación ∮{NAB}{S_}·d<b>ℓ</b> = 2πℏℓ.</p>
 </div>
</div>""", 65,
  "En el problema directo se conocen los potenciales y se buscan los estados; en el inverso se conoce información del "
  "estado y se buscan los potenciales. Con la descomposición de Madelung, la función de onda es la raíz de la "
  "densidad por una fase, y la ecuación de Schrödinger se separa en la continuidad y en una ecuación que da V menos E "
  "en términos de la densidad y del momento cinético u. Lo que se reconstruye depende de los datos: con densidad y "
  "corriente se obtienen localmente V menos E y el campo, fuera de los nodos; con densidad y fase en un gauge, el "
  "campo queda indeterminado. Un control con Fock–Darwin lo muestra: si se ignora el potencial vectorial, la "
  "inversión atribuye el confinamiento magnético a V y obtiene el doble del real.",
  "Derivación del control (estado fundamental): ∇²√P/√P = −2/a² + r²/a⁴ da V − E = −ℏΩ + (m/2)(Ω² − ω_c²/4) r² = −ℏΩ + ½mω₀²r². Sin el término |qA|² queda Ω², y con ω_c/ω₀ = 2, Ω² = 2ω₀². "
  "Distinguir cambio de gauge (no cambia observables) de indeterminación física por datos incompletos (caso (P, S)).")

L("Estado del arte", "Trayectoria de los antecedentes", f"""
<div class="grid3">
 <div class="card"><div class="k">1929–1955 · Espectral 1D</div>Ambarzumian, Borg, Gel'fand–Levitan<div class="lim">Aporte: unicidad con espectros suficientes · Límite: 1D, sin campo</div></div>
 <div class="card"><div class="k">1950–1989 · Dispersión</div>Chadan y Sabatier<div class="lim">Aporte: métodos en varias dimensiones · Límite: ambigüedades; datos externos</div></div>
 <div class="card"><div class="k">1993–1995 · Con campo magnético</div>Sun; Nakamura, Sun y Uhlmann; Eskin y Ralston<div class="lim">Aporte: determinan {B} y {V_}; {A} solo salvo gauge · Límite: datos de frontera; dimensión ≥ 3</div></div>
 <div class="card"><div class="k">1995–2024 · Desde el estado</div>Cooper, Khare y Sukhatme; Bhalgamiya y Novotny<div class="lim">Aporte: {V_} explícito desde {P_} · Límite: solo ψ real, sin {A}</div></div>
 <div class="card"><div class="k">1927–1952 · Hidrodinámica</div>Madelung; Bohm; Takabayasi<div class="lim">Aporte: ecuaciones para ψ complejo con {A} · Límite: uso en el problema directo</div></div>
 <div class="card"><div class="k">1928–2002 · Fock–Darwin</div>Fock; Darwin; Reimann y Manninen<div class="lim">Aporte: solución exacta con vórtices y nodos · Uso: banco de pruebas</div></div>
</div>""", 50,
  "Los antecedentes forman una trayectoria. Los problemas espectrales en una dimensión, de Ambarzumian, Borg y "
  "Gel'fand y Levitan, mostraron unicidad con espectros suficientes. La teoría de dispersión, sistematizada por "
  "Chadan y Sabatier, trajo ambigüedades. Con campo magnético, Sun, Nakamura y Uhlmann, y Eskin y Ralston probaron "
  "que los datos de frontera determinan el campo y V, pero el potencial vectorial solo salvo gauge. Bhalgamiya y "
  "Novotny, en 2024, reconstruyen V a partir de la densidad, pero solo para funciones de onda reales. La formulación "
  "de Madelung y Bohm da las ecuaciones, y Fock–Darwin un caso exacto.",
  "No trasladar sin prueba los teoremas magnéticos (datos de frontera, dimensión ≥ 3) al caso 2D con datos internos.")

L("Pregunta científica", "Vacío de conocimiento y pregunta", """
<div class="card big">En las fuentes revisadas hasta ahora <b>no se identificó</b> una reconstrucción con <b>datos internos</b> de un
<b>estado complejo</b>, con campo magnético y tratamiento de los nodos. Esta afirmación se someterá a la revisión documental.</div>
<div class="q"><div class="k">Pregunta de investigación</div>¿Bajo qué condiciones es posible reconstruir los potenciales asociados a una
partícula cargada descrita por la ecuación estacionaria de Schrödinger en dos dimensiones, a partir de la formulación
hidrodinámica de Madelung, y cuáles son las limitaciones de dicha reconstrucción en estados de Fock–Darwin?</div>
<p class="muted">Pregunta complementaria: ¿qué permiten comprender Barad y Latour sobre el papel de los datos, el gauge y los procedimientos numéricos en el potencial reconstruido?</p>""", 40,
  "En las fuentes revisadas hasta ahora no se identificó una reconstrucción con datos internos de un estado complejo, "
  "con campo magnético y tratamiento de los nodos; esa afirmación se pondrá a prueba en la revisión documental. De "
  "ahí la pregunta: ¿Bajo qué condiciones es posible reconstruir los potenciales asociados a una partícula cargada "
  "descrita por la ecuación estacionaria de Schrödinger en dos dimensiones, a partir de la formulación hidrodinámica "
  "de Madelung, y cuáles son las limitaciones de dicha reconstrucción en estados de Fock–Darwin?",
  "No decir «nadie lo ha estudiado»: decir «en las fuentes revisadas no se identificó». Aun si aparecen trabajos parcialmente equivalentes, compararlos con precisión es una contribución.")

L("Metodología", "Cinco fases, con alcance computacional acotado", f"""
<div class="two w50">
 <div>
  <ol class="phases">
   <li><b>Documental:</b> WoS, Scopus, arXiv, PhilPapers; criterios de inclusión; bola de nieve; matrices de comparación</li>
   <li><b>Analítica:</b> derivación con hipótesis explícitas; qué determina cada conjunto de datos</li>
   <li><b>Computacional:</b> tres estados de Fock–Darwin, {WC}/{W0} = 2; diferencias finitas, convergencia y ruido</li>
   <li><b>Contraste</b> con la literatura</li>
   <li><b>Epistemológica:</b> bitácora de decisiones leída con Barad y Latour</li>
  </ol>
  <p class="muted">Criterios de éxito declarados antes de cada prueba; los resultados negativos se reportan.</p>
 </div>
 <div>{fig_perfiles()}
  <div class="chain"><span>solución exacta</span>{ARR}<span>datos</span>{ARR}<span>discretización</span>{ARR}<span>inversión</span>{ARR}<span>error, orden, ruido</span></div>
  <p class="muted c">Riesgo esperado: error de truncamiento ∼ <i>h</i>² y amplificación del ruido ∼ ε/<i>h</i>².</p>
 </div>
</div>""", 60,
  "La metodología tiene cinco fases. Primero, investigación documental en Web of Science, Scopus, arXiv y PhilPapers, "
  "con criterios de inclusión y matrices de comparación. Segundo, desarrollo analítico: derivar las ecuaciones con "
  "hipótesis explícitas y establecer qué determina cada conjunto de datos. Tercero, un estudio computacional acotado "
  "a tres estados de Fock–Darwin con omega c sobre omega cero igual a dos: el fundamental como control, uno con "
  "vórtice y uno con nodo radial. Cada prueba va de la solución exacta a los datos, la discretización, la inversión y "
  "la validación. Cuarto, contraste con la literatura. Quinto, una discusión epistemológica con Barad y Latour sobre "
  "una bitácora de decisiones de modelado. Los criterios de éxito se fijan antes de ejecutar.",
  "P13–P15: Fock–Darwin tiene solución exacta y tres tipos de estructura nodal. La solución analítica sirve de patrón: separa error de discretización, ruido, errores de implementación y efectos de los nodos. Exactitud, convergencia y estabilidad frente al ruido son propiedades distintas.")

L("Objetivos", "Objetivo general y objetivos específicos", """
<div class="q sm"><div class="k">Objetivo general</div>Analizar las condiciones de reconstrucción de los potenciales escalar y vectorial en la
ecuación estacionaria de Schrödinger, mediante la formulación hidrodinámica de Madelung y el estudio teórico-computacional
de estados de Fock–Darwin, y discutir ese proceso de reconstrucción desde el realismo agencial de Karen Barad y la teoría
del actor-red de Bruno Latour.</div>
<ol class="oe">
 <li><b>OE1.</b> Sistematizar los fundamentos teóricos y los antecedentes bibliográficos del problema inverso de la ecuación de Schrödinger, particularmente en presencia de potenciales vectoriales.</li>
 <li><b>OE2.</b> Derivar y analizar las ecuaciones correspondientes a la formulación hidrodinámica de Madelung, identificando las condiciones de reconstrucción de los potenciales y el papel de la libertad de gauge.</li>
 <li><b>OE3.</b> Estudiar analítica y numéricamente algunos casos representativos de estados de Fock–Darwin, con el propósito de examinar la reconstrucción de los potenciales y sus limitaciones.</li>
 <li><b>OE4.</b> Contrastar los resultados obtenidos con los reportados en la literatura, identificando las condiciones bajo las cuales resulta aplicable el procedimiento de reconstrucción.</li>
 <li><b>OE5.</b> Discutir, desde el realismo agencial de Karen Barad y la teoría del actor-red de Bruno Latour, el papel de la elección de los datos, del gauge y de los procedimientos numéricos en la constitución del potencial reconstruido.</li>
</ol>""", 65,
  "El objetivo general es: Analizar las condiciones de reconstrucción de los potenciales escalar y vectorial en la "
  "ecuación estacionaria de Schrödinger, mediante la formulación hidrodinámica de Madelung y el estudio "
  "teórico-computacional de estados de Fock–Darwin, y discutir ese proceso de reconstrucción desde el realismo "
  "agencial de Karen Barad y la teoría del actor-red de Bruno Latour. Los específicos son: uno, sistematizar los "
  "fundamentos y antecedentes del problema inverso con potenciales vectoriales; dos, derivar y analizar las ecuaciones "
  "de Madelung, identificando las condiciones de reconstrucción y el papel del gauge; tres, estudiar analítica y "
  "numéricamente casos representativos de Fock–Darwin y sus limitaciones; cuatro, contrastar los resultados con la "
  "literatura; y cinco, discutir con Barad y Latour el papel de los datos, el gauge y lo numérico en el potencial reconstruido.",
  "La lámina muestra los objetivos literales; el guion lee el general completo y resume los específicos. Si el Consejo pide la lectura literal, léelos de la lámina (+25 s).")

L("Cronograma", "Actividades en el periodo 2027-1", f"""{fig_gantt()}<p class="muted">El desarrollo analítico ya tiene un avance inicial. Semanas orientativas; las fechas se ajustan al calendario académico oficial de 2027-1.</p>""", 30,
  "El trabajo se desarrolla en un solo periodo, 2027-1, y cierra entre finales de mayo y mediados de junio. Parto de un "
  "avance inicial del desarrollo analítico. En las primeras semanas completo la revisión documental y consolido el "
  "análisis; luego trabajo los dos primeros estados, después el estado con nodo radial con convergencia y ruido, y "
  "cierro con el contraste, la discusión epistemológica y la redacción. La bitácora se lleva durante todo el proceso.",
  "Si preguntan por el plazo: el Art. 9 fija un máximo (un periodo si el plan tiene un espacio de Trabajo de Grado, dos si tiene dos), no un mínimo; terminar en un periodo queda dentro del máximo. Con dos espacios, la nota de TG I queda pendiente hasta la sustentación (Art. 5, par. 2). Prórroga de un periodo por el Consejo Curricular (Art. 9, par. 1).")

L("Cierre", "Conclusiones", f"""
<ol class="concl">
 <li><b>Problema físico delimitado:</b> una partícula cargada, no relativista y sin espín, en 2D, con campo perpendicular y estado estacionario.</li>
 <li><b>Lo reconstruible depende de los datos:</b> con ({P_}, {J}) se obtienen localmente {V_} − {E_} y {BZ}; con ({P_}, {S_}) el campo queda indeterminado. El gauge y los nodos no son detalles técnicos.</li>
 <li><b>Fock–Darwin es el control exacto:</b> sin el potencial vectorial, la inversión atribuye el confinamiento magnético a {V_}.</li>
 <li><b>Propuesta viable</b> en dos periodos, con alcance computacional acotado y una discusión epistemológica subordinada a la física.</li>
</ol>""", 35,
  "Para cerrar, cuatro ideas. El problema está delimitado físicamente: una partícula cargada, sin espín, en dos "
  "dimensiones y con campo perpendicular. Lo que se puede reconstruir depende de los datos, y el gauge y los nodos no "
  "son detalles técnicos. Fock–Darwin ofrece un control exacto: muestra que sin potencial vectorial la reconstrucción "
  "falla. Y la propuesta es viable en dos periodos, con un alcance computacional deliberadamente acotado.",
  "P16: el aporte es organizar críticamente los antecedentes, precisar hipótesis y datos, verificar reconstrucciones controladas y caracterizar sus límites, sin prometer resolver todo el problema inverso magnético.")

L("Cierre", "Bibliografía principal", """
<ol class="bib">
 <li>B. Bhalgamiya y M. A. Novotny, <i>Am. J. Phys.</i> <b>92</b>, 975–979 (2024).</li>
 <li>I. M. Gel'fand y B. M. Levitan, <i>Izv. Akad. Nauk SSSR Ser. Mat.</i> <b>15</b>, 309–360 (1951).</li>
 <li>K. Chadan y P. C. Sabatier, <i>Inverse Problems in Quantum Scattering Theory</i>, Springer (1989).</li>
 <li>G. Nakamura, Z. Sun y G. Uhlmann, <i>Math. Ann.</i> <b>303</b>, 377–388 (1995).</li>
 <li>G. Eskin y J. Ralston, <i>Commun. Math. Phys.</i> <b>173</b>, 199–224 (1995).</li>
 <li>E. Madelung, <i>Z. Phys.</i> <b>40</b>, 322 (1927); D. Bohm, <i>Phys. Rev.</i> <b>85</b>, 166 (1952).</li>
 <li>V. Fock, <i>Z. Phys.</i> <b>47</b>, 446 (1928); C. G. Darwin, <i>Proc. Camb. Phil. Soc.</i> <b>27</b>, 86 (1931).</li>
 <li>S. M. Reimann y M. Manninen, <i>Rev. Mod. Phys.</i> <b>74</b>, 1283 (2002); L. P. Kouwenhoven <i>et al.</i>, <i>Rep. Prog. Phys.</i> <b>64</b>, 701 (2001).</li>
 <li>K. Barad, <i>Meeting the Universe Halfway</i> (2007); B. Latour, <i>Science in Action</i> (1987).</li>
</ol>
<div class="thanks">Gracias</div>""", 10,
  "Las referencias principales están en la lámina y la lista completa en el documento. Muchas gracias; quedo atento "
  "a sus preguntas.")

# ------------------------------------------------------------------ HTML de la presentación
CSS_SLIDES = f"""
@page {{ size: 13.333in 7.5in; margin: 0 }}
* {{ box-sizing: border-box }}
body {{ margin: 0; font-family: "Noto Sans"; color: #1a2433; -webkit-print-color-adjust: exact; print-color-adjust: exact }}
.slide {{ width: 13.333in; height: 7.5in; position: relative; overflow: hidden; page-break-after: always;
         padding: .42in .62in .55in; font-size: 17pt; line-height: 1.32 }}
.sec {{ font-size: 10.5pt; letter-spacing: .12em; text-transform: uppercase; color: {TEAL}; font-weight: 700 }}
h1 {{ font-size: 27pt; color: {NAVY}; margin: .04in 0 .2in; font-weight: 700 }}
h1:after {{ content: ""; display: block; width: 1.1in; height: 4px; background: {OCHRE}; margin-top: .08in }}
.foot {{ position: absolute; left: .62in; right: .62in; bottom: .22in; font-size: 9.5pt; color: {GRIS};
        display: flex; justify-content: space-between; border-top: 1px solid #d8dee4; padding-top: .06in }}
.fig {{ width: 100%; height: auto; display: block }}
.fig .ft {{ font: 600 15px "Noto Sans"; fill: {NAVY} }} .fig .fs {{ font: 13px "Noto Sans"; fill: #2a3646 }}
.two {{ display: grid; grid-template-columns: 1fr 1fr; gap: .38in; align-items: start }}
.two.w55 {{ grid-template-columns: 1.08fr 1fr }} .two.w52 {{ grid-template-columns: 1.06fr 1fr }} .two.w50 {{ grid-template-columns: 1fr 1fr }}
.mt {{ margin-top: .14in }}
.card {{ background: #f1f5f7; border-radius: 12px; padding: .14in .2in; font-size: 15pt }}
.card.big {{ font-size: 17pt; border-left: 6px solid {TEAL} }}
.k {{ font-size: 10.5pt; font-weight: 700; color: {TEAL}; text-transform: uppercase; letter-spacing: .06em; margin-bottom: .04in }}
.lim {{ font-size: 12pt; color: #3b4757; margin-top: .06in }}
.grid3 {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: .18in }}
.grid3 .card {{ min-height: 1.95in; font-size: 15pt }}
.lst {{ margin: .05in 0; padding-left: .28in }} .lst li {{ margin: .06in 0 }} .lst.sm {{ font-size: 15pt }}
.muted {{ color: {GRIS}; font-size: 13pt }} .c {{ text-align: center }}
.row4 {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: .14in; margin-top: .06in }}
.tag {{ background: #f1f5f7; border-top: 4px solid {TEAL}; border-radius: 8px; padding: .06in .12in; font-size: 11.5pt; line-height: 1.22 }}
.tag b {{ display: block; color: {NAVY}; font-size: 13.5pt }}
.warn {{ background: #fbf4e8; border-left: 6px solid {OCHRE}; border-radius: 8px; padding: .08in .16in; font-size: 13.5pt; margin-top: .12in }}
.eq {{ background: #eaf4f3; border-left: 5px solid {TEAL}; border-radius: 8px; padding: .12in .2in; font-size: 19pt; margin-bottom: .12in }}
.eq.sm {{ font-size: 16.5pt; padding: .07in .18in; margin-bottom: .08in }}
.tb {{ border-collapse: collapse; width: 100%; font-size: 13.5pt; margin-top: .1in }}
.tb th {{ background: {NAVY}; color: #fff; text-align: left; padding: .05in .1in; font-weight: 600; font-size: 12.5pt }}
.tb td {{ border-bottom: 1px solid #d8dee4; padding: .05in .1in; vertical-align: top }}
.cases td:first-child {{ white-space: nowrap; font-weight: 600 }}
.ok {{ color: {TEAL}; font-weight: 600 }} .no {{ color: #b0461f; font-weight: 600 }}
.flow {{ display: grid; grid-template-columns: auto auto auto auto auto; gap: .06in .12in; align-items: center; justify-content: start; font-size: 15pt }}
.flow .sp {{ grid-column: 1 / -1; height: 0 }}
.fb {{ background: #eef2f5; border: 1.5px solid #9fb0bf; border-radius: 10px; padding: .05in .16in }}
.fb.alt {{ background: #eaf4f3; border-color: {TEAL} }}
.q {{ background: {NAVY}; color: #fff; border-radius: 14px; padding: .2in .3in; font-size: 19pt; margin: .22in 0 .14in; line-height: 1.38 }}
.q .k {{ color: #7fd3ca }} .q.sm {{ font-size: 15.5pt; margin: .04in 0 .12in; padding: .14in .26in }}
.oe {{ list-style: none; padding: 0; margin: 0; font-size: 13.4pt; line-height: 1.3 }} .oe li {{ margin: .055in 0 }}
.oe b {{ color: {TEAL} }}
.phases {{ font-size: 15pt; padding-left: .3in; margin: 0 }} .phases li {{ margin: .07in 0 }}
.chain {{ display: flex; flex-wrap: wrap; align-items: center; gap: .05in; font-size: 12pt; margin-top: .04in }}
.chain span {{ background: #eaf4f3; border: 1px solid {TEAL}; border-radius: 6px; padding: .02in .08in }}
.levels {{ display: flex; align-items: center; justify-content: center; gap: .1in; font-size: 14pt; margin-top: .1in }}
.levels span {{ background: #eef2f5; border: 1px solid #9fb0bf; border-radius: 8px; padding: .03in .12in }}
.concl {{ font-size: 18pt; line-height: 1.4; padding-left: .36in }} .concl li {{ margin: .13in 0 }}
.bib {{ font-size: 14.2pt; line-height: 1.38; padding-left: .36in; margin-top: 0 }}
.thanks {{ position: absolute; right: .62in; bottom: .62in; font-size: 30pt; color: {TEAL}; font-weight: 700 }}
.s {{ display: inline-block }}
.sq {{ display: inline-flex; align-items: flex-end; vertical-align: -0.18em }}
.sq .rad {{ width: .46em; height: 1.18em; flex: none }} .sq .rc {{ border-top: .065em solid currentColor; padding: 0 .06em; line-height: 1.12; margin-left: -.02em }}
.fr {{ display: inline-flex; flex-direction: column; vertical-align: middle; text-align: center; font-size: .86em; margin: 0 .08em; line-height: 1.1 }}
.fr > span:first-child {{ border-bottom: .055em solid currentColor; padding: 0 .12em .02em }}
sub, sup {{ font-size: .68em; line-height: 0 }}
/* portada */
.cover {{ background: {NAVY}; color: #fff; padding: .7in .8in }}
.cover .inst {{ font-size: 13pt; letter-spacing: .08em; opacity: .9 }}
.cover h1 {{ color: #fff; font-size: 31pt; line-height: 1.22; margin-top: 1.05in; max-width: 9.6in }}
.cover h1:after {{ background: {OCHRE} }}
.cover .sub {{ font-size: 18pt; color: #b9e3de; margin-top: .1in }}
.cover .who {{ position: absolute; left: .8in; bottom: .7in; font-size: 15pt; line-height: 1.55 }}
.cover .who b {{ color: #7fd3ca; font-weight: 600 }}
.cover svg.rings {{ position: absolute; right: -0.6in; top: -0.9in; width: 6.4in; opacity: .55 }}
"""


def html_presentacion():
    n = len(LAMINAS)
    partes = []
    for i, s in enumerate(LAMINAS, 1):
        if i == 1:
            partes.append(f"""<section class="slide cover" id="s1">
<svg class="rings" viewBox="0 0 400 400">{''.join(f'<circle cx="200" cy="200" r="{r}" fill="none" stroke="#7a8ea6" stroke-width="1.2"/>' for r in (40, 80, 120, 160, 196))}
<path d="M10 210 C80 150 140 250 200 200 S320 150 390 190" fill="none" stroke="#cfe7e4" stroke-width="2.5"/>
<path d="M10 190 C80 250 140 150 200 200 S320 250 390 210" fill="none" stroke="#cfe7e4" stroke-width="2.5" opacity=".7"/>
<circle cx="200" cy="200" r="7" fill="{OCHRE}"/></svg>
<div class="inst">UNIVERSIDAD DISTRITAL FRANCISCO JOSÉ DE CALDAS<br>Facultad de Ciencias Matemáticas y Naturales · Programa Académico de Física</div>
<h1>{TITULO}</h1><div class="sub">{SUBT}</div>
<div class="who"><b>Estudiante</b> Juan Sebastián Sánchez Álvarez<br><b>Director</b> Prof. John Hernán Díaz Forero<br>
<b>Sustentación de la propuesta</b> · Consejo Curricular · 24 de noviembre de 2026</div></section>""")
            continue
        partes.append(f"""<section class="slide" id="s{i}"><div class="sec">{s['seccion']}</div><h1>{s['titulo']}</h1>{s['html']}
<div class="foot"><span>J. S. Sánchez Álvarez · Problema inverso de Schrödinger con potencial vectorial</span><span>{i} / {n}</span></div></section>""")
    js = "<script>if(location.hash){var k=location.hash.slice(1);document.querySelectorAll('.slide').forEach(function(e){if(e.id!==k)e.style.display='none'})}</script>"
    return f'<!doctype html><html lang="es"><head><meta charset="utf-8"><title>Presentación</title><style>{CSS_SLIDES}</style></head><body>{"".join(partes)}{js}</body></html>'


# ------------------------------------------------------------------ guion
PREGUNTAS = [
    ("¿Cuál es el objeto físico real de referencia?", "Un punto cuántico semiconductor con confinamiento lateral y campo perpendicular. Es un referente para interpretar el modelo de un solo portador; no se construye."),
    ("¿Cuál es el objeto de estudio?", "No es la muestra: es la reconstrucción de los potenciales escalar y vectorial (o del campo) y las condiciones que la hacen posible o la limitan."),
    ("¿Quién observa y qué mide?", "En el laboratorio habría preparación, control y lectura indirecta. En el trabajo, un observador teórico-computacional prescribe datos ideales. Una simulación no es una medición."),
    ("¿Por qué 2D?", "Se congela el grado transversal cuando la separación en z es grande frente a las energías orbitales; queda la dinámica en x e y."),
    ("¿Qué es el espacio de Hilbert aquí?", "L²(D), el espacio abstracto de estados normalizables. No es el espacio físico ni un sistema de referencia."),
    ("¿Por qué Schrödinger y no Dirac?", "Se estudian excitaciones orbitales de una banda de masa efectiva aproximadamente parabólica, no un régimen de altas energías. m* describe la curvatura de la banda, no una masa en reposo relativista."),
    ("¿Por qué sin espín?", "Para aislar la reconstrucción orbital. El electrón tiene espín, pero Zeeman y espín-órbita quedan fuera del modelo mínimo y se declaran."),
    ("¿Por qué un potencial vectorial si se conoce B_z?", "El acoplamiento mínimo usa A; varias representaciones de gauge dan el mismo B_z = rot A."),
    ("¿Qué se reconstruye exactamente?", "Según los datos: V − E, B_z y una clase de gauge de A. No un vector A único en términos absolutos."),
    ("¿Por qué la densidad sola no basta?", "La ecuación inversa contiene el momento cinético u, ligado a la fase y a A; dos configuraciones pueden tener la misma densidad y campos distintos. El ejemplo: ignorar A en Fock–Darwin da Ω² en lugar de ω₀²."),
    ("¿Qué aporta Madelung?", "Separa continuidad y balance de energía, y hace explícitas las variables invariantes de gauge y los datos necesarios. No añade física nueva: reorganiza la de Schrödinger."),
    ("¿Diferencia entre cambio de gauge e indeterminación física?", "Un cambio de gauge (A → A + ∇χ, S → S + qχ) no cambia ningún observable. La degeneración Φ → Φ + F(P) con datos (P, S) sí cambia B_z: son campos físicamente distintos compatibles con los mismos datos incompletos."),
    ("¿Por qué (P, j) sí determina B_z?", "u = m j/P es invariante; donde S es regular, rot ∇S = 0, así que B_z = −(1/q)(rot u)_z. Es una reconstrucción local fuera de nodos, no un teorema global de unicidad."),
    ("¿Qué pasa en los nodos y vórtices?", "Si P = 0 no se evalúan cocientes por P. La circulación de ∇S alrededor de un vórtice es 2πℏℓ, y el rotacional de u tiene contribuciones concentradas (deltas) en los vórtices; el dominio queda perforado y las condiciones globales importan."),
    ("¿Dónde falla una afirmación ingenua de unicidad?", "Cuando faltan datos, frontera o circulación; cuando se confunde gauge con identificación física; o cuando se ignoran los nodos. Contar ecuaciones no basta."),
    ("¿Por qué Fock–Darwin?", "Solución exacta con estados sin nodo, con vórtice y con nodo radial: tres escenarios distintos en un mismo modelo. Para ω_c/ω₀ = 2, Ω² = 2ω₀²."),
    ("¿Para qué lo numérico si hay solución analítica?", "La solución exacta es el patrón: permite medir el error de discretización, la amplificación del ruido (∼ ε/h²), los errores de implementación y el efecto de los nodos."),
    ("¿Qué garantizan las pruebas?", "Solo lo declarado para los casos y dominios estudiados. Exactitud, convergencia y estabilidad frente al ruido son propiedades distintas."),
    ("¿Qué es lo nuevo?", "Precisar qué datos internos de un estado complejo determinan los potenciales, con el gauge y los nodos explícitos, y verificarlo en casos exactos. Si la revisión encuentra trabajos equivalentes, compararlos con precisión también es aporte."),
    ("¿Por qué Barad y Latour en un trabajo de física?", "Porque el problema muestra con precisión que lo reconstruido depende de qué se toma como dato. Es una discusión complementaria, ligada a decisiones documentadas; no reemplaza la demostración física. Si una categoría no aporta, se reporta."),
    ("¿Por qué monografía y no investigación?", "El aporte es analítico y documental; no requiere grupo, convocatoria (Art. 20) ni estancia."),
]

FORMULAS = [
    ("Hamiltoniano", "Ĥ = (1/2m)[−iℏ∇ − qA]² + V,  Ĥψ = Eψ"),
    ("Madelung", "ψ = √P e^{iS/ℏ},  u = ∇S − qA,  j = P u / m"),
    ("Continuidad", "∇·(P u) = 0"),
    ("Ecuación maestra", "V − E = (ℏ²/2m) ∇²√P/√P − |u|²/2m = −|u|²/2m + (ℏ²/4m)[∇²P/P − ½|∇P|²/P²]"),
    ("Caso (P, j)", "u = m j/P,  B_z = −(1/q)(∇×u)_z  (fuera de nodos)"),
    ("Caso (P, S), Coulomb", "A = ∇⊥Φ,  B_z = −∇²Φ,  q{P, Φ} = ∇·(P∇S);  Φ → Φ + F(P) cambia B_z en −∇²F(P)"),
    ("Fock–Darwin", "ω_c = qB_z/m,  Ω² = ω₀² + ω_c²/4,  E = ℏΩ(2n + |ℓ| + 1) − ½ℏω_c ℓ"),
    ("Control (0,0)", "V − E = −ℏΩ + (m/2)(Ω² − ω_c²/4) r² = −ℏΩ + ½mω₀²r²;  sin |qA|² queda Ω²"),
    ("Vórtice", "∮∇S·dℓ = 2πℏℓ"),
    ("Numérico", "error de truncamiento ∼ h²; ruido amplificado ∼ ε/h²;  p_obs ≈ log₂[ε(h)/ε(h/2)]"),
]

CSS_GUION = f"""
@page {{ size: letter; margin: .75in .8in .8in;
  @bottom-right {{ content: counter(page) " / " counter(pages); font: 9pt "Noto Sans"; color: {GRIS} }}
  @bottom-left {{ content: "Guion de la defensa · J. S. Sánchez Álvarez"; font: 9pt "Noto Sans"; color: {GRIS} }} }}
body {{ font-family: "Noto Sans"; color: #1a2433; font-size: 10.6pt; line-height: 1.45; -webkit-print-color-adjust: exact; print-color-adjust: exact }}
h1 {{ color: {NAVY}; font-size: 20pt; margin: 0 0 .05in }} h2 {{ color: {NAVY}; font-size: 14pt; margin: .26in 0 .08in; border-bottom: 2px solid {OCHRE}; padding-bottom: .03in }}
.meta {{ color: {GRIS}; margin-bottom: .14in }}
table {{ border-collapse: collapse; width: 100% }} th {{ background: {NAVY}; color: #fff; text-align: left; padding: 4px 7px; font-weight: 600 }}
td {{ border-bottom: 1px solid #dde3e8; padding: 4px 7px; vertical-align: top }}
.blk {{ break-inside: avoid; border: 1px solid #d8dee4; border-radius: 9px; margin: .12in 0; overflow: hidden }}
.bh {{ background: #eaf4f3; padding: 5px 10px; display: flex; justify-content: space-between; font-weight: 700; color: {NAVY} }}
.bh span:last-child {{ color: {TEAL}; font-weight: 600 }}
.say {{ padding: 8px 12px; font-size: 11.6pt; line-height: 1.55 }}
.note {{ padding: 6px 12px 8px; font-size: 9.8pt; color: #3b4757; background: #fbf7ee; border-top: 1px dashed #e2cfa8 }}
.note b {{ color: {OCHRE} }}
.qa dt {{ font-weight: 700; color: {NAVY}; margin-top: .08in }} .qa dd {{ margin: .02in 0 0 .18in }}
.box {{ background: #f1f5f7; border-left: 5px solid {TEAL}; padding: 8px 12px; border-radius: 6px; margin: .1in 0 }}
code {{ font-family: "Noto Sans"; font-size: 10.2pt }}
"""


def palabras(t):
    return len(t.split())


def html_guion():
    acum, filas = 0, []
    tot_w = 0
    for i, s in enumerate(LAMINAS, 1):
        w = palabras(s["guion"]); tot_w += w
        acum += s["seg"]
        filas.append(f"<tr><td>{i}</td><td>{s['titulo']}</td><td>{s['seg']} s</td><td>{acum//60}:{acum%60:02d}</td>"
                     f"<td>{w}</td><td>{w/130*60:.0f} s</td></tr>")
    est = tot_w / 130 * 60
    bloques = []
    acum = 0
    for i, s in enumerate(LAMINAS, 1):
        acum += s["seg"]
        nota = f'<div class="note"><b>Si preguntan / notas:</b> {s["notas"]}</div>' if s["notas"] else ""
        bloques.append(f'<div class="blk"><div class="bh"><span>Lámina {i} · {s["titulo"]}</span>'
                       f'<span>{s["seg"]} s · termina en {acum//60}:{acum%60:02d}</span></div>'
                       f'<div class="say">{s["guion"]}</div>{nota}</div>')
    qa = "".join(f"<dt>{k}. {p}</dt><dd>{r}</dd>" for k, (p, r) in enumerate(PREGUNTAS, 1))
    fo = "".join(f"<tr><td><b>{a}</b></td><td>{b}</td></tr>" for a, b in FORMULAS)
    return f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><title>Guion</title><style>{CSS_GUION}</style></head><body>
<h1>Guion de la sustentación de la propuesta</h1>
<div class="meta">Juan Sebastián Sánchez Álvarez · Director: Prof. John Hernán Díaz Forero · Consejo Curricular, 24 de noviembre de 2026 · Máximo 10 minutos</div>
<div class="box">La estructura sigue la guía del director: presentación, modalidad, cuatro láminas de planteamiento físico, estado del
arte, pregunta, metodología, objetivos, cronograma y cierre. El texto está escrito para decirse en voz alta; las fórmulas
están en las láminas y se nombran en palabras. El documento orientador del director (formulación física, 24 páginas) es la
base de las respuestas del anexo A.</div>
<h2>Tiempos</h2>
<table><tr><th>#</th><th>Lámina</th><th>Asignado</th><th>Acumulado</th><th>Palabras</th><th>A 130 ppm</th></tr>{''.join(filas)}
<tr><td></td><td><b>Total</b></td><td><b>{sum(s['seg'] for s in LAMINAS)} s</b></td><td></td><td><b>{tot_w}</b></td><td><b>{est:.0f} s</b></td></tr></table>
<p>A un ritmo pausado (130 palabras por minuto) el guion dura unos <b>{est/60:.1f} minutos</b>. Puntos de control: terminar la
lámina 6 antes de los <b>4:30</b> y la lámina 9 antes de los <b>7:15</b>. Si vas atrasado, recorta en la lámina 4 la frase sobre la
acción característica y en la lámina 6 la frase del control con Fock–Darwin (dila solo si preguntan).</p>
<h2>Texto por lámina</h2>{''.join(bloques)}
<h2>Anexo A. Preguntas probables y respuestas cortas</h2>
<p>Basadas en la sección 12 del documento orientador del director y en la propuesta. Responde en dos o tres frases y ofrece el detalle si lo piden.</p>
<dl class="qa">{qa}</dl>
<h2>Anexo B. Fórmulas y números de referencia</h2>
<table>{fo}</table>
<table style="margin-top:.12in"><tr><th colspan="2">Escalas ilustrativas (m* = 0,067 mₑ, ℏω₀ = 2 meV, |B_z| = 1 T), verificadas</th></tr>
<tr><td>ω₀ = E₀/ℏ</td><td>3,04 × 10¹² s⁻¹</td></tr><tr><td>a₀ = (ℏ/m*ω₀)^½</td><td>23,85 nm</td></tr>
<tr><td>ω_c = e|B|/m*</td><td>2,63 × 10¹² s⁻¹ (ℏω_c = 1,73 meV)</td></tr><tr><td>ℓ_B = (ℏ/e|B|)^½</td><td>25,66 nm</td></tr>
<tr><td>Ω = (ω₀² + ω_c²/4)^½</td><td>3,31 × 10¹² s⁻¹ (a = 22,85 nm)</td></tr><tr><td>T₀ = 2π/ω₀</td><td>2,07 ps</td></tr></table>
<p>Son ejemplos de orden de magnitud, no mediciones propias. En la monografía se trabaja con razones adimensionales, como ω_c/ω₀ = 2.</p>
<h2>Anexo C. Plan de ensayo</h2>
<ol><li>Ensaya tres o cuatro veces con cronómetro, en voz alta y de pie.</li>
<li>Graba un ensayo completo en Microsoft Teams, de máximo 10 minutos, y envíalo al profesor Díaz.</li>
<li>Lunes 23 de noviembre: ensayos con el director; anota sus ajustes en este guion.</li>
<li>Martes 24 de noviembre: sustentación ante el Consejo Curricular. Lleva el PDF de la presentación y una copia en USB.</li></ol>
</body></html>"""


# ------------------------------------------------------------------ salida
def chromium():
    for c in ("chrome-headless-shell", "chromium", "chromium-browser", "google-chrome"):
        p = shutil.which(c)
        if p:
            return p
    base = "/inner_container/opt/playwright"
    for raiz, _, archivos in os.walk(base) if os.path.isdir(base) else []:
        if "chrome-headless-shell" in archivos:
            return os.path.join(raiz, "chrome-headless-shell")
    return None


def imprimir(html, pdf):
    exe = chromium()
    if not exe:
        print(f"No se encontró Chromium; abre {html} en un navegador e imprime a PDF.")
        return
    subprocess.run([exe, "--no-sandbox", "--disable-gpu", "--headless", f"--print-to-pdf={pdf}",
                    "--no-pdf-header-footer", "file://" + html], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=180)
    print("escrito", pdf)


if __name__ == "__main__":
    for nombre, contenido in (("presentacion", glifos(html_presentacion())), ("guion", glifos(html_guion()))):
        h = os.path.join(AQUI, nombre + ".html")
        with open(h, "w", encoding="utf-8") as f:
            f.write(contenido)
        imprimir(h, os.path.join(AQUI, nombre + ".pdf"))
    tot = sum(palabras(s["guion"]) for s in LAMINAS)
    print(f"láminas: {len(LAMINAS)}; asignado {sum(s['seg'] for s in LAMINAS)} s; guion {tot} palabras = {tot/130*60:.0f} s a 130 ppm")
