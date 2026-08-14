import { NextResponse } from "next/server";
import { apiBaseUrl } from "@/lib/api";

export async function GET(_request: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;

  const res = await fetch(`${apiBaseUrl()}/profile/${encodeURIComponent(id)}`, {
    cache: "no-store",
  });

  const data = await res.json().catch(() => ({}));
  return NextResponse.json(data, { status: res.status });
}
