<script lang="ts">
    import { getSelectedTab } from "$lib/globalState.svelte";
    import VStack from "$lib/components/Stack/VStack.svelte";
    import Tabs from "./Tabs.svelte";
    import ClubEditor from "./ClubEditor.svelte";
    import PlayersView from "./PlayersView.svelte";
    import TeamsView from "./TeamsView.svelte";
    import ScoutsView from "./ScoutsView.svelte";
</script>

<VStack className="px-2 flex-1 h-screen">
    <Tabs />
    {#if getSelectedTab() === "Club"}
        <ClubEditor />
    {:else if getSelectedTab() === "Players"}
        <PlayersView />
    {:else if getSelectedTab() === "Teams"}
        <TeamsView />
    {:else if getSelectedTab() === "Scouts"}
        <ScoutsView />
    {/if}
</VStack>
