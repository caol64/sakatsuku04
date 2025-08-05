<script lang="ts">
    import ModeSelect from '$lib/components/ModeSelect.svelte';
    import MainEditor from '$lib/components/MainEditor.svelte';
    import { getModeState } from '$lib/globalState.svelte';
    import BPlayerView from '$lib/components/BPlayerView.svelte';
</script>

{#if getModeState() === ""}
    <ModeSelect />
{:else if getModeState() === "bPlayerView"}
    <BPlayerView />
{:else}
    <MainEditor />
{/if}
