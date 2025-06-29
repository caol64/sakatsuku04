<script lang="ts">
    let { children, className = '' } = $props();
</script>

<div class={`flex flex-row ${className}`}>
    {@render children()}
</div>
