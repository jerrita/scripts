{ config, lib, pkgs, ... }:

with lib;

let
  src = ../.;
  cfg = config.services.ddns;
  pythonEnv = pkgs.python311.withPackages (ps: with ps; [
    netifaces
    requests
    dnspython
  ]);
in
{
  options.services.ddns = {
    enable = mkEnableOption "Jerrita's DDNS service";

    interval = mkOption {
      type = types.str;
      default = "5m";
      description = "Interval between runs of the DDNS script.";
    };

    apiToken = mkOption {
      type = types.str;
      default = "";
      description = "Cloudflare API token.";
    };

    domain = mkOption {
      type = types.str;
      default = "";
      description = "The domain for the DDNS update.";
    };

    zone = mkOption {
      type = types.str;
      default = "";
      description = "The zone for the Cloudflare.";
    };

    nicName = mkOption {
      type = types.str;
      default = "";
      description = "The nic name to get ip address.";
    };
  };

  config = mkIf cfg.enable {
    systemd.timers.ddns = {
      wantedBy = [ "timers.target" ];
      timerConfig = {
        OnBootSec = "10s";
        OnUnitActiveSec = cfg.interval;
      };
    };

    systemd.services.ddns = {
      script = "${pythonEnv}/bin/python ${src}/src/ddns.py";
      serviceConfig = {
        Type = "oneshot";
        Environment = [
          "CF_API_TOKEN=${cfg.apiToken}"
          "DOMAIN=${cfg.domain}"
          "ZONE=${cfg.zone}"
          "NIC_NAME=${cfg.nicName}"
        ];
      };
    };

    environment.systemPackages = [ pythonEnv ];
  };
}
