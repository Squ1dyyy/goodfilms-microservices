import { test, expect } from "@playwright/test";

test.describe("GoodFilms E2E Flow", () => {
  let bookmarks: number[] = [];

  test.beforeEach(async ({ page }) => {
    bookmarks = [];

    // Mock Reference APIs
    await page.route("**/api/v1/genres", async (route) => {
      await route.fulfill({ json: [{ id: 1, name: "Боевик" }] });
    });
    await page.route("**/api/v1/countries", async (route) => {
      await route.fulfill({ json: [{ id: 1, name: "США" }] });
    });
    await page.route("**/api/v1/studios", async (route) => {
      await route.fulfill({ json: [{ id: 1, name: "Warner Bros." }] });
    });

    // Mock Movies List Catalog (Home and Search)
    await page.route("**/api/v1/movies?**", async (route) => {
      await route.fulfill({
        json: {
          items: [
            {
              id: 1,
              title: "Тестовый Фильм",
              release_year: 2024,
              poster_url: "https://example.com/poster.jpg",
              genres: ["Боевик"],
            },
          ],
          total: 1,
          page: 1,
          limit: 12,
        },
      });
    });

    // Mock Movie Detail Endpoint
    await page.route("**/api/v1/movies/1", async (route) => {
      await route.fulfill({
        json: {
          id: 1,
          title: "Тестовый Фильм",
          release_year: 2024,
          poster_url: "https://example.com/poster.jpg",
          genres: ["Боевик"],
          description: "Это тестовое описание фильма.",
          studios: ["Warner Bros."],
          cast: [],
          directors: [],
          writers: [],
          producers: [],
        },
      });
    });

    // Mock Bookmarks endpoints (stateful mockup)
    await page.route("**/api/v1/users/me/bookmarks", async (route) => {
      if (route.request().method() === "GET") {
        await route.fulfill({ json: bookmarks });
      }
    });

    await page.route("**/api/v1/users/me/bookmarks/1", async (route) => {
      if (route.request().method() === "POST") {
        bookmarks.push(1);
        await route.fulfill({ json: { success: true } });
      } else if (route.request().method() === "DELETE") {
        bookmarks = bookmarks.filter((id) => id !== 1);
        await route.fulfill({ json: { success: true } });
      }
    });

    // Mock Notifications endpoints
    await page.route("**/api/v1/notification?**", async (route) => {
      await route.fulfill({ json: [] });
    });
  });

  test("should register, login, add movie to bookmarks, check favorites page and watch providers", async ({
    page,
  }) => {
    // 1. Mock registration
    await page.route("/api/auth/register", async (route) => {
      await route.fulfill({
        json: {
          access_token: "mock-register-token",
          user: { id: 1, username: "testuser" },
        },
      });
    });

    await page.route("/api/auth/refresh", async (route) => {
      await route.fulfill({
        json: {
          access_token: "mock-register-token",
          user: { id: 1, username: "testuser" },
        },
      });
    });

    await page.route("**/api/v1/auth/me", async (route) => {
      await route.fulfill({
        json: {
          id: 1,
          username: "testuser",
          email: "testuser@example.com",
          is_active: true,
          is_verified: true,
          role: "user",
        },
      });
    });

    // Go to register page
    await page.goto("/register");
    await page.fill('input[placeholder="example@mail.com"]', "testuser@example.com");
    await page.fill('input[placeholder="username"]', "testuser");
    await page.fill('input[name="password"]', "password123");
    await page.fill('input[name="password_confirm"]', "password123");

    // Click register button
    await page.click('button[type="submit"]');

    // After registration, user is redirected and authenticated. Let's verify we are on home or page loads.
    await expect(page).toHaveURL("/");

    // 2. Go to Movie Detail Page
    await page.goto("/movies/1");

    // Wait for description to load
    await expect(page.locator("h3:has-text('Описание')")).toBeVisible();
    await expect(page.locator("text=Тестовый Фильм")).toBeVisible();

    // Verify watch providers row is loaded (since movieId 1 is in static watch-links.json)
    await expect(page.locator("text=Где посмотреть:")).toBeVisible();
    const link = page.locator('a:has-text("Кинопоиск HD")');
    await expect(link).toHaveAttribute("href", "/go/kinopoisk/1");

    // 3. Add to Bookmarks
    await page.click('button:has-text("В закладки")');

    // Verify button text changes to "В закладках" (optimistic update)
    await expect(page.locator('button:has-text("В закладках")')).toBeVisible();

    // 4. Navigate to Favorites page
    await page.goto("/favorites");

    // Verify the bookmarked movie card is visible in favorites list
    await expect(page.locator("text=Мои закладки")).toBeVisible();
    await expect(page.locator("text=Тестовый Фильм")).toBeVisible();
  });
});
