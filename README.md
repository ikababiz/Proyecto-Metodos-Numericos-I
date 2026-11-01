# Proyecto-Metodos-Numericos-I
Repositorio para el proyecto de métodos numéricos I.

## Requisitos 
- Se necesita Python instalado y las respectivas bibliotecas.  
- En requirements.txt vienen todas las bibliotecas necesarias para el proyecto.  
- Para la renderización correcta de las ventanas es necesario tener como mínimo MiKTeX Basic descargable en https://miktex.org/download  
Durante la instalación, es necesario marcar "Install missing packages on-the-fly" como "Yes". Un reinicio del sistema puede ser necesario después de instalar.  
- El ejecutable .exe no requiere Python, bibliotecas ni entornos virtuales; todo viene empaquetado, cualquier archivo adicional puede ser leído al estar ubicado en la misma carpeta que el resto del proyecto.  

**Linux / macOS:**
```bash
git clone https://github.com/ikababiz/Proyecto-Metodos-Numericos-I.git  
cd Proyecto-Metodos-Numericos-I
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Windows:**
```powershell
git clone https://github.com/ikababiz/Proyecto-Metodos-Numericos-I.git
cd Proyecto-Metodos-Numericos-I
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Estructura del repositorio  
├── main.py                  ← menú principal  
├── README.md                ← introducción al repositorio  
├── requirements.txt         ← bibliotecas necesarias a instalar (PySide6, Qt Designer, SymPy, NumPy, etc...)  
├── .gitignore               ← los archivos más pesados que no se comparten  
├── ejemplos/                ← Lo primero que subí  
│   ├── TestGUI.py  
│   ├── Asistencia.py  
│   └── graficador.py  
├── recursos/  
│   ├── ExampleGUI.ui  
│   └── resources_rc.py      ← para imágenes  
├── unidad2/                 ← WIP   
│   ├── menu_unidad2.py      ← menú de la unidad  
│   ├── biseccion.py  
│   ├── regula_falsi.py  
│   ├── newton.py  
│   └── secante.py  
├── unidad3/  
│   ├── Gauss.py  
│   ├── Jacobi.py  
├── unidad4/  
│   ├── Doolittle.py  
└── unidad5/  
