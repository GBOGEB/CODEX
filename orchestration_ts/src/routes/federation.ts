import { Router } from "express";

const router = Router();

const MAX_FIELD_LENGTH = 128;

export interface FederationEvent {
  source: string;
  type: string;
}

function isBoundedString(value: unknown): value is string {
  return typeof value === "string" && value.length > 0 && value.length <= MAX_FIELD_LENGTH;
}

// Project the request body onto the known event fields. Only these validated
// fields are echoed back, so arbitrary or sensitive extra fields in the request
// are never reflected and the response size stays bounded.
export function parseFederationEvent(body: unknown): FederationEvent | null {
  if (typeof body !== "object" || body === null || Array.isArray(body)) {
    return null;
  }

  const { source, type } = body as Record<string, unknown>;

  if (!isBoundedString(source) || !isBoundedString(type)) {
    return null;
  }

  return { source, type };
}

router.post("/event", (req, res) => {
  const event = parseFederationEvent(req.body);

  if (event === null) {
    res.status(400).json({
      accepted: false,
      error: `event requires non-empty string fields 'source' and 'type' (max ${MAX_FIELD_LENGTH} chars)`,
    });
    return;
  }

  res.status(202).json({
    accepted: true,
    event,
  });
});

export default router;
