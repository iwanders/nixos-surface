{ config, lib, pkgs, ... }:

let cfg = config.services.thermald;
in {
  imports = [ ];

  options = { };

  config = {
    services.thermald.enable = true;
    services.thermald.debug = true;
    services.thermald.configFile = ./thermald/thermal-conf.xml;

    #systemd.services.thermald.serviceConfig.ExecStart = lib.mkForce  ''
    #  ${cfg.package}/sbin/thermald \
    #    --no-daemon \
    #    ${lib.optionalString cfg.debug "--loglevel=debug"} \
    #    ${lib.optionalString (cfg.configFile != null) "--config-file ${cfg.configFile}"} \
    #    --dbus-enable \
    #    --adaptive \
    #    --ignore-default-control
    #'';
  };
}
