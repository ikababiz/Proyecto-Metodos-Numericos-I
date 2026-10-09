# Proyecto-Metodos-Numericos-I
Repositorio para el proyecto de métodos numéricos I.

## Requisitos 
- Se necesita Python instalado y las respectivas bibliotecas.
- En requirements.txt vienen todas las bibliotecas necesarias para el proyecto.
```bash
git clone git@github.com:ikababiz/Proyecto-Metodos-Numericos-I.git
cd Proyecto-Metodos-Numericos-I
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Estructura del repositorio  
├── main.py                  ← menú principal  
├── README.md                ← introducción al repositorio  
├── requirements.txt         ← bibliotecas necesarias a instalar (PySide6, Qt Designer, etc...)  
├── .gitignore               ← los archivos más pesados que no se comparten  
├── ejemplos/                ← Lo primero que subí  
│   ├── TestGUI.py           ← **ESTE ES EL EJEMPLO IMPORTANTE**  
│   ├── Asistencia.py  
│   └── graficador.py  
├── recursos/  
│   ├── ExampleGUI.ui  
│   └── resources_rc.py      ← para imágenes  
├── unidad2/                 ← WIP  
│   ├── __init__.py  
│   ├── menu_unidad2.py      ← menú de la unidad  
│   ├── biseccion.py  
│   ├── regula_falsi.py  
│   ├── newton.py  
│   └── secante.py  
├── unidad3/  
├── unidad4/  
└── unidad5/  
