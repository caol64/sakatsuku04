<script lang="ts">
    import type { Team, TeamsWithRegion, TeamPlayer } from "$lib/models";
    import HStack from "$lib/components/Stack/HStack.svelte";
    import VStack from "$lib/components/Stack/VStack.svelte";
    import { onMount } from "svelte";
    import teamsData from "$locales/teams_zh.json";
    import teamGroupsData from "$locales/team_groups_zh.json";
    import { getRefreshFlag, getSelectedTab, setRefreshFlag } from "$lib/globalState.svelte";
    import { getPlayerColorStr } from "$lib/utils";

    let treeData: TeamsWithRegion[] = $state([]);
    let openedRegion = $state("");
    let selectedTeam: Team = $state({
        index: 0,
        name: ""
    });
    let teamPlayers: TeamPlayer[] = $state([]);
    let teamFriendly = $state(0);

	function toggleRegion(region: string) {
		openedRegion = openedRegion === region ? "" : region;
	}

    async function selectTeam(team: Team) {
		selectedTeam = team;
        if (window.pywebview?.api?.fetch_team_player) {
            teamPlayers = await window.pywebview.api.fetch_team_player(selectedTeam.index);
            teamFriendly = await window.pywebview.api.fetch_team_friendly(selectedTeam.index);
        } else {
            alert('API 未加载');
        }
	}

    async function featchTeams() {
        treeData = [];
        let index = 0;
        for (let i = 0; i < teamGroupsData.length; i++) {
            const item = teamGroupsData[i];
            const regionName = item[0] as string;
            const max = i + 1 < teamGroupsData.length ? teamGroupsData[i + 1][1] as number : teamsData.length;
            const teams: Team[] = [];
            for (let i = index; i < max; i++) {
                teams.push({
                    index,
                    name: teamsData[index]
                });
                index++;
            }
            treeData.push({
                region: regionName,
                teams: teams
            });
        }
        openedRegion = treeData[0].region;
        selectedTeam = treeData[0].teams[0];
        await selectTeam(selectedTeam);
    }

	onMount(async () => {
        featchTeams();
	});

    $effect(() => {
        if(getRefreshFlag() && getSelectedTab() === "Teams") {
            try {
                featchTeams();
            } finally {
                setRefreshFlag(false);
            }
        }
    });

    async function save() {
        if (window.pywebview?.api?.save_team_friendly) {
            const { message } = await window.pywebview.api.save_team_friendly(selectedTeam.index, teamFriendly);
            if (message === "success") {
                alert("修改成功");
                await selectTeam(selectedTeam);
            } else {
                alert(message);
            }
        } else {
            alert('API 未加载');
        }
    }

</script>

<HStack className="flex-1 overflow-hidden m-2">
    <div class="w-1/4 overflow-y-auto">
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
                            <button onclick={() => selectTeam(team)} class={ selectedTeam.index === team.index ? "activate px-1.5 rounded-md cursor-pointer hover:bg-gray-100" : "px-1.5 rounded-md cursor-pointer hover:bg-gray-100" }>
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

    <VStack className="relative overflow-x-auto grow mx-2">
        <HStack className="items-center mb-1">
            <label for="gameDifficulty" class="w-16">友好度</label>
            <span class="text-sm w-16">{ teamFriendly }</span>
            <input id="gameDifficulty" type="range" min="0" max="255" bind:value={ teamFriendly } class="w-52 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700">
            <button onclick={save} class="w-18 h-8 rounded-md cursor-pointer mx-2 text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium text-sm text-center dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800">
                保存
            </button>
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
                        <th scope="row" class="px-6 py-4 font-medium text-gray-900 whitespace-nowrap dark:text-white" style={`background-image: linear-gradient(to right, transparent 66%, ${getPlayerColorStr(item.pos)} 100%)`}>
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
                            {item.cooperationType}
                        </td>
                        <td>
                            {item.toneType}
                        </td>
                        <td>
                            {item.growTypePhy}
                        </td>
                        <td>
                            {item.growTypeTec}
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
