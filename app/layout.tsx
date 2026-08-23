import type { Metadata } from "next";
import { headers } from "next/headers";
import { IBM_Plex_Mono } from "next/font/google";
import { site, totals } from "./catalog.generated";
import "./globals.css";

const ibmPlexMono = IBM_Plex_Mono({
  variable: "--font-ibm-plex-mono",
  subsets: ["latin"],
  weight: ["400", "500", "600"],
});

export async function generateMetadata(): Promise<Metadata> {
  const incoming = await headers();
  const host = incoming.get("x-forwarded-host") ?? incoming.get("host");
  const protocol = incoming.get("x-forwarded-proto") ?? "https";
  const origin = host ? protocol + "://" + host : "http://localhost:3000";
  const title = site.name;
  const description =
    "A public registry with " +
    totals.plugins +
    " plugins and " +
    totals.skills +
    " skills for Codex, Claude Code, and Claude Cowork.";

  return {
    metadataBase: new URL(origin),
    title: {
      default: title,
      template: "%s | " + title,
    },
    description,
    icons: {
      icon: "/favicon.svg",
      shortcut: "/favicon.svg",
    },
    openGraph: {
      title,
      description,
      images: [{ url: origin + "/og.png", width: 1200, height: 630 }],
      type: "website",
    },
    twitter: {
      card: "summary_large_image",
      title,
      description,
      images: [origin + "/og.png"],
    },
  };
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html:
              'try{if(localStorage.getItem("community-agent-plugins-theme")==="sumi")document.documentElement.dataset.theme="sumi"}catch(e){}',
          }}
        />
      </head>
      <body className={ibmPlexMono.variable}>
        {children}
      </body>
    </html>
  );
}
