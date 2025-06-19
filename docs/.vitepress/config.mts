import { defineConfig } from "vitepress";

export default defineConfig({
  lang: "en-US",
  base: "/synapse/",
  title: "SYNAPSE",
  titleTemplate: "SYNAPSE",
  description:
    "Structured Yielding Network Anchor for Propagation and Spoke Execution",

  srcDir: "./content",
  cleanUrls: true,
  metaChunk: true,
  lastUpdated: true,

  rewrites: {
    "v0/en/:slug*": ":slug*",
  },

  ignoreDeadLinks: "localhostLinks",

  locales: {
    root: {
      lang: "en",
      label: "English",
    },
  },

  themeConfig: {
    logo: "/logo.svg",
    outline: "deep",

    lastUpdated: {
      text: "Updated at",
      formatOptions: {
        dateStyle: "full",
        timeStyle: "medium",
      },
    },

    search: {
      provider: "local",
    },

    nav: [],

    sidebar: [],

    socialLinks: [
      { icon: "github", link: "https://github.com/kyprware/synapse/" },
    ],

    footer: {
      message: "Released under the Apache v2.0 License.",
      copyright: "Copyright © 2025-present Kyprware",
    },

    editLink: {
      pattern:
        "https://github.com/kyprware/synapse/edit/main/docs/content/:path",
      text: "Edit this page on GitHub",
    },
  },

  sitemap: {
    hostname: "https://kyprware.github.io/synapse/",
  },
});
