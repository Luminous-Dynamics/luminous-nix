{ config, lib, pkgs, ... }:

with lib;

let
  cfg = config.services.luminous-healing;
  
  # Python package for luminous-nix
  luminousNixPackage = pkgs.python3Packages.buildPythonPackage rec {
    pname = "luminous-nix";
    version = "2.0.0";
    
    src = ../..;
    
    format = "pyproject";
    
    nativeBuildInputs = with pkgs.python3Packages; [
      poetry-core
    ];
    
    propagatedBuildInputs = with pkgs.python3Packages; [
      aiofiles
      asyncio
      psutil
      prometheus-client
      pyyaml
      rich
      textual
      typer
    ];
    
    doCheck = false;  # Tests require special environment
    
    meta = {
      description = "Self-healing system for NixOS with simplified V2 architecture";
      homepage = "https://github.com/Luminous-Dynamics/luminous-nix";
      license = licenses.mit;
      maintainers = [ "Luminous Dynamics Team" ];
    };
  };
  
  # Configuration file for the service
  configFile = pkgs.writeText "luminous-healing.yaml" ''
    thresholds:
      cpu_percent: ${toString cfg.thresholds.cpu}
      memory_percent: ${toString cfg.thresholds.memory}
      disk_percent: ${toString cfg.thresholds.disk}
      load_average: ${toString cfg.thresholds.loadAverage}
    
    healing:
      enabled: ${if cfg.healing.enabled then "true" else "false"}
      dry_run: ${if cfg.healing.dryRun then "true" else "false"}
      
    monitoring:
      interval: ${toString cfg.monitoring.interval}
      metrics_port: ${toString cfg.monitoring.metricsPort}
      dashboard_port: ${toString cfg.monitoring.dashboardPort}
      
    predictive:
      enabled: ${if cfg.predictive.enabled then "true" else "false"}
      history_size: ${toString cfg.predictive.historySize}
      
    services:
      ${concatStringsSep "\n  " (map (s: "- ${s}") cfg.services.monitored)}
  '';
  
  # SystemD service script
  healingScript = pkgs.writeScript "luminous-healing" ''
    #!${pkgs.python3}/bin/python3
    
    import asyncio
    import logging
    import yaml
    import sys
    import os
    
    # Add package to path
    sys.path.insert(0, "${luminousNixPackage}/${pkgs.python3.sitePackages}")
    
    from luminous_nix.self_healing import SimplifiedHealingEngine
    from luminous_nix.self_healing.predictive_maintenance import PredictiveHealingEngine
    from luminous_nix.self_healing import MetricsServer
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    async def main():
        # Load configuration
        with open("${configFile}", 'r') as f:
            config = yaml.safe_load(f)
        
        # Create healing engine
        engine = SimplifiedHealingEngine()
        
        # Apply thresholds
        engine.detector.thresholds = config['thresholds']
        
        # Configure healing
        engine.healing_enabled = config['healing']['enabled']
        engine.dry_run = config['healing']['dry_run']
        
        # Start metrics server if enabled
        if ${if cfg.monitoring.enableMetrics then "True" else "False"}:
            metrics_server = MetricsServer(
                healing_engine=engine,
                host='0.0.0.0',
                port=config['monitoring']['metrics_port']
            )
            asyncio.create_task(metrics_server.start())
            logger.info(f"Metrics server started on port {config['monitoring']['metrics_port']}")
        
        # Start predictive maintenance if enabled
        if config['predictive']['enabled']:
            predictive = PredictiveHealingEngine(engine)
            asyncio.create_task(predictive.monitor_and_predict(
                interval=config['monitoring']['interval']
            ))
            logger.info("Predictive maintenance enabled")
        
        # Start monitoring
        logger.info(f"Starting self-healing monitoring (interval: {config['monitoring']['interval']}s)")
        await engine.start_monitoring(interval=config['monitoring']['interval'])
    
    if __name__ == "__main__":
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            logger.info("Shutting down gracefully...")
  '';

in {
  ###### Interface
  options = {
    services.luminous-healing = {
      enable = mkEnableOption "Luminous Nix self-healing system";
      
      package = mkOption {
        type = types.package;
        default = luminousNixPackage;
        description = "The luminous-nix package to use";
      };
      
      user = mkOption {
        type = types.str;
        default = "luminous-healing";
        description = "User under which the service runs";
      };
      
      group = mkOption {
        type = types.str;
        default = "luminous-healing";
        description = "Group under which the service runs";
      };
      
      thresholds = {
        cpu = mkOption {
          type = types.int;
          default = 80;
          description = "CPU usage threshold percentage";
        };
        
        memory = mkOption {
          type = types.int;
          default = 85;
          description = "Memory usage threshold percentage";
        };
        
        disk = mkOption {
          type = types.int;
          default = 90;
          description = "Disk usage threshold percentage";
        };
        
        loadAverage = mkOption {
          type = types.float;
          default = 3.0;
          description = "System load average threshold";
        };
      };
      
      healing = {
        enabled = mkOption {
          type = types.bool;
          default = true;
          description = "Enable automatic healing actions";
        };
        
        dryRun = mkOption {
          type = types.bool;
          default = false;
          description = "Run in dry-run mode (no actual healing)";
        };
      };
      
      monitoring = {
        interval = mkOption {
          type = types.int;
          default = 60;
          description = "Monitoring interval in seconds";
        };
        
        enableMetrics = mkOption {
          type = types.bool;
          default = true;
          description = "Enable Prometheus metrics endpoint";
        };
        
        metricsPort = mkOption {
          type = types.port;
          default = 9090;
          description = "Port for Prometheus metrics";
        };
        
        enableDashboard = mkOption {
          type = types.bool;
          default = false;
          description = "Enable web dashboard";
        };
        
        dashboardPort = mkOption {
          type = types.port;
          default = 8080;
          description = "Port for web dashboard";
        };
      };
      
      predictive = {
        enabled = mkOption {
          type = types.bool;
          default = true;
          description = "Enable predictive maintenance";
        };
        
        historySize = mkOption {
          type = types.int;
          default = 100;
          description = "Number of historical data points to keep";
        };
      };
      
      services = {
        monitored = mkOption {
          type = types.listOf types.str;
          default = [ "nginx" "postgresql" "redis" ];
          description = "List of services to monitor";
        };
      };
      
      openFirewall = mkOption {
        type = types.bool;
        default = false;
        description = "Open firewall for metrics and dashboard ports";
      };
    };
  };
  
  ###### Implementation
  config = mkIf cfg.enable {
    # Create user and group
    users.users.${cfg.user} = {
      isSystemUser = true;
      group = cfg.group;
      description = "Luminous healing service user";
      home = "/var/lib/luminous-healing";
      createHome = true;
    };
    
    users.groups.${cfg.group} = {};
    
    # SystemD service
    systemd.services.luminous-healing = {
      description = "Luminous Nix Self-Healing System";
      wantedBy = [ "multi-user.target" ];
      after = [ "network.target" ];
      
      serviceConfig = {
        Type = "simple";
        User = cfg.user;
        Group = cfg.group;
        ExecStart = "${healingScript}";
        Restart = "on-failure";
        RestartSec = 10;
        
        # Permissions for healing actions
        AmbientCapabilities = [
          "CAP_SYS_ADMIN"  # For system management
          "CAP_NET_ADMIN"  # For network management
        ];
        
        # Security hardening
        PrivateTmp = true;
        ProtectSystem = "strict";
        ProtectHome = true;
        ReadWritePaths = [
          "/var/lib/luminous-healing"
          "/var/cache/luminous-nix"
        ];
        
        # Resource limits
        CPUQuota = "20%";
        MemoryLimit = "512M";
      };
      
      environment = {
        LUMINOUS_CONFIG = "${configFile}";
        PYTHONPATH = "${luminousNixPackage}/${pkgs.python3.sitePackages}";
      };
    };
    
    # Socket for privileged operations
    systemd.sockets.luminous-healing = {
      description = "Luminous healing socket";
      wantedBy = [ "sockets.target" ];
      
      socketConfig = {
        ListenStream = "/run/luminous-healing.sock";
        SocketMode = "0660";
        SocketUser = cfg.user;
        SocketGroup = cfg.group;
      };
    };
    
    # Firewall rules
    networking.firewall = mkIf cfg.openFirewall {
      allowedTCPPorts = []
        ++ optional cfg.monitoring.enableMetrics cfg.monitoring.metricsPort
        ++ optional cfg.monitoring.enableDashboard cfg.monitoring.dashboardPort;
    };
    
    # Create necessary directories
    systemd.tmpfiles.rules = [
      "d /var/lib/luminous-healing 0755 ${cfg.user} ${cfg.group} -"
      "d /var/cache/luminous-nix 0755 ${cfg.user} ${cfg.group} -"
      "d /var/log/luminous-healing 0755 ${cfg.user} ${cfg.group} -"
    ];
    
    # Environment packages (for manual testing)
    environment.systemPackages = [ luminousNixPackage ];
  };
}