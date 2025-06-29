<script lang="ts">
    let { children, className } = $props();
</script>

<div class={`relative ${className}`}>
    {@render children()}
</div>
