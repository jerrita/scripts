{
  description = "A collection of scripts by jerrita";

  inputs.nixpkgs.follows = "nixpkgs";
  outputs = { self, nixpkgs }: {
    nixosModules.ddns = import ./nix/ddns.nix;
  };
}
