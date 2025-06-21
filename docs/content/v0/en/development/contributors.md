# Contributors

<script setup>
import { VPTeamMembers } from "vitepress/theme"

const contributors = [
    {
        avatar: "https://github.com/0x15ba88ff.png",
        name: "Pascal Nkornyui",
        title: "Lead Developer",
        links: [
            { icon: "github", link: "https://github.com/0x15ba88ff" },
            { icon: "x", link: "https://x.com/0x15BA88FF" }
        ]
    },
    {
        avatar: "https://github.com/airrstorm.png",
        name: "Earl Asamoah",
        title: "Batman",
        links: [
            { icon: "github", link: "https://github.com/airrstorm" }
        ]
    },
    {
        avatar: "https://github.com/Jeffrey-Osei-Tawiah.png",
        name: "Jeffrey Osei Tawiah",
        title: "Core Contributor",
        links: [
            { icon: "github", link: "https://github.com/Jeffrey-Osei-Tawiah" }
        ]
    }
]
</script>

<VPTeamMembers size="small" :members="contributors" />
