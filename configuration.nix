# man 5 configuration.nix
# nixos-help
{ config, pkgs, lib, ... }:
let
  unstableTarball = fetchTarball
    "https://github.com/NixOS/nixpkgs-channels/archive/nixos-unstable.tar.gz";
  unstable = import unstableTarball { config = config.nixpkgs.config; };
  packages = import ./packages.nix { inherit pkgs unstable; };
in {
  imports = [
    ./hardware-configuration.nix

    ./git.nix
    ./plasma5.nix
    ./yubikey.nix
    ./this.nix
  ];

  boot.loader.systemd-boot.enable = true;
  boot.loader.efi.canTouchEfiVariables = true;
  boot.loader.grub.useOSProber = true;
  boot.loader.grub.configurationLimit = 10;
  boot.kernelPackages = pkgs.linuxPackages_latest;
  # Set the font earlier in the boot process.
  boot.earlyVconsoleSetup = true;
  boot.tmpOnTmpfs = true; # Keep /tmp in RAM

  hardware.enableRedistributableFirmware = true;

  networking.networkmanager.enable = true;
  networking.nameservers = [ "8.8.8.8" "8.8.4.4" ];
  networking.firewall.allowedTCPPorts = [ 80 443 ];
  networking.firewall.enable = false;

  services.printing.enable = true;
  services.printing.drivers = [ pkgs.hplip ];

  services.thermald.enable = true;

  sound.enable = true;
  hardware.pulseaudio.enable = true;

  i18n = {
    # Note: We don't set a font because sometimes the generated
    # hardware-configuration.nix picks a better (larger) one for high-DPI displays.
    consoleKeyMap = "us";
    defaultLocale = "en_US.UTF-8";
    inputMethod = {
      enabled = "ibus";
      ibus.engines = with pkgs.ibus-engines; [ uniemoji typing-booster ];
    };
  };

  time = {
    timeZone = "America/New_York";
    # Don't confuse windows with a UTC timestamp.
    hardwareClockInLocalTime = true;
  };

  # Don't forget to set a password with ‘passwd’.
  users.users.becca = {
    isNormalUser = true;
    extraGroups = [
      "wheel" # Enable ‘sudo’ for the user.
      "audio"
      "sound" # Not sure if these are necessary.
      "video" # Not sure if this is necessary.
      "networkmanager"
    ];
    shell = "/run/current-system/sw/bin/fish";
  };

  # Passwordless sudo
  security.sudo.wheelNeedsPassword = false;

  services.emacs = {
    enable = true;
    defaultEditor = true;
    package = import ./pkg/emacs { inherit (pkgs) emacs; };
  };

  programs.fish.enable = true;

  nixpkgs.config = { allowUnfree = true; };
  environment.systemPackages = packages.all;

  nix = {
    trustedBinaryCaches =
      [ "https://cache.nixos.org" "https://all-hies.cachix.org" ];
    binaryCachePublicKeys = [
      "cache.nixos.org-1:6NCHdD59X431o0gWypbMrAURkbJ16ZPMQFGspcDShjY="
      "all-hies.cachix.org-1:JjrzAOEUsD9ZMt8fdFbzo3jNAyEWlPAwdVuHw4RD43k="
    ];
    trustedUsers = [ "root" "becca" ];
  };

  fonts = {
    enableDefaultFonts = true;
    fontconfig.defaultFonts = {
      emoji = [ "Twitter Color Emoji" ];
      monospace = [ "PragmataPro Mono Liga" ];
    };
  };

  # This value determines the NixOS release with which your system is to be
  # compatible, in order to avoid breaking some software such as database
  # servers. You should change this only after NixOS release notes say you

  system.stateVersion = "19.09"; # Did you read the comment?
}
