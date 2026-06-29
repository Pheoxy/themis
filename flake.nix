{
  description = "Themis: paranoid upstream PR validation for AI-assisted code submissions";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs =
    { self, nixpkgs }:
    let
      systems = [
        "x86_64-linux"
        "aarch64-linux"
      ];
      forAllSystems = nixpkgs.lib.genAttrs systems;
    in
    {
      packages = forAllSystems (
        system:
        let
          pkgs = import nixpkgs { inherit system; };
          python = pkgs.python311;
        in
        {
          default = python.pkgs.buildPythonApplication {
            pname = "themis";
            version = "0.1.0";
            pyproject = true;
            src = ./.;

            build-system = [ python.pkgs.setuptools ];
            nativeBuildInputs = [ pkgs.makeWrapper ];
            nativeCheckInputs = [ pkgs.git ];

            postInstall = ''
              wrapProgram $out/bin/themis \
                --prefix PATH : ${pkgs.lib.makeBinPath [ pkgs.git pkgs.gh ]}
            '';

            checkPhase = ''
              runHook preCheck
              PYTHONPATH=$PWD/src python -m unittest discover -s tests
              PYTHONPATH=$PWD/src python -m themis docs cli --check
              runHook postCheck
            '';
          };
        }
      );

      checks = forAllSystems (
        system:
        let
          pkgs = import nixpkgs { inherit system; };
          python = pkgs.python311;
        in
        {
          default = self.packages.${system}.default;
          unit-tests = pkgs.runCommand "themis-unit-tests" { nativeBuildInputs = [ python pkgs.git ]; } ''
            cd ${self}
            PYTHONPATH=${self}/src python -m unittest discover -s tests
            touch $out
          '';
          cli-docs = pkgs.runCommand "themis-cli-docs" { nativeBuildInputs = [ python ]; } ''
            cd ${self}
            PYTHONPATH=${self}/src python -m themis docs cli --check
            touch $out
          '';
          config-check = pkgs.runCommand "themis-config-check" { nativeBuildInputs = [ python pkgs.git ]; } ''
            cd ${self}
            PYTHONPATH=${self}/src python -m themis config check
            touch $out
          '';
          release-check = pkgs.runCommand "themis-release-check" { nativeBuildInputs = [ python pkgs.git ]; } ''
            cd ${self}
            PYTHONPATH=${self}/src python -m themis release check
            touch $out
          '';
        }
      );

      apps = forAllSystems (system: {
        default = {
          type = "app";
          program = "${self.packages.${system}.default}/bin/themis";
          meta.description = "Themis: paranoid upstream PR validation for AI-assisted code submissions";
        };
      });

      devShells = forAllSystems (
        system:
        let
          pkgs = import nixpkgs { inherit system; };
        in
        {
          default = pkgs.mkShell {
            packages = [
              pkgs.gh
              pkgs.git
              pkgs.python311
            ];

            shellHook = ''
              export PYTHONPATH="$PWD/src''${PYTHONPATH:+:$PYTHONPATH}"
            '';
          };
        }
      );
    };
}
