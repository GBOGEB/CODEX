declare module "express" {
  export interface Request {
    body?: unknown;
  }

  export interface Response {
    status(code: number): Response;
    json(body: unknown): Response;
  }

  export interface Router {
    get(path: string, handler: (req: Request, res: Response) => void): Router;
    post(path: string, handler: (req: Request, res: Response) => void): Router;
  }

  export interface Application extends Router {
    use(pathOrMiddleware: string | unknown, router?: unknown): Application;
    listen(port: number, callback?: () => void): unknown;
  }

  interface ExpressFactory {
    (): Application;
    json(): unknown;
  }

  export function Router(): Router;

  const express: ExpressFactory;
  export default express;
}

declare const process: {
  env: Record<string, string | undefined>;
};

declare const require: {
  main?: unknown;
};

declare const module: unknown;
