from setuptools import setup, find_packages

setup(
    name="gestor_herramientas",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "stramlit>=1.0.0",
        "sqlmodel>=0.0.31",
        "sqlalchemy>=2.0.0",
        "pydantic>=2.0.0",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "gho=frontend.main:main",
        ],
    },
    author="LeGuts",
    description="Gestor de Herramientas y Objetos",
)
