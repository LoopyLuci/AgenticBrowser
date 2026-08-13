{
  "description": "AgenticBrowser dev shell",
  "inputs": {
    "nixpkgs": { "url": "github:NixOS/nixpkgs/nixos-unstable" }
  },
  "outputs": { self, nixpkgs }: 
  let
    system = "x86_64-linux";
    pkgs = nixpkgs.legacyPackages.${system};
    pythonPackages = pkgs.python312.withPackages (ps: [
      ps.fastapi
      ps.uvicorn
      ps.httpx
      ps.pydantic
      ps.cryptography
    ]);
    nodePackages = pkgs.nodejs_20;
  in {
    devShells.${system}.default = pkgs.mkShell {
      buildInputs = [
        pythonPackages
        nodePackages
        pkgs.nodePackages.playwright
        pkgs.git
        pkgs.curl
        pkgs.openssl
      ];
      shellHook = ''
        echo "AgenticBrowser dev shell"
        echo "Backend: uvicorn main:app --port 8123"
        echo "Web UI: cd agentic-browser-web-ui && npm run dev"
        echo "Extension: cd agentic-browser-extension && npm run build"
      '';
    };
  };
}
