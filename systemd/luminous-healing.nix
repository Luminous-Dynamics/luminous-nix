# NixOS module for Luminous Healing Executor Service
# 
# This service runs with elevated privileges to execute healing actions
# requested by the unprivileged monitoring service.
#
# Installation:
# 1. Copy this file to /etc/nixos/luminous-healing.nix
# 2. Add to imports in configuration.nix:
#    imports = [ ./luminous-healing.nix ];
# 3. Enable the service:
#    services.luminous-healing.enable = true;
# 4. Run: sudo nixos-rebuild switch

{ config, lib, pkgs, ... }:

with lib;

let
  cfg = config.services.luminous-healing;
  
  # Python environment with required packages
  pythonEnv = pkgs.python3.withPackages (ps: with ps; [
    # Add any required Python packages here
  ]);
  
  # The service script
  healingExecutorScript = pkgs.writeScriptBin "luminous-healing-executor" ''
    #!${pythonEnv}/bin/python3
    ${builtins.readFile ./healing_executor_service.py}
  '';

in {
  options.services.luminous-healing = {
    enable = mkEnableOption "Luminous Nix Healing Executor Service";
    
    socketPath = mkOption {
      type = types.str;
      default = "/run/luminous-healing.sock";
      description = "Unix socket path for communication";
    };
    
    secretKey = mkOption {
      type = types.nullOr types.str;
      default = null;
      description = "Secret key for request signing (defaults to environment variable)";
    };
    
    user = mkOption {
      type = types.str;
      default = "luminous-healing";
      description = "User to run the service as";
    };
    
    group = mkOption {
      type = types.str;
      default = "luminous-healing";
      description = "Group for the service";
    };
    
    allowedUsers = mkOption {
      type = types.listOf types.str;
      default = [ ];
      description = "Users allowed to connect to the healing socket";
    };
  };
  
  config = mkIf cfg.enable {
    # Create user and group
    users.users.${cfg.user} = {
      isSystemUser = true;
      group = cfg.group;
      description = "Luminous Healing Executor";
    };
    
    users.groups.${cfg.group} = {
      members = cfg.allowedUsers;
    };
    
    # SystemD service
    systemd.services.luminous-healing = {
      description = "Luminous Nix Healing Executor Service";
      after = [ "network.target" ];
      wantedBy = [ "multi-user.target" ];
      
      serviceConfig = {
        Type = "simple";
        User = cfg.user;
        Group = cfg.group;
        
        # Run the service
        ExecStart = "${healingExecutorScript}/bin/luminous-healing-executor";
        
        # Restart policy
        Restart = "always";
        RestartSec = 10;
        
        # Security hardening
        PrivateTmp = true;
        ProtectSystem = "strict";
        ProtectHome = true;
        NoNewPrivileges = true;
        
        # Required paths
        ReadWritePaths = [
          "/etc/nixos"
          "/sys/devices/system/cpu"
          "/proc/sys/vm"
          "/var/log"
        ];
        
        # Capabilities needed for healing actions
        AmbientCapabilities = [
          "CAP_SYS_NICE"      # Process priority
          "CAP_KILL"          # Kill processes
          "CAP_NET_ADMIN"     # Network management
          "CAP_SYS_ADMIN"     # System administration
          "CAP_SYS_RESOURCE"  # Resource limits
        ];
        CapabilityBoundingSet = [
          "CAP_SYS_NICE"
          "CAP_KILL"
          "CAP_NET_ADMIN"
          "CAP_SYS_ADMIN"
          "CAP_SYS_RESOURCE"
        ];
        
        # Environment
        Environment = mkIf (cfg.secretKey != null) [
          "LUMINOUS_HEALING_SECRET=${cfg.secretKey}"
        ];
        
        # Logging
        StandardOutput = "journal";
        StandardError = "journal";
        SyslogIdentifier = "luminous-healing";
      };
      
      # Socket activation (optional)
      # This allows systemd to manage the socket lifecycle
      unitConfig = {
        RequiresMountsFor = [ "/run" ];
      };
    };
    
    # Socket unit (optional - for socket activation)
    systemd.sockets.luminous-healing = {
      description = "Luminous Healing Executor Socket";
      wantedBy = [ "sockets.target" ];
      
      socketConfig = {
        ListenStream = cfg.socketPath;
        SocketMode = "0660";
        SocketUser = cfg.user;
        SocketGroup = cfg.group;
        Accept = false;
      };
    };
    
    # Sudoers rules for the healing service
    # This allows the service to execute specific privileged commands
    security.sudo.extraRules = [{
      users = [ cfg.user ];
      commands = [
        {
          command = "${pkgs.systemd}/bin/systemctl restart *";
          options = [ "NOPASSWD" ];
        }
        {
          command = "${pkgs.systemd}/bin/systemctl stop *";
          options = [ "NOPASSWD" ];
        }
        {
          command = "${pkgs.systemd}/bin/systemctl start *";
          options = [ "NOPASSWD" ];
        }
        {
          command = "${pkgs.nixos-rebuild}/bin/nixos-rebuild switch";
          options = [ "NOPASSWD" ];
        }
        {
          command = "${pkgs.nixos-rebuild}/bin/nixos-rebuild switch --rollback";
          options = [ "NOPASSWD" ];
        }
        {
          command = "${pkgs.nix}/bin/nix-collect-garbage *";
          options = [ "NOPASSWD" ];
        }
      ];
    }];
    
    # Ensure log directory exists
    systemd.tmpfiles.rules = [
      "d /var/log/luminous-healing 0755 ${cfg.user} ${cfg.group} -"
    ];
  };
}