<script lang="ts">
    import { getSelectedTab, getIsLoading } from "$lib/globalState.svelte";
    import VStack from "$lib/components/Stack/VStack.svelte";
    import Tabs from "./Tabs.svelte";
    import ClubEditor from "./ClubEditor.svelte";
    import PlayersView from "./PlayersView.svelte";
    import TeamsView from "./TeamsView.svelte";
    import SearchView from "./SearchView.svelte";
    import TownEditor from "./TownEditor.svelte";
    import ScoutsView from "./ScoutsView.svelte";
    import AlbumView from "./AlbumView.svelte";
</script>

<VStack className="px-2 flex-1 h-screen">
    <Tabs />
    {#if getSelectedTab() === "Game"}
        <ClubEditor />
    {:else if getSelectedTab() === "Players"}
        <PlayersView />
    {:else if getSelectedTab() === "Teams"}
        <TeamsView />
    {:else if getSelectedTab() === "Search"}
        <SearchView />
    {:else if getSelectedTab() === "Scouts"}
        <ScoutsView />
    {:else if getSelectedTab() === "Town"}
        <TownEditor />
    {:else if getSelectedTab() === "Album"}
        <AlbumView />
    {/if}
    {#if getIsLoading()}
        <div class="absolute inset-0 bg-black/50 flex items-center justify-center z-50">
            <svg class="animate-spin h-12 w-12 text-white" viewBox="0 0 24 24">
                <circle
                    class="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    stroke-width="4"
                    fill="none"
                />
                <path
                    class="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                />
            </svg>
        </div>
    {/if}
</VStack>
