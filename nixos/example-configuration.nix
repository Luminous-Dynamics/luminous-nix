# Example NixOS configuration using the Luminous Healing module
{ config, pkgs, ... }:

{
  # Import the luminous-healing module
  imports = [
    ./modules/luminous-healing.nix
  ];
  
  # Enable and configure the self-healing service
  services.luminous-healing = {
    enable = true;
    
    # Adjust thresholds for your system
    thresholds = {
      cpu = 75;        # Alert at 75% CPU
      memory = 80;     # Alert at 80% memory
      disk = 85;       # Alert at 85% disk
      loadAverage = 2.5;
    };
    
    # Healing configuration
    healing = {
      enabled = true;   # Enable automatic healing
      dryRun = false;   # Actually perform healing (not just report)
    };
    
    # Monitoring settings
    monitoring = {
      interval = 60;           # Check every minute
      enableMetrics = true;    # Expose Prometheus metrics
      metricsPort = 9090;      
      enableDashboard = true;  # Enable web dashboard
      dashboardPort = 8080;
    };
    
    # Predictive maintenance
    predictive = {
      enabled = true;
      historySize = 200;  # Keep more history for better predictions
    };
    
    # Services to monitor
    services.monitored = [
      "nginx"
      "postgresql"
      "redis"
      "gitea"
      "grafana"
    ];
    
    # Open firewall for metrics and dashboard
    openFirewall = true;
  };
  
  # Optional: Configure Prometheus to scrape metrics
  services.prometheus = {
    enable = true;
    
    scrapeConfigs = [
      {
        job_name = "luminous-healing";
        static_configs = [{
          targets = [ "localhost:9090" ];
        }];
      }
    ];
  };
  
  # Optional: Configure Grafana dashboard
  services.grafana = {
    enable = true;
    
    provision = {
      datasources = [
        {
          name = "Prometheus";
          type = "prometheus";
          url = "http://localhost:9001";
        }
      ];
      
      dashboards = [
        {
          name = "Luminous Healing";
          folder = "System";
          options.path = ./dashboards/luminous-healing.json;
        }
      ];
    };
  };
}