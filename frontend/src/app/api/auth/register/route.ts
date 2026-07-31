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

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const response = await axios.post(`${BACKEND_URL}/auth/register`, body);
    const { access_token, refresh_token, user } = response.data;

    const cookieStore = await cookies();
    cookieStore.set("refresh_token", refresh_token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "lax",
      path: "/",
    });

    return NextResponse.json({ access_token, user });
  } catch (error: unknown) {
    const axiosErr = error as AxiosError<{ detail?: string }>;
    const status = axiosErr.response?.status || 500;
    const detail = axiosErr.response?.data?.detail || axiosErr.message || "Registration failed";
    return NextResponse.json({ detail }, { status });
  }
}
