import { ImageResponse } from "next/og";

export const size = { width: 1200, height: 630 };
export const contentType = "image/png";
export const alt = "MentorMesh AI — Mentorship grounded in what you actually built";

export default function OpengraphImage() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          background: "#FBFAF8",
          padding: 80,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          <div
            style={{
              width: 48,
              height: 48,
              borderRadius: 12,
              background: "#4338CA",
              display: "flex",
            }}
          />
          <div style={{ fontSize: 32, fontWeight: 600, color: "#1A1B2E" }}>MentorMesh</div>
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
          <div
            style={{
              fontSize: 68,
              fontWeight: 600,
              color: "#1A1B2E",
              lineHeight: 1.1,
              letterSpacing: "-0.03em",
              maxWidth: 900,
            }}
          >
            Mentorship grounded in what you actually built
          </div>
          <div style={{ fontSize: 30, color: "#5A5C72", maxWidth: 820, lineHeight: 1.4 }}>
            Four links in. Specialist mentors who cite their sources, out.
          </div>
        </div>

        <div style={{ display: "flex", gap: 12 }}>
          {["GitHub", "Website", "Pitch deck", "Social"].map((label) => (
            <div
              key={label}
              style={{
                fontSize: 22,
                color: "#5A5C72",
                border: "1px solid #E3E1DC",
                borderRadius: 999,
                padding: "8px 20px",
                display: "flex",
              }}
            >
              {label}
            </div>
          ))}
        </div>
      </div>
    ),
    size
  );
}
