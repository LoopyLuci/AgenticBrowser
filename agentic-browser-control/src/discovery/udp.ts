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
    socket.setBroadcast(true);
    socket.addMembership("239.255.255.250");
    const payload = Buffer.from(
      JSON.stringify({
        service: name,
        controlPort,
        host: "127.0.0.1",
        timestamp: Date.now(),
      })
    );
    socket.send(payload, 0, payload.length, port, "239.255.255.250", () => {});
    const timer = setInterval(() => {
      const current = Buffer.from(
        JSON.stringify({
          service: name,
          controlPort,
          host: "127.0.0.1",
          timestamp: Date.now(),
        })
      );
      socket.send(current, 0, current.length, port, "239.255.255.250", () => {});
    }, 5000);

    return {
      close: () => {
        clearInterval(timer);
        socket.close();
      },
    };
  });

  socket.on("error", (err) => {
    console.error("Discovery beacon error:", err);
  });

  return {
    close: () => socket.close(),
  };
}
