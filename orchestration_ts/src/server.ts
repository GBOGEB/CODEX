import express from "express";
import federationRoutes from "./routes/federation";
import jobsRoutes from "./routes/jobs";

export const app = express();

app.use(express.json());

app.get("/health", (_req, res) => {
  res.status(200).json({ status: "ok" });
});

app.use("/jobs", jobsRoutes);
app.use("/federation", federationRoutes);

const parsedPort = Number.parseInt(process.env.PORT ?? "", 10);
const port = Number.isFinite(parsedPort) ? parsedPort : 3000;

if (require.main === module) {
  app.listen(port, () => {
    console.log(`orchestration server listening on ${port}`);
  });
}
