import { Router } from "express";

const router = Router();

router.post("/event", (req, res) => {
  res.status(202).json({
    accepted: true,
  });
});

export default router;
