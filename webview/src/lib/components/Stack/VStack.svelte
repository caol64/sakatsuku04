<script lang="ts">
    let { children, className = '' } = $props();
</script>

<div class={`flex flex-col ${className}`}>
    {@render children()}
</div>
