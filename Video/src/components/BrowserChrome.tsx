import React from "react";
import { colors } from "../tokens";

export type BrowserContent = "empty" | "website" | "selected";

export const BrowserChrome: React.FC<{
  content?: BrowserContent;
  scrollProgress?: number;
  highlightCard?: boolean;
  showReadLines?: number;
  bookmarkFilled?: boolean;
  backgroundColorHex?: string;
  style?: React.CSSProperties;
}> = ({
  content = "empty",
  scrollProgress = 0,
  highlightCard = false,
  showReadLines = 0,
  bookmarkFilled = false,
  backgroundColorHex = colors.paper,
  style,
}) => {
  return (
    <div
      style={{
        width: 900,
        height: 520,
        borderRadius: 12,
        overflow: "hidden",
        boxShadow: "0 8px 40px rgba(26,18,18,0.15)",
        border: `1px solid ${colors.borderColor}`,
        backgroundColor: backgroundColorHex,
        display: "flex",
        flexDirection: "column",
        ...style,
      }}
    >
      {/* Title bar */}
      <div
        style={{
          height: 44,
          backgroundColor: "#f0ece5",
          display: "flex",
          alignItems: "center",
          padding: "0 16px",
          gap: 8,
          flexShrink: 0,
          borderBottom: `1px solid ${colors.borderColor}`,
        }}
      >
        {["#ff5f56", "#ffbd2e", "#27c93f"].map((c) => (
          <div key={c} style={{ width: 12, height: 12, borderRadius: "50%", backgroundColor: c }} />
        ))}
        <div
          style={{
            marginLeft: 16,
            flex: 1,
            height: 26,
            backgroundColor: "rgba(26,22,20,0.06)",
            borderRadius: 6,
            display: "flex",
            alignItems: "center",
            paddingLeft: 12,
            fontSize: 13,
            color: colors.imprintMuted,
            fontFamily: "SF Mono, monospace",
          }}
        >
          https://example.com/article
        </div>
        <div
          style={{
            width: 20,
            height: 20,
            marginLeft: 8,
            color: bookmarkFilled ? colors.accentPrimary : colors.imprintMuted,
            fontSize: 18,
            lineHeight: "20px",
          }}
        >
          {bookmarkFilled ? "★" : "☆"}
        </div>
      </div>

      {/* Page content area */}
      <div style={{ flex: 1, overflow: "hidden", position: "relative" }}>
        {(content === "website" || content === "selected") && (
          <div
            style={{
              transform: `translateY(${-scrollProgress * 80}px)`,
              padding: 16,
              display: "flex",
              flexDirection: "column",
              gap: 12,
            }}
          >
            <div style={{ height: 32, backgroundColor: colors.accentPrimary, borderRadius: 4, opacity: 0.8 }} />
            <div style={{ height: 80, backgroundColor: colors.accentLighter, borderRadius: 6 }} />
            {[0, 1, 2].map((i) => (
              <div
                key={i}
                style={{
                  height: 72,
                  backgroundColor: i === 1 && highlightCard ? "transparent" : colors.cardBg,
                  borderRadius: 8,
                  border: i === 1 && highlightCard
                    ? `2px solid ${colors.accentPrimary}`
                    : `1px solid ${colors.borderColor}`,
                  padding: 12,
                  overflow: "hidden",
                }}
              >
                {i === 1 && showReadLines > 0 && (
                  <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                    {Array.from({ length: Math.min(showReadLines, 8) }).map((_, li) => (
                      <div
                        key={li}
                        style={{
                          height: 6,
                          backgroundColor: colors.imprintMuted,
                          borderRadius: 3,
                          width: "100%",
                        }}
                      />
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
