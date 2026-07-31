export interface WatchProvider {
  id: string;
  name: string;
  logoUrl: string;
  brandColor: string;
  template: string;
}

export const watchProviders: readonly WatchProvider[] = [
  {
    id: "kinopoisk",
    name: "Кинопоиск HD",
    logoUrl: "/providers/kinopoisk.svg",
    brandColor: "#FF6B00",
    template: "https://hd.kinopoisk.ru/film/{externalId}?utm_source=goodfilms",
  },
  {
    id: "ivi",
    name: "ivi",
    logoUrl: "/providers/ivi.svg",
    brandColor: "#FFD400",
    template: "https://www.ivi.ru/watch/{externalId}?partner=goodfilms",
  },
  {
    id: "okko",
    name: "Okko",
    logoUrl: "/providers/okko.svg",
    brandColor: "#00C2FF",
    template: "https://okko.tv/movie/{externalId}?partner=goodfilms",
  },
] as const;
