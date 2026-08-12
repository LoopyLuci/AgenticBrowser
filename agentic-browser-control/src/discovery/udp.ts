import dgram from "node:dgram";

const CONTROL_PORT = Number(process.env.PORT || 8766);
const DISCOVERY_PORT = 43789;
const SERVICE_NAME = "agenticbrowser-control";

type BeaconOpts = {
  port?: number;
  controlPort?: number;
  host?: string;
  name?: string;
};

export function startDiscoveryBeacon(opts: BeaconOpts = {}) {
  const port = opts.port ?? DISCOVERY_PORT;
  const controlPort = opts.controlPort ?? CONTROL_PORT;
  const host = opts.host ?? "0.0.0.0";
  const name = opts.name ?? SERVICE_NAME;

  const socket = dgram.createSocket("udp4");
  socket.bind(port, host, () => {
    console.log(`Discovery beacon listening on ${host}:${port}`);
    socket.setBroadcast(true);
    socket.addMembership("239.255.255.250");
    socket.on("message", (msg, rinfo) => {
      const text = msg.toString("utf8").trim();
      if (text === "DISCOVER") {
        const response = Buffer.from(
          JSON.stringify({
            service: name,
            controlPort,
            host: "127.0.0.1",
            timestamp: Date.now(),
          })
        );
        socket.send(response, 0, response.length, rinfo.port, rinfo.address);
      }
    });
  });

  socket.on("error", (err) => {
    console.error("Discovery beacon error:", err);
  });

  return {
    close: () => socket.close(),
  };
}
