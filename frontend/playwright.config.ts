import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: false,
  timeout: 90_000,
  // Cold Vite transforms and software WebGL initialization can exceed five seconds.
  expect: { timeout: 15_000 },
  use: {
    baseURL: "http://127.0.0.1:5173",
    viewport: { width: 1440, height: 1100 },
    launchOptions: {
      args: [
        "--use-gl=angle",
        "--use-angle=swiftshader",
        "--enable-unsafe-swiftshader",
      ],
      ...(process.env.CGEM_CHROME_PATH
        ? { executablePath: process.env.CGEM_CHROME_PATH }
        : {}),
    },
    screenshot: "only-on-failure",
    trace: "retain-on-failure",
  },
  outputDir: "/tmp/cgem-playwright-results",
  webServer: {
    command: "npm run dev -- --host 127.0.0.1 --port 5173",
    url: "http://127.0.0.1:5173",
    reuseExistingServer: !process.env.CI,
  },
});
