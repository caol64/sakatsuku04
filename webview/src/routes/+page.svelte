<script lang="ts">
    import ModeSelect from '$lib/components/ModeSelect.svelte';
    import MainEditor from '$lib/components/MainEditor.svelte';
    import { getModeState } from '$lib/globalState.svelte';
</script>

{#if getModeState() === ""}
    <ModeSelect />
{:else}
    <MainEditor />
{/if}
