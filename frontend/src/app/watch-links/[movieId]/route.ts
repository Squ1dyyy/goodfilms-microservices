import { NextRequest, NextResponse } from "next/server";
import { watchProviders } from "@/data/watch-providers";
import watchLinksJson from "@/data/watch-links.json";

const watchLinksData = watchLinksJson as Record<
  string,
  Array<{ providerId: string; externalId: string; accessType: string }>
>;

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ movieId: string }> }
) {
  const { movieId } = await params;
  const linksForMovie = watchLinksData[movieId] || [];

  const responseData = linksForMovie
    .map((link) => {
      const provider = watchProviders.find((p) => p.id === link.providerId);
      if (!provider) return null;

      const finalUrl = provider.template.replace("{externalId}", link.externalId);

      return {
        providerId: provider.id,
        name: provider.name,
        logoUrl: provider.logoUrl,
        brandColor: provider.brandColor,
        url: finalUrl,
        accessType: link.accessType,
      };
    })
    .filter(Boolean);

  return NextResponse.json(responseData);
}
