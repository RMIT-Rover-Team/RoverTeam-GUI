import { Html, Head, Main, NextScript } from "next/document";

export default function Document() {
  return (
    <Html lang="en">
      <Head>
        {/* google font used for GUI */}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          rel="preconnect"
          href="https://fonts.gstatic.com"
          crossOrigin=""
        />
        <link
          href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;700&display=swap"
          rel="stylesheet"
        />
      </Head>

      <body className="antialiased">
        <Main />
        <NextScript />
      </body>
    </Html>
  );
}
