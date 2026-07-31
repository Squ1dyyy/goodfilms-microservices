import { NextResponse } from "next/server";
import { cookies } from "next/headers";
import axios, { AxiosError } from "axios";

// Route handlers run server-side (inside the container), so prefer the
// internal gateway URL. NEXT_PUBLIC_API_BASE_URL points at localhost:8080,
// which from inside the container is the container itself, not the gateway.
const BACKEND_URL =
  process.env.INTERNAL_API_BASE_URL ||
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  "http://localhost:8080/api/v1";

export async function POST() {
  try {
    const cookieStore = await cookies();
    const refreshToken = cookieStore.get("refresh_token")?.value;

    if (!refreshToken) {
      return NextResponse.json({ detail: "No refresh token available" }, { status: 401 });
    }

    const response = await axios.post(`${BACKEND_URL}/auth/refresh`, {
      refresh_token: refreshToken,
    });

    const { access_token, refresh_token: new_refresh_token, user } = response.data;

    // Update the cookie with the new refresh token (if returned, or keep the old one)
    const tokenToStore = new_refresh_token || refreshToken;
    cookieStore.set("refresh_token", tokenToStore, {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "lax",
      path: "/",
    });

    return NextResponse.json({ access_token, user });
  } catch (error: unknown) {
    const axiosErr = error as AxiosError<{ detail?: string }>;
    const status = axiosErr.response?.status || 500;
    const detail = axiosErr.response?.data?.detail || axiosErr.message || "Failed to refresh token";
    return NextResponse.json({ detail }, { status });
  }
}
