import { NextRequest, NextResponse } from "next/server";
import { watchProviders } from "@/data/watch-providers";
import watchLinksJson from "@/data/watch-links.json";

const watchLinksData = watchLinksJson as Record<
  string,
  Array<{ providerId: string; externalId: string; accessType: string }>
>;

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ providerId: string; movieId: string }> }
) {
  const { providerId, movieId } = await params;

  const linksForMovie = watchLinksData[movieId] || [];
  const link = linksForMovie.find((l) => l.providerId === providerId);

  if (!link) {
    return new NextResponse("Not Found", { status: 404 });
  }

  const provider = watchProviders.find((p) => p.id === providerId);
  if (!provider) {
    return new NextResponse("Provider Not Found", { status: 404 });
  }

  const finalUrl = provider.template.replace("{externalId}", link.externalId);

  // Log click analytics
  console.log(`[Affiliate Click] Movie: ${movieId}, Provider: ${providerId}, Time: ${new Date().toISOString()}, Redirect URL: ${finalUrl}`);

  return NextResponse.redirect(finalUrl, 302);
}
