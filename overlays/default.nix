{
  unstable = import ./unstable.nix;
  cargo = import ./cargo.nix;
  emacs = import ./emacs.nix;
  nvim = import ./nvim.nix;
  mathematica = import ./mathematica.nix;
  rebecca = import ./rebeccapkgs.nix;
}
