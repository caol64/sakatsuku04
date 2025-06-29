<script lang="ts">
    import { getSelectedTab } from "$lib/globalState.svelte";
    import VStack from "$lib/components/Stack/VStack.svelte";
    import Tabs from "./Tabs.svelte";
    import ClubEditor from "./BaseEditor.svelte";
    import MyTeamEditor from "./MyTeamEditor.svelte";
    import OtherTeamsEditor from "./OtherTeamsEditor.svelte";
    import ScoutsEditor from "./ScoutsEditor.svelte";
</script>

<VStack className="px-2 flex-1 h-screen">
    <Tabs />
    {#if getSelectedTab() === "Base"}
        <ClubEditor />
    {:else if getSelectedTab() === "My Team"}
        <MyTeamEditor />
    {:else if getSelectedTab() === "Other Teams"}
        <OtherTeamsEditor />
    {:else if getSelectedTab() === "Scouts"}
        <ScoutsEditor />
    {/if}
</VStack>
