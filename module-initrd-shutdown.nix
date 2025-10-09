{ config, lib, pkgs, ... }:
let
    cfg = config.services.initrd-shutdown;
in {
  imports = [ ];

  # https://systemd.io/DEBUGGING/
  # https://blog.decent.id/post/nixos-systemd-initrd/
  # https://discourse.nixos.org/t/migrating-to-boot-initrd-systemd-and-debugging-stage-1-systemd-services/54444/2

  # https://www.freedesktop.org/software/systemd/man/latest/bootup.html#Bootup%20in%20the%20initrd

  options = {
     services.initrd-shutdown = {
       enable = lib.mkOption {
         default = false;
         type = with lib.types; bool;
         description = ''
           Shutdown the machine if on initrd / luks unlock too long.
         '';
       };
     }; };


   config = lib.mkIf cfg.enable {
     boot.initrd.systemd.services.initrd-shutdown = {
       wantedBy = [ "initrd.target" ]; 
       #DefaultDependencies = "no";
       #after = [ "network.target" ];
       description = "Shut down the device if stalled on the password prompt for too long.";
       before = [ "sysroot.mount" ];
       unitConfig.DefaultDependencies = "no";
       serviceConfig = {
          Type = "oneshot";
          StandardOutput="tty";
      };
      script = ''
        set -o pipefail

        DURATION=40
        COUNTDOWN=20
        GRACEPERIOD=10

        echo "Shutdown in $DURATION s." | systemd-cat -t initrd-shutdown
        echo -e "\nShutdown in $DURATION s.\n"

        for i in $(seq 1 $DURATION);
        do
            sleep 1

            # display time left.
            TIMELEFT=$((DURATION-i))
            if [ $TIMELEFT -lt $COUNTDOWN ]; then
              if (( i % 5 == 0 )); then
                echo "Shutdown in $TIMELEFT s."
                echo "Shutdown in $TIMELEFT s." | systemd-cat -t initrd-shutdown
              fi
            fi

            # Check if the root device is reached (decryption key entered)
            set +e
            BASICTARGET=$(systemctl check initrd-root-device.target)
            set -e
            if [[ "$BASICTARGET" == "active" ]]; then
              # Shut down this systemd service to prevent blocking the boot.
              echo "Reached initrd root device, stopping shutdown timer."
              echo "Reached initrd root device, stopping shutdown timer." | systemd-cat -t initrd-shutdown
              exit 0
            fi
        done

        # extra 10s grace period, in case we fall through the above loop for some reason.
        echo "Final $GRACEPERIOD second sleep."
        echo "Final $GRACEPERIOD second sleep." | systemd-cat -t initrd-shutdown
        sleep $GRACEPERIOD

        echo "Shutting down."
        echo "Shutting down." | systemd-cat -t initrd-shutdown

        # actually shut down the system.
        systemctl poweroff
      '';
     };
   };
}
