{ config, lib, pkgs, ... }:

with lib;

let
  cfg = config.services.ddns;
  pythonEnv = pkgs.python3.withPackages (ps: with ps; [
    (ps.requirement "${../../requirements.txt}")
  ]);
in
{
  options.services.ddns = {
    enable = mkEnableOption "Jerrita's DDNS service";

    interval = mkOption {
      type = types.str;
      default = "5min";
      description = "Interval between runs of the DDNS script.";
    };
  };

  config = mkIf cfg.enable {
    systemd.timers.myddnsTimer = {
      wantedBy = [ "timers.target" ];
      timerConfig.OnCalendar = "*:0/${toString (div (toMinutes cfg.interval) 5)}";
    };

    systemd.services.myddnsService = {
      script = "${pythonEnv}/bin/python ${../../src/ddns.py}";
      serviceConfig = {
        Type = "oneshot";
      };
      wantedBy = [ "myddnsTimer.timer" ];
    };

    environment.systemPackages = [ pythonEnv ];
  };
}
