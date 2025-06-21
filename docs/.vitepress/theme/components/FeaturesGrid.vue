<template>
    <div class="features-grid">
        <slot />
    </div>
</template>

<style scoped>
.features-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.5rem;
    margin: 2rem 0;
}
</style>
