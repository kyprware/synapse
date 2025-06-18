import { defineConfig } from "vitepress";

export default defineConfig({
  lang: "en-US",
  base: "/synapse/",
  title: "SYNAPSE",
  titleTemplate: "SYNAPSE",
  description:
    "Structured Yielding Network Anchor for Propagation and Spoke Execution",
  cleanUrls: true,
  metaChunk: true,
  lastUpdated: true,
  locales: {
    root: {
      lang: "en",
      label: "English",
      link: "/v1/en/",
    },
  },
  themeConfig: {
    nav: [],

    sidebar: [],

    socialLinks: [
      { icon: "github", link: "https://github.com/kyprware/synapse/" },
    ],

    footer: {
      message: "Released under the Apache v2.0 License.",
      copyright: "Copyright © 2025-present Kyprware",
    },
  },
});
