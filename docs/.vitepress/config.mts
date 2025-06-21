import { defineConfig } from "vitepress";
import { withMermaid } from "vitepress-plugin-mermaid"

export default withMermaid(
    defineConfig({
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
            nav: [
                { text: "Home", link: "/" },
                { text: "Guide", link: "/guide/introduction" },
                {
                    text: "Development",
                    items: [
                        { text: "Contributing", link: "/development/contributing" },
                        { text: "Contributors", link: "/development/contributors" }
                    ]
                }
            ],
            sidebar: {
                "/guide/": [
                    {
                        text: "Getting Started",
                        collapsed: false,
                        items: [
                            { text: "Introduction", link: "/guide/introduction" },
                            { text: "Quick Start", link: "/guide/quickstart" }
                        ]
                    },
                    {
                        text: "Core Concepts",
                        collapsed: false,
                        items: [
                            { text: "Architecture", link: "/guide/architecture" },
                            { text: "Transport", link: "/guide/transport" },
                            { text: "Permissions", link: "/guide/permissions" }
                        ]
                    },
                    {
                        text: "Reference",
                        collapsed: false,
                        items: [
                            { text: "Resources", link: "/guide/resources" },
                            { text: "Examples", link: "/guide/examples" }
                        ]
                    }
                ],
                "/development/": [
                    {
                        text: "Development",
                        collapsed: false,
                        items: [
                            { text: "Contributing", link: "/development/contributing" },
                            { text: "Contributors", link: "/development/contributors" }
                        ]
                    }
                ]
            },
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
    })
);
