import assert from "node:assert/strict";
import test from "node:test";
import { AddressInfo } from "node:net";
import { app } from "../src/server";

async function withServer<T>(callback: (baseUrl: string) => Promise<T>): Promise<T> {
  const server = app.listen(0);

  try {
    await new Promise<void>((resolve) => server.once("listening", resolve));
    const address = server.address() as AddressInfo;

    return await callback(`http://127.0.0.1:${address.port}`);
  } finally {
    await new Promise<void>((resolve, reject) => {
      server.close((error) => {
        if (error) {
          reject(error);
          return;
        }

        resolve();
      });
    });
  }
}

test("GET /jobs returns an empty ready jobs collection", async () => {
  await withServer(async (baseUrl) => {
    const response = await fetch(`${baseUrl}/jobs`);

    assert.equal(response.status, 200);
    assert.deepEqual(await response.json(), {
      jobs: [],
      status: "ready",
    });
  });
});

test("POST /federation/event accepts and echoes the event payload", async () => {
  await withServer(async (baseUrl) => {
    const event = {
      source: "codex",
      type: "sha_update_verified",
    };

    const response = await fetch(`${baseUrl}/federation/event`, {
      method: "POST",
      headers: {
        "content-type": "application/json",
      },
      body: JSON.stringify(event),
    });

    assert.equal(response.status, 202);
    assert.deepEqual(await response.json(), {
      accepted: true,
      event,
    });
  });
});
