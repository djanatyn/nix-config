# Configuration for desktops; graphical computers for personal use.
{ config, pkgs, lib, ... }: {
  imports = [
    # See: /nix/var/nix/profiles/per-user/root/channels/nixos/nixpkgs/nixos/modules/virtualisation/openstack-config.nix
    <nixpkgs/nixos/modules/virtualisation/openstack-config.nix>
    ./common.nix
  ];

  systemd.services = {
    amazon-init.enable = false;
    apply-ec2-data.enable = false;
  };

  services.sshguard = { enable = true; };

  boot.kernelPackages = lib.mkDefault pkgs.linuxPackages_latest;

  users.mutableUsers = false;

  networking.firewall.allowedTCPPorts = [ 22 80 443 ];

  system.autoUpgrade.allowReboot = true;

  environment.systemPackages = with pkgs; [
    htop
    gitAndTools.gitFull
    gitAndTools.hub
    gitAndTools.delta
    git-lfs
    (neovim.override {
      withNodeJs = true;
      vimAlias = true;
    })
    fish
    tmux
    bind
    ncat
    fd
    fzf
    file
    wget
    rsync
    watchman
    zip
    unzip
    atool
    broot
    exa
    just
    bat
    ripgrep
    hexd
    jq
    shellcheck
    gcc
    gnumake
    rnix-lsp
    nixfmt
    any-nix-shell
    nodejs-12_x
    yarn
    (python38.withPackages (pypkgs:
      with pypkgs; [
        (black.overridePythonAttrs { doCheck = false; })
        mypy
        ptpython
        pytest
        pynvim
        requests
      ]))
  ];
}
