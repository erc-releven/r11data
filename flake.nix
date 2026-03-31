{
  description = "r11data dev shell for uv + numpy/pandas on NixOS";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs = { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs { inherit system; };

      libPath = pkgs.lib.makeLibraryPath [
        pkgs.stdenv.cc.cc.lib
        pkgs.zlib
      ];
    in {
      devShells.${system}.default = pkgs.mkShell {
        packages = with pkgs; [
          uv
          python312
          gcc
        ];

        NIX_LD = pkgs.lib.fileContents "${pkgs.stdenv.cc}/nix-support/dynamic-linker";
        LD_LIBRARY_PATH = libPath;
      };
    };
}
