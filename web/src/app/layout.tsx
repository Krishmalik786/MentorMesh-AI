import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import { ThemeProvider } from "@/components/theme-provider";
import { TooltipProvider } from "@/components/ui/tooltip";
import { Toaster } from "@/components/ui/sonner";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  display: "swap",
});

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-jetbrains-mono",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  metadataBase: new URL("https://mentormesh.ai"),
  title: {
    default: "MentorMesh AI — Mentorship grounded in what you actually built",
    template: "%s · MentorMesh AI",
  },
  description:
    "Drop in four links. Get a startup profile built from real evidence, then chat with specialist mentors who cite their sources instead of guessing.",
  openGraph: {
    title: "MentorMesh AI — Mentorship grounded in what you actually built",
    description:
      "Drop in four links. Get a startup profile built from real evidence, then chat with specialist mentors who cite their sources instead of guessing.",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "MentorMesh AI",
    description: "Mentorship grounded in what you actually built.",
  },
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="en"
      suppressHydrationWarning
      className={`${inter.variable} ${jetbrainsMono.variable} h-full antialiased`}
    >
      <body className="flex min-h-full flex-col">
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
          <TooltipProvider>
            {children}
            <Toaster />
          </TooltipProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
