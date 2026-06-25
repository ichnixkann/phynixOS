{ pkgs, python3 }:
pkgs.python3Packages.buildPythonApplication {
  pname = "phynix-copilot";
  version = "0.1.0";
  src = ./.;

  propagatedBuildInputs = with pkgs.python3Packages; [
    smolagents
    huggingface-hub
    chromadb
    requests
    pydantic
  ];

  buildInputs = with pkgs; [
    python3
  ];

  postInstall = ''
    mkdir -p $out/bin
    cp cli.py $out/bin/pcopilot
    chmod +x $out/bin/pcopilot
  '';

  meta = {
    description = "PHYNIX OS Copilot — AI Assistant for NixOS Configuration";
    license = pkgs.lib.licenses.lgpl3Plus;
  };
}
