"""
inspeccionar_cycling.py: describe la estructura de los .mat del dataset de pedaleo
(Mendeley Data, "Two-target cycling task, primate motor cortex"; Russo et al.) SIN suponer nombres de campos.

    python inspeccionar_cycling.py ruta/al/archivo.mat [otro.mat ...]

Imprime, recursivamente, cada campo con su tipo, forma, dtype, fracción de NaN y rango.
Al final lista:
  - arreglos con 3 o más ejes (candidatos a tiempo x neurona x ensayo),
  - campos cuyo nombre contiene palabras clave relacionadas con las preguntas abiertas
    (sesión/fecha, unidad/canal, ensayo, suavizado, frecuencia de muestreo).
Archivos v5 con scipy.io.loadmat; archivos v7.3 (HDF5) con h5py (pip install h5py).
No decide nada: el resultado es la entrada para el análisis posterior.
"""
import sys

import numpy as np

MAX_PROF = 6
MAX_ELEM = 4
CLAVES = ("sess", "date", "day", "unit", "neuron", "chan", "elec", "array", "trial", "dist", "dir", "pos",
          "smooth", "kern", "bin", "fs", "rate", "time", "cond", "id")
arreglos_3d = []
campos_clave = []


def anotar(ruta, forma):
    nombre = ruta.split("/")[-1].split("[")[0].lower()
    if any(c in nombre for c in CLAVES):
        campos_clave.append((ruta, forma))
    if forma is not None and len(forma) >= 3:
        arreglos_3d.append((ruta, forma))


def describir(ruta, a, sangria):
    forma = tuple(a.shape)
    extra = ""
    if a.size and a.dtype.kind in "fiub":
        x = a.astype(float)
        nan = float(np.isnan(x).mean())
        if nan < 1.0:
            extra = f", nan = {nan:.3f}, rango [{np.nanmin(x):.4g}, {np.nanmax(x):.4g}]"
        else:
            extra = ", todo NaN"
    elif a.dtype.kind in "US":
        extra = f", ejemplo = {str(a.flat[0])[:40]!r}" if a.size else ""
    print(f"{sangria}{ruta.split('/')[-1]}: arreglo {a.dtype}, forma {forma}{extra}")
    anotar(ruta, forma)


def recorrer(ruta, obj, prof=0):
    sangria = "  " * prof
    nombre = ruta.split("/")[-1]
    if hasattr(obj, "_fieldnames"):                       # estructura de MATLAB
        print(f"{sangria}{nombre}: estructura con campos {list(obj._fieldnames)}")
        anotar(ruta, None)
        if prof < MAX_PROF:
            for c in obj._fieldnames:
                recorrer(f"{ruta}/{c}", getattr(obj, c), prof + 1)
    elif isinstance(obj, np.ndarray) and obj.dtype == object:     # celdas o arreglo de estructuras
        print(f"{sangria}{nombre}: arreglo de objetos, forma {obj.shape}")
        anotar(ruta, tuple(obj.shape))
        if prof < MAX_PROF:
            for i, el in enumerate(obj.flat):
                if i >= MAX_ELEM:
                    print(f"{sangria}  ... ({obj.size - MAX_ELEM} elementos más sin mostrar)")
                    break
                recorrer(f"{ruta}[{i}]", el, prof + 1)
    elif isinstance(obj, np.ndarray):
        describir(ruta, obj, sangria)
    else:
        print(f"{sangria}{nombre}: {type(obj).__name__} = {str(obj)[:60]!r}")
        anotar(ruta, None)


def inspeccionar_v5(path):
    from scipy.io import loadmat
    d = loadmat(path, squeeze_me=True, struct_as_record=False)
    for k, v in d.items():
        if k.startswith("__"):
            continue
        recorrer(k, v)


def inspeccionar_h5(path):
    import h5py
    with h5py.File(path, "r") as f:
        def visitar(nombre, o):
            if isinstance(o, h5py.Dataset):
                print(f"{nombre}: dataset {o.dtype}, forma {o.shape}")
                anotar(nombre, tuple(o.shape))
        f.visititems(visitar)
        print("(en v7.3, las estructuras y celdas de MATLAB aparecen como referencias; "
              "los ejes están en orden inverso al de MATLAB)")


def main(paths):
    for p in paths:
        print(f"\n===== {p} =====")
        try:
            inspeccionar_v5(p)
        except NotImplementedError:
            print("(formato v7.3: se usa h5py)")
            inspeccionar_h5(p)
    print("\n=== Arreglos con 3 o más ejes ===")
    for r, f in arreglos_3d:
        print(f"  {r}: {f}")
    print("\n=== Campos con palabras clave (sesión, unidad, ensayo, suavizado, muestreo...) ===")
    for r, f in campos_clave:
        print(f"  {r}: {f}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1:])
