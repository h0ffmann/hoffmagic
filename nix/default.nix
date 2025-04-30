{ lib, pkgs ? import <nixpkgs> {}, pythonPackages ? pkgs.python312Packages }:

let
  python = pkgs.python312;
in

pythonPackages.buildPythonPackage rec {
  pname = "hoffmagic";
  version = "0.1.0";
  format = "pyproject";

  src = ../.;

  nativeBuildInputs = with pythonPackages; [
    setuptools
    hatchling
  ];

  propagatedBuildInputs = with pythonPackages; [
    fastapi
    uvicorn
    jinja2
    sqlalchemy
    alembic
    pydantic
    psycopg
    python-multipart
    markdown
    pygments
    pillow
    python-frontmatter
    email-validator
    typer
    rich
  ];

  checkInputs = with pythonPackages; [
    pytest
    pytest-cov
  ];

  meta = with lib; {
    description = "A beautiful Python-based blog application";
    homepage = "https://github.com/yourusername/hoffmagic";
    license = licenses.mit;
    maintainers = with maintainers; [ ];
  };
}
