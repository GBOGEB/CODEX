import { Router } from "express";

const router = Router();

router.post("/event", (req, res) => {
  res.status(202).json({
    accepted: true,
    event: req.body ?? null,
  });
});

export default router;
