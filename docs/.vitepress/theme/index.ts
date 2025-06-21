import type { Theme } from "vitepress";
import DefaultTheme from "vitepress/theme";
import "./style.css";
import Feature from "./components/Feature.vue"
import FeaturesGrid from "./components/FeaturesGrid.vue"

export default {
    extends: DefaultTheme,
    enhanceApp({ app }) {
        app.component("Feature", Feature);
        app.component("FeaturesGrid", FeaturesGrid);
    }
} satisfies Theme
