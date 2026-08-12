{ config, pkgs, ... }:

{
  services.agentic-browser = {
    enable = true;
    controlPort = 8766;
    backendUrl = "http://localhost:8123";
    envFile = "/etc/agentic-browser/agentic.env";
  };

  systemd.services.agentic-browser-control = {
    description = "AgenticBrowser control plane";
    wantedBy = [ "multi-user.target" ];
    serviceConfig = {
      User = "agenticbrowser";
      Group = "agenticbrowser";
      WorkingDirectory = "/opt/agentic-browser/control";
      ExecStart = "${pkgs.nodejs}/bin/node dist/server.js";
      Restart = "on-failure";
      EnvironmentFile = config.services.agentic-browser.envFile;
    };
  };

  systemd.services.agentic-browser-backend = {
    description = "AgenticBrowser backend";
    wantedBy = [ "multi-user.target" ];
    serviceConfig = {
      User = "agenticbrowser";
      Group = "agenticbrowser";
      WorkingDirectory = "/opt/agentic-browser/backend";
      ExecStart = "${pkgs.python311}/bin/uvicorn main:app --host 127.0.0.1 --port 8123";
      Restart = "on-failure";
      EnvironmentFile = config.services.agentic-browser.envFile;
    };
  };
}
