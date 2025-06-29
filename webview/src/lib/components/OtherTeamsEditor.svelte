<script lang="ts">
    import type { Team, TeamsWithRegion, TeamPlayer } from "$lib/models";
    import HStack from "$lib/components/Stack/HStack.svelte";
    import VStack from "$lib/components/Stack/VStack.svelte";
    import { onMount } from "svelte";

    let treeData: TeamsWithRegion[] = $state([]);
    let openedRegion = $state("");
    let selectedTeam: Team = $state({
        index: 0,
        name: "",
        friendly: 0
    });
    let teamPlayers: TeamPlayer[] = $state([]);

	function toggleRegion(region: string) {
		openedRegion = openedRegion === region ? "" : region;
	}

    async function selectTeam(team: Team) {
		selectedTeam = team;
        if (window.pywebview?.api?.fetch_team_player) {
            teamPlayers = await window.pywebview.api.fetch_team_player(selectedTeam.index);
        } else {
            alert('pywebview API 未加载');
        }
	}

	onMount(async () => {
        if (window.pywebview?.api?.fetch_other_teams) {
            const pageData: TeamsWithRegion[] = await window.pywebview.api.fetch_other_teams();
            if (pageData) {
                treeData = pageData;
                openedRegion = treeData[0].region;
                selectedTeam = treeData[0].teams[0];
                await selectTeam(selectedTeam);
            }
        } else {
            alert('pywebview API 未加载');
        }
	});

</script>

<HStack className="flex-1 overflow-hidden">
    <div class="w-1/4 overflow-y-auto my-2">
        {#each treeData as item}
            <div class="py-0.5 flex items-center gap-x-0.5 w-full">
                <button onclick={() => toggleRegion(item.region)} class="size-6 flex justify-center items-center hover:bg-gray-100 rounded-md">
                    <svg class="size-4 text-gray-800 dark:text-neutral-200" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M5 12h14"></path>
                        {#if openedRegion !== item.region}
                            <path d="M12 5v14"></path>
                        {/if}
                    </svg>
                    <span class="sr-only">Icon</span>
                </button>

                <div class="px-1.5 rounded-md">
                    <span class="text-sm text-gray-800 dark:text-neutral-200">
                        {item.region}
                    </span>
                </div>
            </div>

            {#if openedRegion === item.region}
                <div class="">
                    {#each item.teams as team}
                        <div class="ps-7 relative before:absolute before:top-0 before:start-3 before:w-0.5 before:-ms-px before:h-full before:bg-gray-100 dark:before:bg-neutral-700">
                            <button onclick={() => selectTeam(team)} class={ selectedTeam.name === team.name ? "activate px-1.5 rounded-md cursor-pointer hover:bg-gray-100" : "px-1.5 rounded-md cursor-pointer hover:bg-gray-100" }>
                                <span class="text-sm text-gray-800 dark:text-neutral-200">
                                    {team.name}
                                </span>
                            </button>
                        </div>
                    {/each}
                </div>
            {/if}
        {/each}
    </div>

    <VStack className="relative overflow-x-auto grow my-2">
        <HStack className="my-2 items-center">
            <label for="gameDifficulty">友好度</label>
            <span class="text-sm">{ selectedTeam.friendly }</span>
            <input id="gameDifficulty" type="range" bind:value={ selectedTeam.friendly } class="h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700">
        </HStack>

        <table class="w-full text-sm text-left rtl:text-right text-gray-500 dark:text-gray-400">
            <thead class="text-xs text-gray-700 uppercase bg-gray-50 dark:bg-gray-700 dark:text-gray-400">
                <tr>
                    <th scope="col" class="w-48">
                        球员
                    </th>
                    <th scope="col">
                        年龄
                    </th>
                    <th scope="col">
                        号码
                    </th>
                    <th scope="col">
                        位置
                    </th>
                    <th scope="col">
                        等级
                    </th>
                    <th scope="col">
                        连携
                    </th>
                    <th scope="col">
                        口调
                    </th>
                    <th scope="col">
                        身体
                    </th>
                    <th scope="col">
                        技术
                    </th>
                    <th scope="col">
                        头脑
                    </th>
                </tr>
            </thead>
            <tbody>
                {#each teamPlayers as item}
                    <tr class="bg-white border-b dark:bg-gray-800 dark:border-gray-700 border-gray-200">
                        <th scope="row" class="px-6 py-4 font-medium text-gray-900 whitespace-nowrap dark:text-white">
                            {item.name}
                        </th>
                        <td>
                            {item.age}
                        </td>
                        <td>
                            {item.number}
                        </td>
                        <td>
                            {item.pos}
                        </td>
                        <td>
                            {item.rank}
                        </td>
                        <td>
                            {item.teamWork}
                        </td>
                        <td>
                            {item.toneType}
                        </td>
                        <td>
                            {item.growTypePhy}
                        </td>
                        <td>
                            {item.growTypeTech}
                        </td>
                        <td>
                            {item.growTypeSys}
                        </td>
                    </tr>
                {/each}
            </tbody>
        </table>
    </VStack>

</HStack>

<style lang="postcss">
    @reference "tailwindcss";
    .activate {
        @apply bg-gray-100  dark:bg-gray-600;
    }
    th {
        @apply px-1 py-1;
    }
    td {
        @apply px-1 py-1;
    }
</style>
