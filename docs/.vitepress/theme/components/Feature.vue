<template>
    <component
        :is="link ? 'a' : 'div'"
        :href="link ? `/synapse${link}` : undefined"
        class="feature"
        rel="noopener"
    >
    <h3 class="feature-title">{{ title }}</h3>
    <p class="feature-details">{{ details }}</p>
    </component>
</template>

<script setup lang="ts">
    defineProps<{
        title: string
        details: string
        link?: string
    }>()
</script>

<style scoped>
.feature {
    display: block;
    border: 1px solid var(--vp-c-divider);
    border-radius: 8px;
    padding: 1.5rem;
    background-color: var(--vp-c-bg-soft);
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
    text-decoration: none;
    color: inherit;
}

.feature:hover {
    border-color: var(--vp-c-brand);
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.feature-title {
    font-size: 1.2rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
    color: var(--vp-c-text-1);
}

.feature-details {
    font-size: 0.95rem;
    color: var(--vp-c-text-2);
}
</style>
