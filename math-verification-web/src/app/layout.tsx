import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Mathematical Verification Suite | Yang-Mills, Collatz, Goldbach",
  description: "Rigorous verification of Yang-Mills Mass Gap (Phase 1), Collatz Conjecture, and Goldbach Conjecture. Interactive computational tools and mathematical proofs.",
  keywords: ["Yang-Mills", "Mass Gap", "Collatz Conjecture", "Goldbach Conjecture", "Mathematical Proof", "Verification"],
  authors: [{ name: "David Redavid" }],
  openGraph: {
    title: "Mathematical Verification Suite",
    description: "Rigorous verification of Yang-Mills Mass Gap, Collatz Conjecture, and Goldbach Conjecture",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-gray-950 text-gray-100 font-mono antialiased">
        {children}
      </body>
    </html>
  );
}