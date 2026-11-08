import { createRootRoute, HeadContent, Outlet, Scripts } from "@tanstack/react-router";
import { ThemeBoot } from "@/components/theme-toggle";
import { themeBootScript } from "@/lesson/theme";
import appCss from "../styles.css?url";

const APP_NAME = "Láminas";

export const Route = createRootRoute({
  head: () => ({
    meta: [
      { charSet: "utf-8" },
      { name: "viewport", content: "width=device-width, initial-scale=1" },
      { title: APP_NAME },
      {
        name: "description",
        content:
          "A comprehension course. Pick a level, pick a step, then look and listen.",
      },
      { name: "theme-color", content: "#e8edf2" },
    ],
    links: [
      { rel: "icon", type: "image/svg+xml", href: "/favicon.svg" },
      { rel: "stylesheet", href: appCss },
      { rel: "preconnect", href: "https://fonts.googleapis.com" },
      {
        rel: "preconnect",
        href: "https://fonts.gstatic.com",
        crossOrigin: "anonymous",
      },
      {
        rel: "stylesheet",
        href: "https://fonts.googleapis.com/css2?family=Outfit:wght@500;600&family=Source+Sans+3:wght@400;600&display=swap",
      },
    ],
  }),
  component: () => (
    <html lang="en" suppressHydrationWarning>
      <head>
        <HeadContent />
        <script dangerouslySetInnerHTML={{ __html: themeBootScript }} />
      </head>
      <body>
        <ThemeBoot />
        <Outlet />
        <Scripts />
      </body>
    </html>
  ),
});
