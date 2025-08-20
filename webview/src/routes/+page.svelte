<script lang="ts">
    import ModeSelect from '$lib/components/ModeSelect.svelte';
    import MainEditor from '$lib/components/MainEditor.svelte';
    import { getModeState } from '$lib/globalState.svelte';
    import BPlayerView from '$lib/components/BPlayerView.svelte';
    import BScoutView from '$lib/components/BScoutView.svelte';
    import BCoachView from '$lib/components/BCoachView.svelte';
</script>

{#if getModeState() === ""}
    <ModeSelect />
{:else if getModeState() === "bPlayerView"}
    <BPlayerView />
{:else if getModeState() === "bScoutView"}
    <BScoutView />
{:else if getModeState() === "bCoachView"}
    <BCoachView />
{:else}
    <MainEditor />
{/if}
