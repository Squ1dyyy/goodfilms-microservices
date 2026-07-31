import { cookies } from "next/headers";
import axios from "axios";

// Route handlers run server-side (inside the container), so prefer the
// internal gateway URL. NEXT_PUBLIC_API_BASE_URL points at localhost:8080,
// which from inside the container is the container itself, not the gateway.
const BACKEND_URL =
  process.env.INTERNAL_API_BASE_URL ||
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  "http://localhost:8080/api/v1";

export async function POST(request: Request) {
  try {
    const authHeader = request.headers.get("Authorization");
    const cookieStore = await cookies();
    const refreshToken = cookieStore.get("refresh_token")?.value;

    // Delete the refresh token cookie locally
    cookieStore.delete("refresh_token");

    if (refreshToken) {
      const headers: Record<string, string> = {};
      if (authHeader) {
        headers["Authorization"] = authHeader;
      }
      
      await axios.post(
        `${BACKEND_URL}/auth/logout`,
        { refresh_token: refreshToken },
        { headers }
      );
    }

    return new Response(null, { status: 204 });
  } catch {
    // Fallback: even if backend call fails, we proceed with logout locally
    return new Response(null, { status: 204 });
  }
}
