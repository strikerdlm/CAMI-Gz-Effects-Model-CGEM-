import { expect, test, type Page } from "@playwright/test";
import turn from "./fixtures/turn.json" with { type: "json" };
import loop from "./fixtures/loop.json" with { type: "json" };

async function mockFlight(page: Page) {
  await page.route("**/simulate-flight", async (route) => {
    const request = route.request().postDataJSON() as { scenario: string };
    await route.fulfill({ json: request.scenario === "loop" ? loop : turn });
  });
}
test("play, seek, cameras and setup use one lesson state", async ({ page }) => {
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  await mockFlight(page);
  await page.goto("/simulator");
  await expect(
    page.getByRole("heading", {
      name: "The aircraft. The load. The response.",
    }),
  ).toBeVisible();
  await expect(page.locator(".flight-scene")).toBeVisible();
  await expect(page.locator(".flight-scene-error")).toHaveCount(0);
  await page.getByRole("button", { name: "Play lesson", exact: true }).click();
  await expect
    .poll(async () =>
      Number(await page.locator(".flight-time strong").textContent()),
    )
    .toBeGreaterThan(0.2);
  await page.getByRole("button", { name: "Pause lesson", exact: true }).click();
  const t = await page.locator(".flight-time strong").textContent();
  await page.getByRole("button", { name: "Cockpit", exact: true }).click();
  await expect(
    page.getByRole("button", { name: "Cockpit", exact: true }),
  ).toHaveAttribute("aria-pressed", "true");
  await expect(page.locator(".flight-time strong")).toHaveText(t!);
  await page
    .getByRole("slider", { name: "Lesson time", exact: true })
    .press("End");
  await expect(page.locator(".flight-time strong")).toHaveText(
    turn.duration_s.toFixed(2),
  );
  await page.getByRole("button", { name: "Restart lesson" }).click();
  await expect(page.locator(".flight-time strong")).toHaveText("0.00");
  await expect(page.locator(".flight-physiology-values")).toContainText("—");
  for (const name of ["Orbit", "Split", "Chase"])
    await page.getByRole("button", { name, exact: true }).click();
  await page.getByRole("button", { name: "Forces", exact: true }).click();
  await page.getByRole("button", { name: "Setup", exact: true }).click();
  await page.getByLabel("Entry IAS · kt", { exact: true }).fill("135");
  await expect(page.locator(".flight-scene")).toHaveCount(0);
  await expect(
    page.getByRole("button", { name: "Export video" }),
  ).toBeDisabled();
  const request = page.waitForRequest("**/simulate-flight");
  await page
    .getByRole("button", { name: "Generate lesson", exact: true })
    .first()
    .click();
  expect((await request).postDataJSON().entry_ias_kts).toBe(135);
  await expect(page.locator(".flight-scene")).toBeVisible();
  expect(errors).toEqual([]);
});

test("a slow superseded request cannot replace the latest lesson", async ({
  page,
}) => {
  let requests = 0;
  await page.route("**/simulate-flight", async (route) => {
    const body = route.request().postDataJSON() as { scenario: string };
    requests++;
    if (body.scenario === "coordinated_turn")
      await new Promise((resolve) => setTimeout(resolve, 500));
    await route
      .fulfill({ json: body.scenario === "loop" ? loop : turn })
      .catch(() => undefined);
  });
  await page.goto("/simulator");
  await expect.poll(() => requests).toBeGreaterThan(0);
  await page.getByRole("button", { name: /Inside loop/ }).click();
  await expect(page.locator(".flight-time")).toContainText(
    loop.duration_s.toFixed(2),
  );
  await page.getByRole("button", { name: "Setup", exact: true }).click();
  await expect(page.getByLabel("Entry IAS · kt", { exact: true })).toHaveValue(
    "180",
  );
});

test("errors and unavailable physiology have explicit states", async ({
  page,
}) => {
  await page.route("**/simulate-flight", (route) =>
    route.fulfill({
      status: 422,
      json: { detail: "Entry speed is outside the maneuver envelope." },
    }),
  );
  await page.goto("/simulator");
  await expect(
    page.getByText("Entry speed is outside the maneuver envelope."),
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Export video" }),
  ).toBeDisabled();
  await page.unroute("**/simulate-flight");
  await page.route("**/simulate-flight", (route) =>
    route.fulfill({
      json: {
        ...turn,
        physiology: {
          status: "unavailable",
          result: null,
          reason: "CGEM binary unavailable.",
          binary_sha256: null,
        },
      },
    }),
  );
  await page
    .getByRole("button", { name: "Generate lesson", exact: true })
    .click();
  await expect(page.locator(".flight-scene")).toBeVisible();
  await expect(
    page.getByText("CGEM binary unavailable.", { exact: true }),
  ).toBeVisible();
  await expect(page.locator(".flight-physiology-values")).toHaveCount(0);
});

test("mobile is usable and legacy traces never invent aircraft attitude", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await mockFlight(page);
  await page.goto("/simulator");
  await expect(page.locator(".flight-scene")).toBeVisible();
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBe(true);
  await page.getByRole("button", { name: "Setup", exact: true }).click();
  await expect(page.getByLabel("Aircraft loading")).toBeVisible();
  await page.getByRole("button", { name: "Close setup" }).click();
  await page
    .getByRole("link", { name: "Open the full G-trace lesson library" })
    .click();
  await expect(
    page.getByRole("heading", { name: "Maneuver exposure lessons" }),
  ).toBeVisible();
  await expect(page.locator(".flight-scene")).toHaveCount(0);
  await expect(
    page.getByText(/This catalog trace does not define aircraft attitude/),
  ).toBeVisible();
  await expect(page.getByText("ATTITUDE · VISUAL PROXY")).toHaveCount(0);
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBe(true);
});

test("video interval validation and cancellation preserve the viewer", async ({
  page,
}) => {
  await mockFlight(page);
  await page.goto("/simulator");
  await page.getByRole("button", { name: "Export video" }).click();
  const dialog = page.getByRole("dialog");
  await expect(dialog).toBeVisible();
  await dialog.getByLabel("Start · simulation seconds").fill("8");
  await dialog.getByLabel("End · simulation seconds").fill("2");
  await expect(
    dialog.getByRole("button", { name: "Render MP4" }),
  ).toBeDisabled();
  await dialog.getByLabel("Start · simulation seconds").fill("0");
  await dialog
    .getByLabel("End · simulation seconds")
    .fill(String(turn.duration_s));
  // CI Chromium may lack a licensed H.264 encoder; unsupported capability is a tested UI state.
  await expect
    .poll(
      async () =>
        await dialog.getByText("Checking H.264 encoding support…").count(),
      { timeout: 20_000 },
    )
    .toBe(0);
  if (await dialog.getByRole("button", { name: "Render MP4" }).isEnabled()) {
    await dialog.getByRole("button", { name: "Render MP4" }).click();
    await expect
      .poll(
        async () =>
          Number(await dialog.getByRole("progressbar").getAttribute("value")),
        { timeout: 30_000 },
      )
      .toBeGreaterThan(0);
    await dialog.getByRole("button", { name: "Cancel export" }).click();
    await expect(
      dialog.getByText("Export cancelled. The lesson is unchanged."),
    ).toBeVisible();
  } else
    await expect(
      dialog.getByText(/H.264 encoding at 1080p is unavailable/),
    ).toBeVisible();
  await dialog.getByRole("button", { name: "Close", exact: true }).click();
  await expect(page.locator(".flight-time strong")).toHaveText("0.00");
  await expect(page.locator(".flight-scene-error")).toHaveCount(0);
});

test("aircraft loading preserves a seek and recovers after an asset failure", async ({
  page,
}) => {
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  await mockFlight(page);
  let release!: () => void;
  const gate = new Promise<void>((resolve) => {
    release = resolve;
  });
  await page.route("**/models/Extra-300-r03.glb", async (route) => {
    await gate;
    await route.continue();
  });
  await page.goto("/simulator");
  await expect(page.locator(".flight-scene-status")).toBeVisible();
  await page
    .getByRole("slider", { name: "Lesson time", exact: true })
    .press("End");
  release();
  await expect(page.locator("canvas.flight-scene")).toHaveAttribute(
    "aria-busy",
    "false",
  );
  await expect(page.locator(".flight-time strong")).toHaveText(
    turn.duration_s.toFixed(2),
  );
  for (const name of ["Chase", "Cockpit", "Split", "Orbit"]) {
    await page.getByRole("button", { name, exact: true }).click();
    await expect(page.locator(".flight-scene-error")).toHaveCount(0);
  }
  await page.unroute("**/models/Extra-300-r03.glb");
  await page.route("**/models/Extra-300-r03.glb", (route) =>
    route.fulfill({ status: 503, body: "Unavailable" }),
  );
  await page.reload();
  await expect(page.getByRole("alert")).toContainText(
    "Extra 300 model could not load",
  );
  await page.unroute("**/models/Extra-300-r03.glb");
  await page.reload();
  await expect(page.locator("canvas.flight-scene")).toHaveAttribute(
    "aria-busy",
    "false",
  );
  await expect(page.locator(".flight-scene-error")).toHaveCount(0);
  expect(errors).toEqual([]);
});

test("navigation during aircraft loading releases the retired view", async ({
  page,
}) => {
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  await mockFlight(page);
  let release!: () => void;
  const gate = new Promise<void>((resolve) => {
    release = resolve;
  });
  let completed!: () => void;
  const responseSent = new Promise<void>((resolve) => {
    completed = resolve;
  });
  await page.route("**/models/Extra-300-r03.glb", async (route) => {
    const response = await route.fetch();
    await gate;
    await route.fulfill({ response });
    completed();
  });
  await page.goto("/simulator");
  await expect(page.locator(".flight-scene-status")).toBeVisible();
  await page
    .getByRole("link", { name: "Open the full G-trace lesson library" })
    .click();
  await expect(page.locator("canvas.flight-scene")).toHaveCount(0);
  release();
  await responseSent;
  await page.unroute("**/models/Extra-300-r03.glb");
  await page.getByRole("link", { name: /Open Extra 300L simulation/ }).click();
  await expect(page.locator("canvas.flight-scene")).toHaveAttribute(
    "aria-busy",
    "false",
  );
  await expect(page.locator(".flight-scene-error")).toHaveCount(0);
  expect(errors).toEqual([]);
});

test("MP4 export waits for its aircraft and supports cancellation while loading", async ({
  page,
}) => {
  await mockFlight(page);
  await page.goto("/simulator");
  await expect(page.locator("canvas.flight-scene")).toHaveAttribute(
    "aria-busy",
    "false",
  );
  await page.getByRole("button", { name: "Export video" }).click();
  const dialog = page.getByRole("dialog");
  await expect(
    dialog.getByText("Checking H.264 encoding support…"),
  ).toHaveCount(0, { timeout: 20_000 });
  const render = dialog.getByRole("button", { name: "Render MP4" });
  if (!(await render.isEnabled())) {
    await expect(
      dialog.getByText(/H.264 encoding at 1080p is unavailable/),
    ).toBeVisible();
    return;
  }
  await dialog.getByLabel("End · simulation seconds").fill("0.1");
  let release!: () => void;
  const gate = new Promise<void>((resolve) => {
    release = resolve;
  });
  let completed!: () => void;
  const responseSent = new Promise<void>((resolve) => {
    completed = resolve;
  });
  await page.route("**/models/Extra-300-r03.glb", async (route) => {
    await gate;
    await route.continue();
    completed();
  });
  const requested = page.waitForRequest("**/models/Extra-300-r03.glb");
  await render.click();
  await requested;
  await expect(dialog.getByRole("progressbar")).toHaveAttribute("value", "0");
  await dialog.getByRole("button", { name: "Cancel export" }).click();
  await expect(
    dialog.getByText("Export cancelled. The lesson is unchanged."),
  ).toBeVisible();
  release();
  await responseSent;
  await page.unroute("**/models/Extra-300-r03.glb");
  const download = page.waitForEvent("download");
  await render.click();
  const video = await download;
  expect(await video.failure()).toBeNull();
  await expect(dialog.getByText(/Video ready/)).toBeVisible();
  await dialog.getByRole("button", { name: "Close", exact: true }).click();
  await expect(page.locator(".flight-time strong")).toHaveText("0.00");
  await expect(page.locator(".flight-scene-error")).toHaveCount(0);
});
