import { MetadataRoute } from "next";
import { moviesQueries } from "@/features/movies/queries";

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const baseUrl = process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000";

  // Base static routes
  const routes = ["", "/movies", "/favorites", "/notifications", "/search"].map((route) => ({
    url: `${baseUrl}${route}`,
    lastModified: new Date(),
    changeFrequency: "daily" as const,
    priority: route === "" ? 1.0 : 0.8,
  }));

  const movieUrls: MetadataRoute.Sitemap = [];

  try {
    const limit = 50;
    // Load page 1 to find total movies count
    const firstPage = await moviesQueries.getMovies({ page: 1, limit });
    const total = firstPage.total || 0;
    const pages = Math.ceil(total / limit);

    firstPage.items.forEach((m) => {
      movieUrls.push({
        url: `${baseUrl}/movies/${m.id}`,
        lastModified: new Date(),
        changeFrequency: "weekly",
        priority: 0.6,
      });
    });

    // Fetch remainder of movies pages in parallel or series
    for (let p = 2; p <= pages; p++) {
      try {
        const pageData = await moviesQueries.getMovies({ page: p, limit });
        pageData.items.forEach((m) => {
          movieUrls.push({
            url: `${baseUrl}/movies/${m.id}`,
            lastModified: new Date(),
            changeFrequency: "weekly",
            priority: 0.6,
          });
        });
      } catch (pageErr) {
        console.error(`Failed to fetch movies page ${p} for sitemap:`, pageErr);
      }
    }
  } catch (err) {
    console.error("Error generating dynamic sitemap routes:", err);
  }

  return [...routes, ...movieUrls];
}
