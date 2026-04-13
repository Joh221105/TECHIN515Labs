import fs from "fs";
import path from "path";
import { NextResponse } from "next/server";
import { getDb } from "@/lib/db";
import { petitionUploadDir } from "@/lib/paths";

export const runtime = "nodejs";

export async function GET(
  _request: Request,
  context: { params: Promise<{ id: string }> },
) {
  const { id } = await context.params;
  const db = getDb();
  const row = db.prepare("SELECT id FROM petitions WHERE id = ?").get(id) as
    | { id: string }
    | undefined;
  if (!row) {
    return NextResponse.json({ error: "Not found" }, { status: 404 });
  }
  const filePath = path.join(petitionUploadDir(id), "combined.pdf");
  if (!fs.existsSync(filePath)) {
    return NextResponse.json({ error: "Combined PDF not available" }, { status: 404 });
  }
  const buf = fs.readFileSync(filePath);
  return new NextResponse(buf, {
    headers: {
      "Content-Type": "application/pdf",
      "Content-Disposition": `attachment; filename="combined-${id}.pdf"`,
    },
  });
}
